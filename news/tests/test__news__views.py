import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MoiGoroda.settings')

import django
django.setup()

from django.urls import reverse
import pytest


url = reverse('news-list')
login_url = reverse('signin')


@pytest.mark.django_db
def test__access_not_auth_user(client):
    """
    У неавторизованного пользователя должна открываться запрошенная страница.
    """
    response = client.get(url)
    assert response.status_code == 200
    assert 'news/news__list.html' in (t.name for t in response.templates)


@pytest.mark.django_db
def test__access_auth_user(create_user, client):
    """
    У авторизованного пользователя должна открываться запрошенная страница.
    """
    client.login(username='username', password='password')
    response = client.get(url)
    assert response.status_code == 200
    assert 'news/news__list.html' in (t.name for t in response.templates)
