"""

Copyright 2024 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

"""

import re
import pytest
from bs4 import BeautifulSoup

from django.urls import reverse

url = reverse('news-list')
login_url = reverse('signin')


@pytest.mark.django_db
def test__guest_has_no_info_about_number_of_users_who_read_news(setup, client):
    response = client.get(url)
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    footer = source.find('div', {'id': 'news_1'}).find('div', {'class': 'card-footer'})

    assert 'Количество прочитываний' not in footer.get_text()


@pytest.mark.django_db
def test__regular_user_has_no_info_about_number_of_users_who_read_news(setup, client):
    client.login(username='username1', password='password')
    response = client.get(url)
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    footer = source.find('div', {'id': 'news_1'}).find('div', {'class': 'card-footer'})

    assert 'Количество прочитываний' not in footer.get_text()


@pytest.mark.django_db
def test__superuser_has_info_about_number_of_users_who_read_news(setup, client):
    """
    Что происходит в этом тесте:
    1. Заходим на страницу с аккаунта суперпользователя. Он должен увидеть надпись "Количество прочитываний: 0".
       Текущий заход не засчитывается в этот показатель.
    2. Далее заходим на страницу под аккаунтом обычного пользователя. Счётчик прочитываний становится равным 2.
    3. Чтобы увидеть эту цифру, заходим ещё раз под аккаунтом суперпользователя.
    """
    client.login(username='superuser2', password='password')
    response = client.get(url)
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    footer = source.find('div', {'id': 'news_1'}).find('div', {'class': 'card-footer'})
    assert 'Количество прочитываний: 0' in footer.get_text()

    client.login(username='username1', password='password')
    client.get(url)

    client.login(username='superuser2', password='password')
    response = client.get(url)
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    footer = source.find('div', {'id': 'news_1'}).find('div', {'class': 'card-footer'})
    assert 'Количество прочитываний: 2' in footer.get_text()


@pytest.mark.django_db
def test__news__unreaded_message__guest(setup, client):
    """
    У неавторизованного пользовавтеля в карточке новости не должно быть
    никакой информации о том, прочитана эта новость или нет.
    """
    response = client.get(url)
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    footer = source.find('div', {'id': 'news_1'}).find('div', {'class': 'card-footer'})

    assert 'Не прочитано' not in footer.get_text()
    assert not footer.find('i', 'fa-solid fa-envelope')
    assert 'Прочитано' not in footer.get_text()
    assert not footer.find('i', 'fa-regular fa-envelope-open')


@pytest.mark.django_db
def test__news__unreaded_message__auth_user(setup, client):
    """
    При первом заходе на страницу новостей авторизованным пользователем
    непрочитанная новость должна иметь соответствующую пометку.
    """
    client.login(username='username1', password='password')
    response = client.get(url)
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    footer = source.find('div', {'id': 'news_1'}).find('div', {'class': 'card-footer'})

    assert 'Не прочитано' in footer.get_text()
    assert footer.find('i', 'fa-solid fa-envelope')
    assert 'Прочитано' not in footer.get_text()
    assert not footer.find('i', 'fa-regular fa-envelope-open')


@pytest.mark.django_db
def test__news__read_messages__auth_user(setup, client):
    """
    При первом прочтении новости авторизованным пользователем она помечается как прочитанная
    и при повторном заходе на страницу новость должна быть отмечена как прочитанная.
    """
    client.login(username='username1', password='password')

    # После первого открытия страницы новость должна отображаться как непрочитанная
    response = client.get(url)
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    footer = source.find('div', {'id': 'news_1'}).find('div', {'class': 'card-footer'})
    assert 'Не прочитано' in footer.get_text()
    assert footer.find('i', 'fa-solid fa-envelope')
    assert 'Прочитано' not in footer.get_text()
    assert not footer.find('i', 'fa-regular fa-envelope-open')

    # А после второго - как прочитанная
    response = client.get(url)
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    footer = source.find('div', {'id': 'news_1'}).find('div', {'class': 'card-footer'})
    assert 'Не прочитано' not in footer.get_text()
    assert not footer.find('i', 'fa-solid fa-envelope')
    assert 'Прочитано' in footer.get_text()
    assert footer.find('i', 'fa-regular fa-envelope-open')


@pytest.mark.django_db
def test__news__unread_messages__sidebar__auth_user(setup, client):
    """
    При заходе на любую страницу сайта авторизованный пользователь должен видеть уведомление
    о наличии непрочитанных новостей (в случае, если они имеются)
    """
    client.login(username='username1', password='password')
    # Проверять нужно на другой странице (не на новостях),
    # так как непрочитанная новость сразу же помечается прочитанной и бейджик не отображается в сайдбаре
    response = client.get(reverse('city-all-list'))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    sidebar_news = (
        source.find('div', {'class': 'sidebar'}).find('ul').find('li', {'id': 'sidebar_news'})
    )
    link_news = sidebar_news.find('a', {'id': 'sidebar_news_link'})
    span = link_news.find('span', {'class': 'badge bg-danger'})

    assert span
    assert span.find('i', {'class': 'fa-solid fa-comment-dots'})
    assert 'Новые' in span.get_text()


@pytest.mark.django_db
def test__news__read_messages__sidebar__auth_user(setup, client):
    """
    Если непрочитанных новостей нет, то и уведомления на сайдбаре не должно быть.
    """
    client.login(username='username1', password='password')
    response = client.get(url)
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    sidebar_news = (
        source.find('div', {'class': 'sidebar'}).find('ul').find('li', {'id': 'sidebar_news'})
    )
    link_news = sidebar_news.find('a', {'id': 'sidebar_news_link'})
    span = link_news.find('span', {'class': 'badge bg-danger'})

    assert not span
    assert 'Новые' not in link_news.get_text()


@pytest.mark.django_db
def test__news__read_messages__sidebar__guest(setup, client):
    """
    Для неавторизованных пользователей на сайдбаре никаких уведомлений быть не должно.
    """
    response = client.get(url)
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    sidebar_news = (
        source.find('div', {'class': 'sidebar'}).find('ul').find('li', {'id': 'sidebar_news'})
    )
    link_news = sidebar_news.find('a', {'id': 'sidebar_news_link'})
    span = link_news.find('span', {'class': 'badge bg-danger'})

    assert not span
    assert 'Новые' not in link_news.get_text()


@pytest.mark.django_db
def test__news__html_tags_headers(setup, client):
    response = client.get(url)
    assert '<h1>H1</h1>' in response.content.decode()
    assert '<h2>H2</h2>' in response.content.decode()
    assert '<h3>H3</h3>' in response.content.decode()
    assert '<h4>H4</h4>' in response.content.decode()
    assert '<h5>H5</h5>' in response.content.decode()
    assert '<h6>H6</h6>' in response.content.decode()


@pytest.mark.django_db
def test__news__html_tags_text_style(setup, client):
    response = client.get(url)
    assert '<strong>bold1</strong>' in response.content.decode()
    assert '<strong>bold2</strong>' in response.content.decode()
    assert '<em>italic1</em>' in response.content.decode()
    assert '<em>italic2</em>' in response.content.decode()


@pytest.mark.django_db
def test__news__html_tags_link(setup, client):
    response = client.get(url)
    assert '<a href="https://link">Link</a>' in response.content.decode()


@pytest.mark.django_db
def test__news__html_tags_image(setup, client):
    response = client.get(url)
    assert '<img alt="Изображение" src="https://link">' in response.content.decode()


@pytest.mark.django_db
def test__news__html_tags_code(setup, client):
    response = client.get(url)
    assert '<code>somecode1</code>' in response.content.decode()
    assert '<code>somecode2</code>' in response.content.decode()


@pytest.mark.django_db
def test__news__html_tags_blockquote(setup, client):
    response = client.get(url)
    parse = re.compile(r'(?s)<blockquote>(.*?)</blockquote>')
    assert re.search(parse, response.content.decode())


@pytest.mark.django_db
def test__news__html_tags_list(setup, client):
    response = client.get(url)
    parse1 = re.compile(r'(?s)<ul>(.*?)</ul>')
    parse2 = re.compile(r'(?s)<li>(.*?)</li>')
    assert re.search(parse1, response.content.decode())
    assert re.search(parse2, response.content.decode())


@pytest.mark.django_db
def test__news__without_title(setup, client):
    response = client.get(url)
    assert 'Заголовок новости 1' not in response.content.decode()
    assert 'Заголовок новости 2' not in response.content.decode()
