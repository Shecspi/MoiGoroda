import json
from itertools import zip_longest

from django.urls import reverse, NoReverseMatch, resolve
from rest_framework.permissions import IsAuthenticated
from rest_framework.test import APIClient

from place.api import GetPlaces
from place.models import Place
from place.serializers import PlaceSerializer
from tests.create_db import create_user, create_category_of_place, create_place


def test__url_path_to_get_places_exists():
    try:
        reverse('get_places')
    except NoReverseMatch:
        assert False
    else:
        assert True


def test__correct_url_to_get_places():
    assert reverse('get_places') == '/api/place/'


def test__correct_resolve_by_url():
    assert resolve('/api/place/').func.cls == GetPlaces


def test__get_places_has_correct_permission_classes():
    place = GetPlaces()
    assert place.permission_classes == (IsAuthenticated,)


def test__get_places_has_correct_http_methods():
    place = GetPlaces()
    correct_methods = ['get']
    assert all([i == j for i, j in zip_longest(correct_methods, place.http_method_names)])


def test__get_places_has_correct_serializer_class():
    place = GetPlaces()
    assert place.serializer_class == PlaceSerializer


def test__get_places__one_own_place(django_user_model):
    user = create_user(django_user_model, 1)
    category = create_category_of_place()
    place = create_place(name='Place name', lat=55.5, lon=66.6, category=category, user=user)
    assert Place.objects.count() == 1

    client = APIClient()
    client.login(username='username1', password='password')
    response = client.get(reverse('get_places'), format='json', charset='utf-8')

    correct_response = [
        {
            'id': place.id,
            'name': place.name,
            'latitude': place.latitude,
            'longitude': place.longitude,
            'category_detail': {'id': category.id, 'tags_detail': [], 'name': category.name},
            'created_at': place.created_at.isoformat(),
            'updated_at': place.updated_at.isoformat(),
        }
    ]

    assert response.status_code == 200
    assert json.loads(response.content.decode('utf-8')) == correct_response


def test__get_places__one_own_and_one_other_user_places(django_user_model):
    user1 = create_user(django_user_model, 1)
    user2 = create_user(django_user_model, 2)
    category = create_category_of_place()
    place1 = create_place(name='Place name 1', lat=55.5, lon=66.6, category=category, user=user1)
    create_place(name='Place name 2', lat=55.5, lon=66.6, category=category, user=user2)

    assert Place.objects.count() == 2

    client = APIClient()
    client.login(username='username1', password='password')
    response = client.get(reverse('get_places'), format='json', charset='utf-8')

    correct_response = [
        {
            'id': place1.id,
            'name': place1.name,
            'latitude': place1.latitude,
            'longitude': place1.longitude,
            'category_detail': {'id': category.id, 'tags_detail': [], 'name': category.name},
            'created_at': place1.created_at.isoformat(),
            'updated_at': place1.updated_at.isoformat(),
        }
    ]

    assert response.status_code == 200
    assert json.loads(response.content.decode('utf-8')) == correct_response


def test__get_places__two_own_places(django_user_model):
    user = create_user(django_user_model, 1)
    category = create_category_of_place()
    place1 = create_place(name='Place name 1', lat=55.5, lon=66.6, category=category, user=user)
    place2 = create_place(name='Place name 2', lat=55.5, lon=66.6, category=category, user=user)

    assert Place.objects.count() == 2

    client = APIClient()
    client.login(username='username1', password='password')
    response = client.get(reverse('get_places'), format='json', charset='utf-8')

    correct_response = [
        {
            'id': place1.id,
            'name': place1.name,
            'latitude': place1.latitude,
            'longitude': place1.longitude,
            'category_detail': {'id': category.id, 'tags_detail': [], 'name': category.name},
            'created_at': place1.created_at.isoformat(),
            'updated_at': place1.updated_at.isoformat(),
        },
        {
            'id': place2.id,
            'name': place2.name,
            'latitude': place2.latitude,
            'longitude': place2.longitude,
            'category_detail': {'id': category.id, 'tags_detail': [], 'name': category.name},
            'created_at': place2.created_at.isoformat(),
            'updated_at': place2.updated_at.isoformat(),
        },
    ]

    assert response.status_code == 200
    assert json.loads(response.content.decode('utf-8')) == correct_response
