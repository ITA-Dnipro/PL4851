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
        cls.investor = InvestorProfile.objects.create(
            user=cls.user, investor_name='Inv', investor_type='private'
        )
        startup = StartupProfile.objects.create(
            user=make_user('st@test.com', User.Role.STARTUP),
            startup_name='S',
            startup_description='d',
            startup_phone='380000000000',
            startup_email='st@test.com',
        )
        cls.project = Project.objects.create(
            startup=startup,
            project_title='P',
            project_description='d',
            investment_sum=100,
            project_stage='seed',
            status=Project.ProjectStatus.ACTIVE,
        )
        cls.new_project = Project.objects.create(
            startup=startup,
            project_title='P2',
            project_description='d',
            investment_sum=100,
            project_stage='seed',
            status=Project.ProjectStatus.ACTIVE,
        )
        cls.draft_project = Project.objects.create(
            startup=startup,
            project_title='Draft',
            project_description='d',
            investment_sum=100,
            project_stage='seed',
        )
        SavedProject.objects.create(investor=cls.investor, project=cls.project)
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

    def _post(self, target_id, target_type='project'):
        return self.client.post(
            self.url,
            {'target_type': target_type, 'target_id': target_id},
            format='json',
        )

    def test_save_creates(self):
        self.client.force_authenticate(self.user)
        response = self._post(self.new_project.pk)
        self.assertEqual(response.status_code, 201)
        self.assertIn('saved_id', response.data)
        self.assertIn('saved_at', response.data)

    def test_save_duplicate_is_idempotent(self):
        self.client.force_authenticate(self.user)
        first = self._post(self.new_project.pk)
        second = self._post(self.new_project.pk)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.data['saved_id'], second.data['saved_id'])
        self.assertEqual(SavedProject.objects.count(), 2)

    def test_save_unknown_project_returns_404(self):
        self.client.force_authenticate(self.user)
        self.assertEqual(self._post(99999).status_code, 404)

    def test_save_unsupported_type_returns_400(self):
        self.client.force_authenticate(self.user)
        self.assertEqual(self._post(1, 'company').status_code, 400)

    def test_save_unauthenticated_returns_401(self):
        self.assertEqual(self._post(self.new_project.pk).status_code, 401)

    def test_save_other_user_returns_403(self):
        self.client.force_authenticate(self.other)
        self.assertEqual(self._post(self.new_project.pk).status_code, 403)

    def test_save_draft_returns_404(self):
        self.client.force_authenticate(self.user)
        self.assertEqual(self._post(self.draft_project.pk).status_code, 404)
        self.assertEqual(SavedProject.objects.count(), 1)

    def test_delete(self):
        self.client.force_authenticate(self.user)
        saved = SavedProject.objects.get(investor=self.investor)
        response = self.client.delete(f'{self.url}{saved.pk}/')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(SavedProject.objects.filter(pk=saved.pk).exists())

    def test_delete_unknown_returns_404(self):
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.delete(f'{self.url}99999/').status_code, 404)

    def test_delete_unauthenticated_returns_401(self):
        self.assertEqual(self.client.delete(f'{self.url}1/').status_code, 401)
