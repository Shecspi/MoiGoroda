import pytest
from bs4 import BeautifulSoup
from django.urls import reverse

from city.models import VisitedCity

url = reverse('region-selected', kwargs={'pk': 1})
symbols = 'АБВГДЕЖЗИЙКЛМНОПРСТУ'


@pytest.mark.django_db
def test_access_not_auth_user(setup_db, client):
    """
    Тестирование того, что у неавторизованного пользователя есть доступ на страницу и отображается корректный шаблон.
    """
    response = client.get(url)

    assert response.status_code == 200
    assert 'region/cities_by_region__list.html' in (t.name for t in response.templates)


@pytest.mark.django_db
def test_access_auth_user(create_user, setup_db, client):
    """
    У авторизованного пользователя должна открываться запрошенная страница.
    """
    client.login(username='username', password='password')
    response = client.get(url)
    assert response.status_code == 200
    assert 'region/cities_by_region__list.html' in (t.name for t in response.templates)


@pytest.mark.django_db
def test_content_1st_page(create_user, setup_db, setup_20_visited_cities_in_1_region, client):
    """
    Тестирование ситуации, когда у авторизованного пользователя
    посещено городов больше, чем отображается на странице.
    В таком случае на первой странице должны выполняться следующие условия:
        * имеется заголовок страницы с названием региона
        * отображается 16 карточек с посещёнными городами региона и на каждой есть информация о названии города,
          дате посещения, численности населения, дате основания, рейтинг и наличие магнита.
        * имеется пагинация из 2 страниц

    `setup_db` создаёт 20 регионов и 20 городов в них.
    """
    client.login(username='username', password='password')
    response = client.get(url)
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    # На странице должен быть заголовок с названием региона
    assert ('Регион А область' in source.find('h1').text)

    # На странице должно отображаться 16 городов с А по П
    all_cities = source.find_all('div', {'class': 'h4'})
    assert len(all_cities) == 16
    for index in range(0, 16):
        assert f'Город {symbols[index]}' in all_cities[index].text

    # Проверка наличия пагинации с правильным номером страницы
    assert 'Страница 1 из 2' in response.content.decode()


@pytest.mark.django_db
def test_content_2nd_page(create_user, setup_db, setup_20_visited_cities_in_1_region, client):
    """
    Тестирование ситуации, когда у авторизованного пользователя
    посещено городов больше, чем отображается на странице.
    В таком случае на второй странице должны выполняться следующие условия:
        * имеется заголовок страницы с названием региона
        * отображается 2 карточки посещённых городов с информацией о названии города,
          дате посещения, численности населения, дате основания, рейтинг и наличие магнита.
        * отображается 2 карточки непосещённых городов с информацией о названии города,
          численности населения, дате основания.
        * имеется пагинация из 2 страниц

    `setup_db` создаёт 20 регионов и 20 городов в них.
    """
    client.login(username='username', password='password')
    response = client.get(f'{url}?page=2')
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    # На странице должен быть заголовок с названием региона
    assert ('Регион А область' in source.find('h1').text)

    # На странице должно отображаться 4 города с Р по У
    all_cities = source.find_all('div', {'class': 'h4'})
    assert len(all_cities) == 4
    for index in range(0, 4):
        assert f'Город {symbols[index + 16]}' in all_cities[index].text

    # Проверка карточек с посещёнными городами
    assert len(source.find_all('div', {'class': 'card-visited-city'})) == 2
    for block in source.find_all('div', {'class': 'card-visited-city'}):
        assert 'Дата посещения не указана' in block.text
        assert 'Население' in block.text
        assert 'Год основания не известен' in block.text
        assert(len(block.find_all('i', {'class': 'fa-star'}))) == 5
        assert 'Магнит' in block.text

    # Проверка карточек с непосещёнными городами
    assert len(source.find_all('div', {'class': 'card-notvisited-city'})) == 2
    for block in source.find_all('div', {'class': 'card-notvisited-city'}):
        assert 'Дата посещения не указана' not in block.text
        assert 'Население' in block.text
        assert 'Год основания не известен' in block.text
        assert (len(block.find_all('i', {'class': 'fa-star'}))) == 0
        assert 'Магнит' not in block.text

    # Проверка наличия пагинации с правильным номером страницы
    assert 'Страница 2 из 2' in response.content.decode()
