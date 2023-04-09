import pytest
from django.urls import reverse

from travel.models import VisitedCity

url = reverse('region-selected', kwargs={'pk': 1})
login_url = reverse('signin')


@pytest.mark.django_db
def test_access_not_auth_user(client):
    """
    Неавторизованный пользователь должен перенаправляться на страницу авторизации.
    """
    # Проверяем факт перенаправления
    response = client.get(url)
    assert response.status_code == 302
    assert response['Location'] == login_url[:-1] + f'?next={url}'

    # Проверяем конечную точку перенаправления
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert 'account/signin.html' in (t.name for t in response.templates)


@pytest.mark.django_db
def test_access_auth_user(create_user, setup_db, client):
    """
    У авторизованного пользователя должна открываться запрошенная страница.
    """
    client.login(username='username', password='password')
    response = client.get(url, kwargs={'pk': 1})
    assert response.status_code == 200
    assert 'region/cities_by_region__list.html' in (t.name for t in response.templates)


@pytest.mark.django_db
def test_content_1st_page(create_user, setup_db, setup_visited_cities_20_cities_in_1_region, client):
    """
    В случае, если посещённых городов в этом регионе больше, чем 16 (лимит пагинации),
    то они разделяются на несколько страниц.
    На первой странице отображаюстя первые 16 городов.
    """
    client.login(username='username', password='password')
    response = client.get(url)

    assert 'Регион 1' in response.content.decode()

    # На странице должно отображаться 16 городов с 1 по 16
    for number in range(1, 17):
        assert f'Город {number}' in response.content.decode()
    assert 'Регион 17' not in response.content.decode()
    assert 'Страница 1 из 2' in response.content.decode()


@pytest.mark.django_db
def test_content_2nd_page(create_user, setup_db, setup_visited_cities_20_cities_in_1_region, client):
    """
    В случае, если посещённых городов в этом регионе больше, чем 16 (лимит пагинации),
    то они разделяются на несколько страниц.
    На второй странице отображаюстя последние 4 города.
    """
    client.login(username='username', password='password')
    response = client.get(f'{url}?page=2')

    assert 'Регион 1' in response.content.decode()

    # На странице должно отображаться 4 города с 17 по 20
    for number in range(17, 21):
        assert f'Город {number}' in response.content.decode()
    assert 'Регион 3' not in response.content.decode()
    assert 'Страница 2 из 2' in response.content.decode()
