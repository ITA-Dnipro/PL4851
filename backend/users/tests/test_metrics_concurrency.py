from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from django.contrib.auth import get_user_model
from django.db import close_old_connections, connection
from django.test import TransactionTestCase

from ..metrics import increment_metric
from ..models import PasswordResetMetrics, PasswordResetToken
from ..services.password_reset import (
    consume_password_reset_token,
    create_password_reset_token,
    hash_token,
)


class PasswordResetMetricsConcurrencyTest(TransactionTestCase):
    def setUp(self):
        if connection.vendor != 'postgresql':
            self.skipTest('Concurrency tests require PostgreSQL')

        PasswordResetMetrics.objects.create(pk=1)

    def run_concurrently(self, metric_names):
        barrier = Barrier(len(metric_names))

        def worker(metric_name):
            close_old_connections()
            try:
                barrier.wait(timeout=10)
                increment_metric(metric_name)
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=len(metric_names)) as executor:
            list(executor.map(worker, metric_names))

    def test_simultaneous_updates_to_same_metric(self):
        self.run_concurrently(['requests', 'requests'])

        metrics = PasswordResetMetrics.objects.get(pk=1)

        self.assertEqual(metrics.requests, 2)
        self.assertEqual(PasswordResetMetrics.objects.count(), 1)

    def test_simultaneous_updates_to_different_metrics(self):
        self.run_concurrently(
            [
                'expired_attempts',
                'reused_attempts',
            ]
        )

        metrics = PasswordResetMetrics.objects.get(pk=1)

        self.assertEqual(metrics.expired_attempts, 1)
        self.assertEqual(metrics.reused_attempts, 1)
        self.assertEqual(PasswordResetMetrics.objects.count(), 1)

    def test_simultaneous_consumption_of_same_token(self):
        User = get_user_model()

        user = User.objects.create_user(
            email='concurrent_reset@example.com',
            first_name='Concurrent',
            last_name='Test',
            role='startup',
            password='securepassword123',
        )

        raw_token = create_password_reset_token(user)
        barrier = Barrier(2)

        def worker(_):
            close_old_connections()
            try:
                barrier.wait(timeout=10)
                result = consume_password_reset_token(raw_token)
                return result is not None
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(worker, range(2)))

        self.assertEqual(results.count(True), 1)
        self.assertEqual(results.count(False), 1)

        token = PasswordResetToken.objects.get(
            token_hash=hash_token(raw_token),
        )
        self.assertIsNotNone(token.used_at)

        metrics = PasswordResetMetrics.objects.get(pk=1)
        self.assertEqual(metrics.confirms, 1)
        self.assertEqual(metrics.reused_attempts, 1)
