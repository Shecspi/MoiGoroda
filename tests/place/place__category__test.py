import json
from itertools import zip_longest

from django.urls import reverse, NoReverseMatch, resolve
from rest_framework.permissions import IsAuthenticated
from rest_framework.test import APIClient

from place.api import GetCategory
from place.models import TagOSM
from place.serializers import CategorySerializer
from tests.create_db import create_user, create_category_of_place


def test__url_path_to_get_category_exists():
    try:
        reverse('category_of_place')
    except NoReverseMatch:
        assert False
    else:
        assert True


def test__correct_url_to_get_category():
    assert reverse('category_of_place') == '/api/place/category/'


def test__correct_resolve_by_url():
    assert resolve('/api/place/category/').func.cls == GetCategory


def test__get_category_has_correct_permission_classes():
    category = GetCategory()
    assert category.permission_classes == (IsAuthenticated,)


def test__get_category_has_correct_http_methods():
    category = GetCategory()
    correct_methods = ['get']
    assert all([i == j for i, j in zip_longest(correct_methods, category.http_method_names)])


def test__get_category_has_correct_serializer_class():
    category = GetCategory()
    assert category.serializer_class == CategorySerializer


def test__get_category_1(django_user_model):
    create_user(django_user_model, 1)
    client = APIClient()
    client.login(username='username1', password='password')
    response = client.get(reverse('category_of_place'), format='json', charset='utf-8')

    assert response.status_code == 200
    assert response.json() == []


def test__get_category_2(django_user_model):
    create_user(django_user_model, 1)
    category1 = create_category_of_place(1)
    category2 = create_category_of_place(2)
    category3 = create_category_of_place(3)

    client = APIClient()
    client.login(username='username1', password='password')
    response = client.get(reverse('category_of_place'), format='json', charset='utf-8')

    correct_response = [
        {'id': category1.id, 'name': category1.name, 'tags_detail': []},
        {'id': category2.id, 'name': category2.name, 'tags_detail': []},
        {'id': category3.id, 'name': category3.name, 'tags_detail': []},
    ]

    assert response.status_code == 200
    assert json.loads(response.content.decode('utf-8')) == correct_response


def test__get_category_3(django_user_model):
    create_user(django_user_model, 1)
    tag = TagOSM.objects.create(name='Название тега')
    category = create_category_of_place(1)
    category.tags.add(tag)
    category.save()

    client = APIClient()
    client.login(username='username1', password='password')
    response = client.get(reverse('category_of_place'), format='json', charset='utf-8')

    correct_response = [
        {
            'id': category.id,
            'name': category.name,
            'tags_detail': [{'id': tag.id, 'name': tag.name}],
        }
    ]

    assert response.status_code == 200
    assert json.loads(response.content.decode('utf-8')) == correct_response
