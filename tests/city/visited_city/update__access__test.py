import pytest
from django.urls import reverse


@pytest.mark.django_db
def test__guest_by_get(setup, client):
    """
    Доступ через GET неавторизованным пользователям запрещён. Перенаправление на форму авторизации.
    """
    response = client.get(reverse('city-update', kwargs={'pk': 1}))
    assert response.status_code == 302

    response = client.get(reverse('city-update', kwargs={'pk': 1}), follow=True)
    assert response.status_code == 200
    assert 'account/signin.html' in (t.name for t in response.templates)


@pytest.mark.django_db
def test__guest_by_post(setup, client):
    """
    Доступ через POST неавторизованным пользователям запрещён. Перенаправление на форму авторизации.
    """
    response = client.post(reverse('city-update', kwargs={'pk': 1}))
    assert response.status_code == 302

    response = client.post(reverse('city-update', kwargs={'pk': 1}), follow=True)
    assert response.status_code == 200
    assert 'account/signin.html' in (t.name for t in response.templates)


@pytest.mark.django_db
def test__auth_user_by_get(setup, caplog, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('city-update', kwargs={'pk': 1}))
    assert response.status_code == 200


@pytest.mark.django_db
def test__auth_user_by_get_to_incorrect_city(setup, caplog, client):
    client.login(username='username1', password='password')
    response = client.get(reverse('city-update', kwargs={'pk': 2}))
    assert caplog.records[0].levelname == 'WARNING'
    assert (
        '(Visited city) Attempt to update a non-existent visited city #2'
        in caplog.records[0].getMessage()
    )
    assert response.status_code == 404
