import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from city.models import VisitedCity


@pytest.mark.django_db
def test__guest_by_get(setup, client):
    response = client.get(reverse('city-delete', kwargs={'pk': 1}))
    assert response.status_code == 302

    response = client.get(reverse('city-delete', kwargs={'pk': 1}), follow=True)
    assert response.status_code == 200
    assert 'account/signin.html' in (t.name for t in response.templates)


@pytest.mark.django_db
def test__guest_by_post(setup, client):
    response = client.post(reverse('city-delete', kwargs={'pk': 1}))
    assert response.status_code == 302

    response = client.post(reverse('city-delete', kwargs={'pk': 1}), follow=True)
    assert response.status_code == 200
    assert 'account/signin.html' in (t.name for t in response.templates)


@pytest.mark.django_db
def test__auth_user_by_get(setup, caplog, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('city-delete', kwargs={'pk': 1}))

    assert caplog.records[0].levelname == 'WARNING'
    assert '(Visited city) Attempt to access the GET method' in caplog.records[0].getMessage()
    assert response.status_code == 403


@pytest.mark.django_db
def test__auth_user_by_post(setup, caplog, client):
    client.login(username='username1', password='password')
    user = User.objects.get(username='username1')
    qty_before = VisitedCity.objects.filter(user=user).count()
    response = client.post(reverse('city-delete', kwargs={'pk': 1}), follow=True)
    qty_after = VisitedCity.objects.filter(user=user).count()

    assert caplog.records[0].levelname == 'INFO'
    assert '(Visited city) Deleting the visited city #1' in caplog.records[0].getMessage()
    assert qty_before - qty_after == 1
    assert response.status_code == 200
    assert 'city/city_all__list.html' in (t.name for t in response.templates)


@pytest.mark.django_db
def test__auth_user_not_owner_by_get(setup, client):
    client.login(username='username2', password='password')
    response = client.get(reverse('city-delete', kwargs={'pk': 1}))
    assert response.status_code == 403


@pytest.mark.django_db
def test__auth_user_not_owner_by_post(setup, caplog, client):
    client.login(username='username2', password='password')
    response = client.post(reverse('city-delete', kwargs={'pk': 1}))

    assert caplog.records[0].levelname == 'WARNING'
    assert (
        '(Visited city) Attempt to delete a non-existent visited city #1'
        in caplog.records[0].getMessage()
    )
    assert response.status_code == 404
