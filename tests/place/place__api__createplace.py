import json
from itertools import zip_longest

from django.urls import reverse, NoReverseMatch
from rest_framework.permissions import IsAuthenticated
from rest_framework.test import APIClient

from place.api import CreatePlace
from place.serializers import PlaceSerializer
from tests.create_db import create_user, create_type_object_of_place


def test__url_path_to_create_place_exists():
    try:
        reverse('create_place')
    except NoReverseMatch:
        assert False
    else:
        assert True


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
    user = create_user(django_user_model, 1)
    typeobject = create_type_object_of_place()
    data = {
        'name': 'Place name',
        'latitude': 55.5,
        'longitude': 66.6,
        'type_object': typeobject.id,
    }

    client = APIClient()
    client.login(username='username1', password='password')
    response = client.post('/api/place/create/', data=data, format='json', charset='utf-8')
    response_json = json.loads(response.content.decode('utf-8'))
    print(response_json)

    assert response.status_code == 201
    for key in ['name', 'latitude', 'longitude', 'type_object_detail', 'created_at', 'updated_at']:
        assert key in response_json
    assert response_json.get('name') == 'Place name'
    assert response_json.get('latitude') == 55.5
    assert response_json.get('longitude') == 66.6
    assert response_json.get('type_object_detail').get('id') == typeobject.id
