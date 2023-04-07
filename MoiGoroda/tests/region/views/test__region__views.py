import pytest
from django.urls import reverse


url = reverse('region-all')
login_url = reverse('signin')
# ToDo Добавить проверку количества отображаемых регионов через len(response.context['all_regions'])
# ToDo Добавить проверку пагинации


@pytest.fixture
def create_user(client, django_user_model):
    new_user = django_user_model.objects.create_user(
        username='username', password='password'
    )
    return new_user


@pytest.mark.django_db
def test_access_not_auth_user(client):
    """
    Неавторизованный пользователь должен перенаправляться на страницу авторизации.
    """
    response = client.get(url)
    assert response.status_code == 302
    assert response['Location'] == login_url[:-1] + f'?next={url}'


@pytest.mark.django_db
def test_access_auth_user(create_user, client):
    """
    У авторизованного пользователя должна открываться запрошенная страница.
    """
    client.login(username='username', password='password')
    response = client.get(url)
    assert response.status_code == 200
    assert 'travel/region/list.html' in (t.name for t in response.templates)


def test_content_zero_regions(create_user, client):
    """
    При отсутствии посещённых городов должна отобразиться соответствующая надпись.
    """
    client.login(username='username', password='password')
    response = client.get(url)
    assert 'Регионы России' in response.content.decode()
    assert 'На данный момент Вы не посетили ни одного региона России' in response.content.decode()


@pytest.mark.django_db
def test_content_1_page(create_user, setup_db, setup_visited_cities_10_cities, client):
    client.login(username='username', password='password')
    response = client.get(url)

    assert 'Регионы России' in response.content.decode()

    # На странице должно отображаться 16 регионов с 1 по 16 (даже если они небыли посещены)
    assert 'Регион 1' in response.content.decode()
    assert 'Регион 16' in response.content.decode()
    assert 'Регион 17' not in response.content.decode()

    assert response.content.decode().count('1 из 1') == 10
    assert response.content.decode().count('0 из 1') == 6


@pytest.mark.django_db
def test_content_2_page(create_user, setup_db, setup_visited_cities_10_cities, client):
    client.login(username='username', password='password')
    response = client.get(f'{url}?page=2')

    # На странице должно отображаться 4 региона с 17 по 20 (даже если они небыли посещены)
    assert 'Регион 3' not in response.content.decode()
    assert 'Регион 17' in response.content.decode()
    assert 'Регион 20' in response.content.decode()

    assert response.content.decode().count('0 из 1') == 4
