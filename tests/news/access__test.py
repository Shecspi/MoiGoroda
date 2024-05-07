"""

Copyright 2024 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

"""

import pytest

from django.urls import reverse


url = reverse('news-list')
login_url = reverse('signin')


@pytest.mark.django_db
def test__access__guest(setup, client):
    response = client.get(url)

    assert response.status_code == 200
    assert 'news/news__list.html' in (t.name for t in response.templates)


@pytest.mark.django_db
def test__access__auth_user(setup, client):
    client.login(username='username1', password='password')
    response = client.get(url)

    assert response.status_code == 200
    assert 'news/news__list.html' in (t.name for t in response.templates)
