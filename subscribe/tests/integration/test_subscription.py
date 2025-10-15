# mypy: disable-error-code="no-untyped-def,no-any-return,attr-defined,return-value"
import json
import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from account.models import ShareSettings
from subscribe.infrastructure.models import Subscribe


@pytest.fixture
def user(db) -> None:
    return User.objects.create_user(username='testuser', password='pass')


@pytest.fixture
def other_user(db) -> None:
    return User.objects.create_user(username='otheruser', password='pass')


@pytest.fixture
def client_logged(client, user) -> None:
    client.login(username='testuser', password='pass')
    return client


#
# save (subscribe/unsubscribe)
#


@pytest.mark.django_db
def test_subscribe_success(client_logged, user, other_user) -> None:
    ShareSettings.objects.create(user=other_user, can_subscribe=True)

    url = reverse('save_subscribe')
    data = {'from_id': user.id, 'to_id': other_user.id, 'action': 'subscribe'}

    response = client_logged.post(url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert response.json()['status'] == 'subscribed'
    assert Subscribe.objects.filter(subscribe_from=user, subscribe_to=other_user).exists()


@pytest.mark.django_db
def test_subscribe_invalid_json(client_logged) -> None:
    url = reverse('save_subscribe')
    response = client_logged.post(url, data='{invalid json', content_type='application/json')
    assert response.status_code == 400
    assert response.json()['status'] == 'error'


@pytest.mark.django_db
def test_subscribe_forbidden_other_user(client_logged, other_user) -> None:
    ShareSettings.objects.create(user=other_user, can_subscribe=True)
    url = reverse('save_subscribe')
    data = {'from_id': other_user.id, 'to_id': other_user.id, 'action': 'subscribe'}

    response = client_logged.post(url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 403
    assert response.json()['status'] == 'forbidden'


@pytest.mark.django_db
def test_subscribe_user_not_exists(client_logged, user) -> None:
    url = reverse('save_subscribe')
    data = {'from_id': user.id, 'to_id': 9999, 'action': 'subscribe'}

    response = client_logged.post(url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 403
    assert response.json()['status'] == 'forbidden'


@pytest.mark.django_db
def test_subscribe_not_allowed(client_logged, user, other_user) -> None:
    ShareSettings.objects.create(user=other_user, can_subscribe=False)

    url = reverse('save_subscribe')
    data = {'from_id': user.id, 'to_id': other_user.id, 'action': 'subscribe'}

    response = client_logged.post(url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 403
    assert response.json()['status'] == 'forbidden'


@pytest.mark.django_db
def test_unsubscribe_success(client_logged, user, other_user) -> None:
    ShareSettings.objects.create(user=other_user, can_subscribe=True)
    Subscribe.objects.create(subscribe_from=user, subscribe_to=other_user)

    url = reverse('save_subscribe')
    data = {'from_id': user.id, 'to_id': other_user.id, 'action': 'unsubscribe'}

    response = client_logged.post(url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert response.json()['status'] == 'unsubscribed'
    assert not Subscribe.objects.filter(subscribe_from=user, subscribe_to=other_user).exists()


#
# delete_subscriber
#


@pytest.mark.django_db
def test_delete_subscriber_success(client_logged, user, other_user) -> None:
    ShareSettings.objects.create(user=user, can_subscribe=True)
    Subscribe.objects.create(subscribe_from=other_user, subscribe_to=user)

    url = reverse('delete_subscribe')
    data = {'user_id': other_user.id}

    response = client_logged.post(url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert response.json()['status'] == 'success'
    assert not Subscribe.objects.filter(subscribe_from=other_user, subscribe_to=user).exists()


@pytest.mark.django_db
def test_delete_subscriber_invalid_json(client_logged) -> None:
    url = reverse('delete_subscribe')
    response = client_logged.post(url, data='{invalid json', content_type='application/json')
    assert response.status_code == 400
    assert response.json()['status'] == 'error'


@pytest.mark.django_db
def test_delete_subscriber_user_not_exists(client_logged) -> None:
    url = reverse('delete_subscribe')
    data = {'user_id': 9999}
    response = client_logged.post(url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 403
    assert response.json()['status'] == 'forbidden'


@pytest.mark.django_db
def test_delete_subscriber_not_subscribed(client_logged, user, other_user) -> None:
    url = reverse('delete_subscribe')
    data = {'user_id': other_user.id}
    response = client_logged.post(url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 403
    assert response.json()['status'] == 'forbidden'


#
# permissions
#


@pytest.mark.django_db
def test_unauthenticated_cannot_access(client) -> None:
    url = reverse('save_subscribe')
    response = client.post(url, data='{}', content_type='application/json')
    assert response.status_code == 302  # redirect to login
