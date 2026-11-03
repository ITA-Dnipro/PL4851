import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from messaging.mongo import get_conversations_collection, get_messages_collection
from messaging.services import create_conversation, create_message
from projects.models import Project
from startups.models import LocationType, StartupProfile

pytestmark = pytest.mark.django_db

User = get_user_model()


@pytest.fixture(autouse=True)
def _clean_mongo_collections():
    get_conversations_collection().delete_many({})
    get_messages_collection().delete_many({})


@pytest.fixture
def verified_startup():
    owner = User.objects.create_user(
        email='verified-owner@example.com',
        password='Str0ng-pass!',
        first_name='V',
        last_name='O',
        role=User.Role.STARTUP,
    )
    return StartupProfile.objects.create(
        user=owner,
        startup_name='Verified Co',
        startup_description='desc',
        startup_phone='+380000000000',
        startup_email='verified@example.com',
        location=LocationType.KYIV_CITY,
        slug='verified-co',
        is_verified=True,
    )


@pytest.fixture
def unverified_startup():
    owner = User.objects.create_user(
        email='unverified-owner@example.com',
        password='Str0ng-pass!',
        first_name='U',
        last_name='O',
        role=User.Role.STARTUP,
    )
    return StartupProfile.objects.create(
        user=owner,
        startup_name='Unverified Co',
        startup_description='desc',
        startup_phone='+380000000000',
        startup_email='unverified@example.com',
        location=LocationType.KYIV_CITY,
        slug='unverified-co',
        is_verified=False,
    )


@pytest.fixture
def draft_project(verified_startup):
    return Project.objects.create(
        startup=verified_startup,
        project_title='Draft project',
        project_description='desc',
        investment_sum=1000,
        project_stage='MVP',
        status=Project.ProjectStatus.DRAFT,
    )


@pytest.fixture
def active_project(verified_startup):
    return Project.objects.create(
        startup=verified_startup,
        project_title='Active project',
        project_description='desc',
        investment_sum=1000,
        project_stage='MVP',
        status=Project.ProjectStatus.ACTIVE,
    )


@pytest.fixture
def user_a():
    return User.objects.create_user(
        email='alice@example.com',
        password='Str0ng-pass!',
        first_name='Alice',
        last_name='A',
        role=User.Role.STARTUP,
    )


@pytest.fixture
def user_b():
    return User.objects.create_user(
        email='bob@example.com',
        password='Str0ng-pass!',
        first_name='Bob',
        last_name='B',
        role=User.Role.STARTUP,
    )


@pytest.fixture
def user_c():
    return User.objects.create_user(
        email='carol@example.com',
        password='Str0ng-pass!',
        first_name='Carol',
        last_name='C',
        role=User.Role.STARTUP,
    )


def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def test_unauthenticated_request_is_rejected():
    client = APIClient()
    response = client.get(reverse('messaging:conversation-list'))
    assert response.status_code == 401


def test_create_conversation(user_a, user_b):
    client = auth_client(user_a)
    response = client.post(
        reverse('messaging:conversation-list'),
        {'participants': [user_a.pk, user_b.pk]},
        format='json',
    )

    assert response.status_code == 201
    conversation_id = response.json()['conversation_id']
    assert conversation_id

    from messaging.services import is_participant

    assert is_participant(conversation_id, user_a.pk)
    assert is_participant(conversation_id, user_b.pk)


def test_create_conversation_rejects_requester_not_in_participants(user_a, user_b):
    client = auth_client(user_a)
    response = client.post(
        reverse('messaging:conversation-list'),
        {'participants': [user_b.pk]},
        format='json',
    )

    assert response.status_code == 400


def test_create_conversation_rejects_unknown_user(user_a):
    client = auth_client(user_a)
    response = client.post(
        reverse('messaging:conversation-list'),
        {'participants': [user_a.pk, 999999]},
        format='json',
    )

    assert response.status_code == 400


def test_create_conversation_rejects_draft_project(user_a, user_b, draft_project):
    client = auth_client(user_a)
    response = client.post(
        reverse('messaging:conversation-list'),
        {'participants': [user_a.pk, user_b.pk], 'project_id': draft_project.pk},
        format='json',
    )

    assert response.status_code == 400


def test_create_conversation_accepts_active_project(user_a, user_b, active_project):
    client = auth_client(user_a)
    response = client.post(
        reverse('messaging:conversation-list'),
        {'participants': [user_a.pk, user_b.pk], 'project_id': active_project.pk},
        format='json',
    )

    assert response.status_code == 201


def test_create_conversation_rejects_unverified_startup(
    user_a, user_b, unverified_startup
):
    client = auth_client(user_a)
    response = client.post(
        reverse('messaging:conversation-list'),
        {'participants': [user_a.pk, user_b.pk], 'startup_id': unverified_startup.pk},
        format='json',
    )

    assert response.status_code == 400


def test_create_conversation_accepts_verified_startup(user_a, user_b, verified_startup):
    client = auth_client(user_a)
    response = client.post(
        reverse('messaging:conversation-list'),
        {'participants': [user_a.pk, user_b.pk], 'startup_id': verified_startup.pk},
        format='json',
    )

    assert response.status_code == 201


def test_list_conversations_includes_unread_count_and_last_message(user_a, user_b):
    conversation_id = create_conversation([user_a.pk, user_b.pk])
    create_message(conversation_id, user_a.pk, 'hello')

    client = auth_client(user_b)
    response = client.get(reverse('messaging:conversation-list'))

    assert response.status_code == 200
    data = response.json()
    assert data['total_count'] == 1
    conv = data['results'][0]
    assert conv['conversation_id'] == conversation_id
    assert conv['unread_count'] == 1
    assert conv['last_message']['body'] == 'hello'


def test_send_message_via_rest_persists_to_mongo(user_a, user_b):
    conversation_id = create_conversation([user_a.pk, user_b.pk])
    client = auth_client(user_a)

    response = client.post(
        reverse('messaging:message-list', kwargs={'conversation_id': conversation_id}),
        {'body': 'hello from REST'},
        format='json',
    )

    assert response.status_code == 201
    assert response.json()['body'] == 'hello from REST'

    stored = get_messages_collection().find_one(
        {'conversation_id': conversation_id, 'body': 'hello from REST'}
    )
    assert stored is not None
    assert stored['sender_id'] == user_a.pk


def test_send_message_non_participant_gets_403(user_a, user_b, user_c):
    conversation_id = create_conversation([user_a.pk, user_b.pk])
    client = auth_client(user_c)

    response = client.post(
        reverse('messaging:message-list', kwargs={'conversation_id': conversation_id}),
        {'body': 'hello'},
        format='json',
    )

    assert response.status_code == 403


def test_list_messages_non_participant_gets_403(user_a, user_b, user_c):
    conversation_id = create_conversation([user_a.pk, user_b.pk])
    client = auth_client(user_c)

    response = client.get(
        reverse('messaging:message-list', kwargs={'conversation_id': conversation_id})
    )

    assert response.status_code == 403


def test_unknown_conversation_gets_404(user_a):
    client = auth_client(user_a)
    response = client.get(
        reverse('messaging:message-list', kwargs={'conversation_id': 'does-not-exist'})
    )

    assert response.status_code == 404


def test_mark_read_resets_unread_count(user_a, user_b):
    conversation_id = create_conversation([user_a.pk, user_b.pk])
    create_message(conversation_id, user_a.pk, 'hello')

    client = auth_client(user_b)
    response = client.post(
        reverse(
            'messaging:conversation-read', kwargs={'conversation_id': conversation_id}
        )
    )
    assert response.status_code == 204

    list_response = client.get(reverse('messaging:conversation-list'))
    assert list_response.json()['results'][0]['unread_count'] == 0


def test_mark_read_non_participant_gets_403(user_a, user_b, user_c):
    conversation_id = create_conversation([user_a.pk, user_b.pk])
    client = auth_client(user_c)

    response = client.post(
        reverse(
            'messaging:conversation-read', kwargs={'conversation_id': conversation_id}
        )
    )

    assert response.status_code == 403
