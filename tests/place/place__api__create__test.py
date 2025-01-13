import json
from itertools import zip_longest

from django.urls import reverse, NoReverseMatch, resolve
from rest_framework.permissions import IsAuthenticated
from rest_framework.test import APIClient

from place.api import CreatePlace
from place.serializers import PlaceSerializer
from tests.create_db import create_user, create_category_of_place


def test__url_path_to_create_place_exists():
    try:
        reverse('create_place')
    except NoReverseMatch:
        assert False
    else:
        assert True


def test__correct_url_for_creation_place():
    assert reverse('create_place') == '/api/place/create/'


def test__correct_resolve_by_url():
    assert resolve('/api/place/create/').func.cls == CreatePlace


def test__create_place_has_correct_permission_classes():
    place = CreatePlace()
    assert place.permission_classes == (IsAuthenticated,)


def test__create_place_has_correct_http_methods():
    place = CreatePlace()
    correct_methods = ['post']
    assert all([i == j for i, j in zip_longest(correct_methods, place.http_method_names)])


def test__create_place_has_correct_serializer_class():
    place = CreatePlace()
    assert place.serializer_class == PlaceSerializer


def test__create_place_can_process_correct_data(django_user_model):
    create_user(django_user_model, 1)
    category = create_category_of_place()
    data = {
        'name': 'Place name',
        'latitude': 55.5,
        'longitude': 66.6,
        'category': category.id,
    }

    client = APIClient()
    client.login(username='username1', password='password')
    response = client.post('/api/place/create/', data=data, format='json', charset='utf-8')
    response_json = json.loads(response.content.decode('utf-8'))

    assert response.status_code == 201
    for key in ['name', 'latitude', 'longitude', 'category_detail', 'created_at', 'updated_at']:
        assert key in response_json
    assert response_json.get('name') == 'Place name'
    assert response_json.get('latitude') == 55.5
    assert response_json.get('longitude') == 66.6
    assert response_json.get('category_detail').get('id') == category.id
