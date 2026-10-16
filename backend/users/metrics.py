from django.db.models import F

from .models import PasswordResetMetrics

METRIC_NAMES = {
    'requests',
    'confirms',
    'expired_attempts',
    'reused_attempts',
}


def increment_metric(metric_name):
    if metric_name not in METRIC_NAMES:
        raise ValueError(f'Invalid metric name: {metric_name}')

    metrics, _ = PasswordResetMetrics.objects.get_or_create(pk=1)

    PasswordResetMetrics.objects.filter(pk=metrics.pk).update(
        **{metric_name: F(metric_name) + 1}
    )
