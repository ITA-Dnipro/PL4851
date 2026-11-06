from django.test import TestCase
from rest_framework.test import APIClient

from dashboard.models import SavedProject
from investors.models import InvestorProfile
from projects.models import Project
from startups.models import StartupProfile
from users.models import User


def make_user(email, role):
    return User.objects.create_user(
        email=email,
        password='pass12345',
        first_name='new',
        last_name='user',
        role=role,
    )


class SavedItemsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = make_user('inv@test.com', User.Role.INVESTOR)
        cls.other = make_user('other@test.com', User.Role.INVESTOR)
        investor = InvestorProfile.objects.create(
            user=cls.user, investor_name='Inv', investor_type='private'
        )
        startup = StartupProfile.objects.create(
            user=make_user('st@test.com', User.Role.STARTUP),
            startup_name='S',
            startup_description='d',
            startup_phone='380000000000',
            startup_email='st@test.com',
        )
        project = Project.objects.create(
            startup=startup,
            project_title='P',
            project_description='d',
            investment_sum=100,
            project_stage='seed',
        )
        SavedProject.objects.create(investor=investor, project=project)
        cls.url = f'/api/users/{cls.user.pk}/saved/'

    def setUp(self):
        self.client = APIClient()

    def test_list(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def test_unsupported_type_returns_400(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url, {'type': 'company'})
        self.assertEqual(response.status_code, 400)

    def test_unauthenticated_returns_401(self):
        self.assertEqual(self.client.get(self.url).status_code, 401)
