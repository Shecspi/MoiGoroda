import pytest

from bs4 import BeautifulSoup
from django.urls import reverse


url = reverse('region-all')
create_url = reverse('city-create')
login_url = reverse('signin')
symbols = 'АБВГДЕЖЗИЙКЛМНОПРСТУ'


@pytest.mark.django_db
def test_access_not_auth_user(client):
    """
    Тестирование того, что у неавторизованного пользователя есть доступ на страницу и отображается корректный шаблон.
    """
    response = client.get(url)

    assert response.status_code == 200
    assert 'region/region__list.html' in (t.name for t in response.templates)


@pytest.mark.django_db
def test_access_auth_user(create_user, client):
    """
    Тестирование того, что у авторизованного пользователя есть доступ на страницу и отображается корректный шаблон.
    """
    client.login(username='username', password='password')
    response = client.get(url)

    assert response.status_code == 200
    assert 'region/region__list.html' in (t.name for t in response.templates)


@pytest.mark.django_db
def test_html_has_tabs_auth_user(create_user, client):
    """
    Тестирование того, что у авторизованного пользователя отображается меню с вкладками "Список" и "Карта".
        * вкладка "Список" должна быть активна по-умолчанию
        " на обоех вкладках должны присутствовать иконки
        * на обоех вкладках должен быть текст "Список" и "Карта" соответственно.
    """
    client.login(username='username', password='password')
    response = client.get(url)
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    assert (
        source.find('div', {'class': 'nav flex-column nav-pills'}).find('button', {'class': 'nav-link active'})
        .find('i', {'class': 'fa-solid fa-list'}) is not None
    )
    assert (
        'Список' in
        source.find('div', {'class': 'nav flex-column nav-pills'}).find('button', {'class': 'nav-link active'}).text
    )
    assert (
        source.find('div', {'class': 'nav flex-column nav-pills'}).find('button', {'id': 'map-tab'})
        .find('i', {'class': 'fa-solid fa-map-location-dot'}) is not None
    )
    assert (
        'Карта' in
        source.find('div', {'class': 'nav flex-column nav-pills'}).find('button', {'id': 'map-tab'}).text
    )


@pytest.mark.django_db
def test_html_has_tabs_not_auth_user(create_user, client):
    """
    Тестирование того, что у неавторизованного пользователя отображается меню с вкладками "Список" и "Карта".
        * вкладка "Список" должна быть активна по-умолчанию
        " на обоех вкладках должны присутствовать иконки
        * на обоех вкладках должен быть текст "Список" и "Карта" соответственно.
    """
    response = client.get(url)
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    assert (
        source.find('div', {'class': 'nav flex-column nav-pills'}).find('button', {'class': 'nav-link active'})
        .find('i', {'class': 'fa-solid fa-list'}) is not None
    )
    assert (
        'Список' in
        source.find('div', {'class': 'nav flex-column nav-pills'}).find('button', {'class': 'nav-link active'}).text
    )
    assert (
        source.find('div', {'class': 'nav flex-column nav-pills'}).find('button', {'id': 'map-tab'})
        .find('i', {'class': 'fa-solid fa-map-location-dot'}) is not None
    )
    assert (
        'Карта' in
        source.find('div', {'class': 'nav flex-column nav-pills'}).find('button', {'id': 'map-tab'}).text
    )


@pytest.mark.django_db
def test_html_has_button_add_city_auth_user(create_user, client):
    """
    Тестирование того, что у авторизованного пользователя отображается кнопка "Добавить город".
    На кнопке должны присутстввовать:
        * иконка
        * надпись "Добавить город"
    """
    client.login(username='username', password='password')
    response = client.get(url)
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    assert source.find('a', {'class': 'btn', 'href': create_url}).find('i', {'class', 'fa-solid fa-city'}) is not None
    assert 'Добавить город' in source.find('a', {'class': 'btn', 'href': create_url}).text


@pytest.mark.django_db
def test_html_has_button_add_city_not_auth_user(create_user, client):
    """
    Тестирование того, что у неавторизованного пользователя не отображается кнопка "Добавить город".
    """
    response = client.get(url)
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    assert source.find('a', {'href': create_url}) is None


@pytest.mark.django_db
def test_html_has_search_auth_user(create_user, client):
    """
    Тестирование того, что у авторизованного пользователя отображается форма поиска.
    На ней должны присутствовать:
        * поле ввода текста с подсказкой
        * кнопка с иконкой поиска
        * кнопка с надписью "Найти"
    """
    client.login(username='username', password='password')
    response = client.get(url)
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    assert (
            source.find('form', {'action': url}).find('input', {'type': 'text'}).get('placeholder')
            == 'Введите текст для поиска'
    )
    assert (
            source.find('form', {'action': url}).find('button', {'type': 'submit'})
            .find('i', {'class': 'fa-solid fa-magnifying-glass'})
            is not None
    )
    assert 'Найти' in source.find('form', {'action': url}).find('button', {'type': 'submit'}).text


@pytest.mark.django_db
def test_html_has_search_not_auth_user(create_user, client):
    """
    Тестирование того, что у неавторизованного пользователя отображается форма поиска.
    На ней должны присутствовать:
        * поле ввода текста с подсказкой
        * кнопка с иконкой поиска
        * кнопка с надписью "Найти"
    """
    response = client.get(url)
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    assert (
            source.find('form', {'action': url}).find('input', {'type': 'text'}).get('placeholder')
            == 'Введите текст для поиска'
    )
    assert (
            source.find('form', {'action': url}).find('button', {'type': 'submit'})
            .find('i', {'class': 'fa-solid fa-magnifying-glass'})
            is not None
    )
    assert 'Найти' in source.find('form', {'action': url}).find('button', {'type': 'submit'}).text


@pytest.mark.django_db
def test_content_zero_visited_regions(setup_1_city_in_1_region, create_user, client):
    """
    Тестирование ситуации, когда у авторизованного пользователя нет посещённых регионов.
    В таком случае должны отображаться карточки с регионами, на которых:
        * имеется заголовок страницы
        * имеется 16 карточек с регионами
        * на каждой из 16 карточек есть информация о 0 посещённых городов и общем их количестве в регионе (0 из 1)
        * на каждой из 16 карточек есть информация о названии региона
        * на каждой из 16 карточек есть информация о федеральном округе
        * на всех карточках нет прогресс-бара посещённых городов
        * имеется пагинация из 2 страниц

    `setup_1_city_in_1_region` создаёт 20 регионов и 20 городов (по 1 в каждом).
    """
    client.login(username='username', password='password')
    response = client.get(url)
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    assert 'Регионы России' in response.content.decode()
    assert len(source.find_all('div', {'class': 'card-region'})) == 16
    for block in source.find_all('div', {'class': 'card-region'}):
        assert 'Area 1' in block.text
        assert '0 из 1' in block.text
        assert block.find('div', {'class': 'pregoress-bar'}) is None
    assert 'Страница 1 из 2' in response.content.decode()


@pytest.mark.django_db
def test_content_1st_page(create_user, setup_1_city_in_1_region,
                          setup_18_visited_cities_in_18_regions, client):
    """
    Тестирование ситуации, когда у авторизованного пользователя
    посещено городов больше, чем отображается на странице.
    В таком случае на первой странице должны отображаться карточки с регионами:
        * имеется заголовок страницы
        * имеется 16 карточек регионов с посещёнными городами, на каждой из которых имеется
          название региона, федеральный округ, прогресс бар, количество посещённых городов (1 из 1).
        * имеется пагинация из 2 страниц

    `setup_1_city_in_1_region` создаёт 20 регионов и 20 городов (по 1 в каждом).
    `setup_18_visited_cities_in_18_regions` создаёт 18 посещённых городов в 18 регионах (по 1 в каждом).
    """
    client.login(username='username', password='password')
    response = client.get(url)
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    assert 'Регионы России' in response.content.decode()
    all_regions = source.find_all('div', {'class': 'card-region'})
    assert len(all_regions) == 16
    for index in range(0, 16):
        assert f'Регион {symbols[index]}' in all_regions[index].text
        assert 'Area 1' in all_regions[index].text
    assert response.content.decode().count('1 из 1') == 16
    assert len(source.find_all('div', {'class': 'progress-bar'})) == 16


@pytest.mark.django_db
def test_content_2nd_page(create_user, setup_1_city_in_1_region,
                          setup_18_visited_cities_in_18_regions, client):
    """
    Тестирование ситуации, когда у авторизованного пользователя
    посещено городов больше, чем отображается на странице.
    В таком случае на второй странице должны отображаться карточки с регионами:
        * имеется заголовок страницы
        * отображается 4 карточки с регионами
        * на каждой карточке есть информация о названии региона
        * на каждой карточке есть информация о федеральном округе
        * имеется 2 карточки регионов с посещёнными городами, на каждой из которых имеется
          название региона, федеральный округ, прогресс бар, количество посещённых городов (1 из 1).
        * имеется 2 карточки регионов с непосещёнными городами и на каждой из которых имеется
          название региона, федеральный округ и количество посещённых городов (0 из 1).
        * имеется пагинация из 2 страниц

    `setup_1_city_in_1_region` создаёт 20 регионов и 20 городов (по 1 в каждом).
    `setup_18_visited_cities_in_18_regions` создаёт 18 посещённых городов в 18 регионах (по 1 в каждом).
    """
    client.login(username='username', password='password')
    response = client.get(url + "?page=2")
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    assert 'Регионы России' in response.content.decode()
    all_regions = source.find_all('div', {'class': 'card-region'})
    assert len(all_regions) == 4
    for index in range(0, 4):
        assert f'Регион {symbols[index + 16]}' in all_regions[index].text
        assert 'Area 1' in all_regions[index].text
    assert response.content.decode().count('1 из 1') == 2
    assert response.content.decode().count('0 из 1') == 2
    assert len(source.find_all('div', {'class': 'progress-bar'})) == 2
