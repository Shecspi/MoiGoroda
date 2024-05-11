"""
Тестирует корректность отображения страницы 404.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from bs4 import BeautifulSoup


@pytest.mark.django_db
def test__access(client):
    response = client.get('incorrect_url')
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    assert response.status_code == 404
    assert 'error/404.html' in (t.name for t in response.templates)
    assert source.find('img', {'src': '/static/image/error/404.png'})
    assert 'Страница не найдена' in source.find('p').get_text()
