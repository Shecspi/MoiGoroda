"""
Тестирует корректность обработки ситуации, когда в БД нет ни одного города для указанного региона.
Вообще, такая ситуация никогда не должна возникать, но протестировать всё-таки стоит.
Страница тестирования '/region/<int>/list'.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from bs4 import BeautifulSoup
from django.urls import reverse

from region.models import Area, Region


@pytest.fixture
def setup_db(client):
    area = Area.objects.create(title='Area 1')
    Region.objects.create(id=1, area=area, title=f'Регион 1', type='область', iso3166='RU-RU-1')


@pytest.mark.django_db
def test__content__error_message(setup_db, client):
    response = client.get(reverse('region-selected-list', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')
    error_message = source.find('div', {'id': 'error_message'})
    lines = [
        'В сервисе "Мои города" для региона Регион 1 область не сохранено ни одного города.',
        'Произошла ошибка, мы постараемся как можно быстрее исправить её.',
        'Приносим свои извинения за доставленные неудобства.',
    ]

    assert error_message
    for line in lines:
        assert line in error_message.get_text()
