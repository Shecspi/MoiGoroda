import pytest

from bs4 import BeautifulSoup
from django.urls import reverse


url = reverse('region-all')
create_url = reverse('city-create')
login_url = reverse('signin')


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
def test_content_zero_regions(setup_db, create_user, client):
    """
    Тестирование ситуации, когда у авторизованного пользователя нет посещённых регионов.
    В таком случае должны отображаться карточки с регионами, на которых:
        * имеется заголовок страницы
        * имеется 16 карточек с регионами
        * на каждой из 16 карточек указывается о 0 посещённых городов и общем их количестве в регионе (0 из 1)
        * на каждой из 16 карточек есть информация о названии региона
        * на каждой из 16 карточек есть информация о федеральном округе
        * на всех карточках нет прогресс-бара посещённых городов
        * имеется пагинация из 2 страниц

    `setup_db` создаёт 20 регионов и 20 городов в них.
    """
    client.login(username='username', password='password')
    response = client.get(url)
    assert 'Регионы России' in response.content.decode()
    assert response.content.decode().count('0 из 1') == 16
    assert response.content.decode().count('Area 1') == 16
    for i in 'АБВГДЕЁЖЗИЙКЛМНО':
        assert f'Регион {i} область' in response.content.decode()
    assert '<div class="progress-bar' not in response.content.decode()
    assert 'Страница 1 из 2' in response.content.decode()


@pytest.mark.django_db
def test_content_1_page(create_user, setup_db, setup_visited_cities_10_cities, client):
    """
    Тестирование ситуации, когда у авторизованного пользователя
    посещено регионовом меньше, чем отображается на странице.
    В таком случае должны отображаться карточки с регионами:
        * имеется заголовок страницы
        * отображаются все регионы согласно пагинации, даже не посещённые
        * на каждой из 16 карточек есть информация о названии региона
        * на каждой из 16 карточек есть информация о федеральном округе
        * имеется 10 карточек с посещёнными регионами
        * на каждой из 10 карточек указывается об 1 посещённом городе из 1
        * на каждой из 10 карточек имеется прогресс-бар
        * имеется 6 карточек с непосещёнными регионами
        * на каждой из 6 карточек указывается об 0 посещённом городов из 1
        * имеется пагинация из 2 страниц

    `setup_db` создаёт 20 регионов и 20 городов в них.
    """
    client.login(username='username', password='password')
    response = client.get(url)

    assert 'Регионы России' in response.content.decode()

    # На странице должно отображаться 16 регионов (даже если они небыли посещены)
    for i in 'АБВГДЕЁЖЗИЙКЛМНО':
        assert f'Регион {i} область' in response.content.decode()
    assert 'Регион П' not in response.content.decode()
    assert response.content.decode().count('Area 1') == 16

    assert response.content.decode().count('1 из 1') == 10
    assert response.content.decode().count('<div class="progress-bar') == 10
    assert response.content.decode().count('0 из 1') == 6

    assert 'Страница 1 из 2' in response.content.decode()


@pytest.mark.django_db
def test_content_2_page(create_user, setup_db, setup_visited_cities_10_cities, client):
    """
    Тестирование ситуации, когда у авторизованного пользователя
    посещено регионовом меньше, чем отображается на странице.
    В данном случае - открыта вторая страница. На ней вообще нет посещённых городов.
    В таком случае должны отображаться карточки с регионами:
        * имеется заголовок страницы
        * отображаются все регионы согласно пагинации, даже не посещённые
        * на каждой из 4 карточек есть информация о названии региона
        * на каждой из 4 карточек есть информация о федеральном округе
        * карточек с посещёнными регионами нет
        * имеется 4 карточки с непосещёнными регионами
        * на каждой из 4 карточек указывается об 0 посещённом городов из 1
        * на каждой из 4 карточек указывается об 0 посещённом городов из 1
        * имеется пагинация из 2 страниц

    `setup_db` создаёт 20 регионов и 20 городов в них.
    """
    client.login(username='username', password='password')
    response = client.get(f'{url}?page=2')

    assert 'Регионы России' in response.content.decode()

    # На странице должно отображаться 4 региона с 17 по 20 (даже если они небыли посещены)
    for i in 'ПРСТ':
        assert f'Регион {i} область' in response.content.decode()
    assert 'Регион А' not in response.content.decode()
    assert 'Регион О' not in response.content.decode()
    assert response.content.decode().count('Area 1') == 4

    assert response.content.decode().count('1 из 1') == 0
    assert response.content.decode().count('0 из 1') == 4
    assert response.content.decode().count('<div class="progress-bar') == 0

    assert 'Страница 2 из 2' in response.content.decode()
