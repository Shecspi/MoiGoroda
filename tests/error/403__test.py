"""
Тестирует корректность отображения страницы 403.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""


import pytest
from bs4 import BeautifulSoup
from django.urls import reverse

from city.models import City, VisitedCity
from region.models import Area, Region


@pytest.fixture
def setup_db(client, django_user_model):
    user = django_user_model.objects.create_user(username='username', password='password')
    area = Area.objects.create(title='Area 1')
    region = Region.objects.create(area=area, title='Регион 1', type='O')
    city = City.objects.create(title='Город 1', region=region, coordinate_width=1, coordinate_longitude=1)
    VisitedCity.objects.create(id=1, user=user, region=region, city=city, rating='5')


@pytest.mark.django_db
def test__access(setup_db, client):
    client.login(username='username', password='password')
    response = client.get(reverse('city-delete', kwargs={'pk': 1}))
    source = BeautifulSoup(response.content.decode(), 'html.parser')

    assert response.status_code == 403
    assert 'error/403.html' in (t.name for t in response.templates)
    assert source.find('img', {'src': '/static/image/error/403.png'})
    assert 'Отказано в доступе' in source.find('p').get_text()
