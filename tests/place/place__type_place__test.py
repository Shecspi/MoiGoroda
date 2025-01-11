import json
from itertools import zip_longest

from django.urls import reverse, NoReverseMatch, resolve
from rest_framework.permissions import IsAuthenticated
from rest_framework.test import APIClient

from place.api import GetTypePlace
from place.models import TagOSM
from place.serializers import TypeObjectSerializer
from tests.create_db import create_user, create_type_object_of_place


def test__url_path_to_get_types_places_exists():
    try:
        reverse('type_place')
    except NoReverseMatch:
        assert False
    else:
        assert True


def test__correct_url_to_get_type_places():
    assert reverse('type_place') == '/api/place/type_place/'


def test__correct_resolve_by_url():
    assert resolve('/api/place/type_place/').func.cls == GetTypePlace


def test__get_type_places_has_correct_permission_classes():
    type_place = GetTypePlace()
    assert type_place.permission_classes == (IsAuthenticated,)


def test__get_type_places_has_correct_http_methods():
    type_place = GetTypePlace()
    correct_methods = ['get']
    assert all([i == j for i, j in zip_longest(correct_methods, type_place.http_method_names)])


def test__get_type_places_has_correct_serializer_class():
    type_place = GetTypePlace()
    assert type_place.serializer_class == TypeObjectSerializer


def test__get_type_places_1(django_user_model):
    create_user(django_user_model, 1)
    client = APIClient()
    client.login(username='username1', password='password')
    response = client.get(reverse('type_place'), format='json', charset='utf-8')

    assert response.status_code == 200
    assert response.json() == []


def test__get_type_places_2(django_user_model):
    create_user(django_user_model, 1)
    typeobject1 = create_type_object_of_place(1)
    typeobject2 = create_type_object_of_place(2)
    typeobject3 = create_type_object_of_place(3)

    client = APIClient()
    client.login(username='username1', password='password')
    response = client.get(reverse('type_place'), format='json', charset='utf-8')

    correct_response = [
        {'id': 1, 'name': 'Тип места 1', 'tags_detail': []},
        {'id': 2, 'name': 'Тип места 2', 'tags_detail': []},
        {'id': 3, 'name': 'Тип места 3', 'tags_detail': []},
    ]

    assert response.status_code == 200
    assert json.loads(response.content.decode('utf-8')) == correct_response


def test__get_type_places_3(django_user_model):
    create_user(django_user_model, 1)
    tag = TagOSM.objects.create(name='Название тега')
    typeobject = create_type_object_of_place(1)
    typeobject.tags.add(tag)
    typeobject.save()

    client = APIClient()
    client.login(username='username1', password='password')
    response = client.get(reverse('type_place'), format='json', charset='utf-8')

    correct_response = [
        {
            'id': typeobject.id,
            'name': typeobject.name,
            'tags_detail': [{'id': tag.id, 'name': tag.name}],
        }
    ]

    assert response.status_code == 200
    assert json.loads(response.content.decode('utf-8')) == correct_response
