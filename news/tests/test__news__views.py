import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MoiGoroda.settings')

import django
django.setup()

import re
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


@pytest.mark.django_db
def test__news__html_tags_headers(setup_db, client):
    """
    Тестирует, что маркдаун разметка преобразуется в HTML-тэги.
    """
    response = client.get(url)
    assert '<h1>H1</h1>' in response.content.decode()
    assert '<h2>H2</h2>' in response.content.decode()
    assert '<h3>H3</h3>' in response.content.decode()
    assert '<h4>H4</h4>' in response.content.decode()
    assert '<h5>H5</h5>' in response.content.decode()
    assert '<h6>H6</h6>' in response.content.decode()


@pytest.mark.django_db
def test__news__html_tags_text_style(setup_db, client):
    response = client.get(url)
    assert '<strong>bold1</strong>' in response.content.decode()
    assert '<strong>bold2</strong>' in response.content.decode()
    assert '<em>italic1</em>' in response.content.decode()
    assert '<em>italic2</em>' in response.content.decode()


@pytest.mark.django_db
def test__news__html_tags_link(setup_db, client):
    response = client.get(url)
    assert '<a href="https://link">Link</a>' in response.content.decode()


@pytest.mark.django_db
def test__news__html_tags_image(setup_db, client):
    response = client.get(url)
    assert '<img alt="Изображение" src="https://link">' in response.content.decode()


@pytest.mark.django_db
def test__news__html_tags_code(setup_db, client):
    response = client.get(url)
    assert '<code>somecode1</code>' in response.content.decode()
    assert '<code>somecode2</code>' in response.content.decode()


@pytest.mark.django_db
def test__news__html_tags_blockquote(setup_db, client):
    response = client.get(url)
    parse = re.compile(r'(?s)<blockquote>(.*?)</blockquote>')
    assert re.search(parse, response.content.decode())


@pytest.mark.django_db
def test__news__html_tags_list(setup_db, client):
    response = client.get(url)
    parse1 = re.compile(r'(?s)<ul>(.*?)</ul>')
    parse2 = re.compile(r'(?s)<li>(.*?)</li>')
    assert re.search(parse1, response.content.decode())
    assert re.search(parse2, response.content.decode())


@pytest.mark.django_db
def test__news__without_title(setup_db, client):
    response = client.get(url)
    assert 'Заголовок новости 1' not in response.content.decode()
    assert 'Заголовок новости 2' not in response.content.decode()
