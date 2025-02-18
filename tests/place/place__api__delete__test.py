from itertools import zip_longest

from django.urls import reverse, resolve
from rest_framework.permissions import IsAuthenticated
from rest_framework.test import APIClient

from place.api import DeletePlace
from place.models import Place
from tests.create_db import create_user, create_category_of_place, create_place


def test__correct_resolve_by_url():
    assert resolve('/api/place/delete/1').func.cls == DeletePlace


def test__correct_url_for_deleting_place():
    assert reverse('delete_place', kwargs={'pk': 1}) == '/api/place/delete/1'


def test__delete_place_has_correct_permission_classes():
    place = DeletePlace()
    assert place.permission_classes == (IsAuthenticated,)


def test__delete_place_has_correct_http_methods():
    place = DeletePlace()
    correct_methods = ['delete']
    assert all([i == j for i, j in zip_longest(correct_methods, place.http_method_names)])


def test__can_delete_own_place(django_user_model):
    user = create_user(django_user_model, 1)
    category = create_category_of_place()
    place = create_place(name='Place name', lat=55.5, lon=66.6, category=category, user=user)
    assert Place.objects.count() == 1

    client = APIClient()
    client.login(username='username1', password='password')
    response = client.delete(
        reverse('delete_place', kwargs={'pk': place.id}), format='json', charset='utf-8'
    )

    assert response.status_code == 204
    assert Place.objects.count() == 0


def test__can_not_delete_other_users_place(django_user_model):
    user1 = create_user(django_user_model, 1)
    create_user(django_user_model, 2)
    category = create_category_of_place()

    # Запись создаётся от имени одного пользователя, а пытаемся удалить от другого
    place = create_place(name='Place name 1', lat=55.5, lon=66.6, category=category, user=user1)
    assert Place.objects.count() == 1

    client = APIClient()
    client.login(username='username2', password='password')
    response = client.delete(
        reverse('delete_place', kwargs={'pk': place.id}), format='json', charset='utf-8'
    )

    assert response.status_code == 404
    assert Place.objects.count() == 1


def test__can_not_delete_non_existent_place(django_user_model):
    create_user(django_user_model, 1)
    assert Place.objects.count() == 0

    client = APIClient()
    client.login(username='username1', password='password')
    response = client.delete(
        reverse('delete_place', kwargs={'pk': 1}), format='json', charset='utf-8'
    )

    assert response.status_code == 404
    assert Place.objects.count() == 0


def test__delete_places_has_correct_log_records(django_user_model, caplog):
    user = create_user(django_user_model, 1)
    category = create_category_of_place()
    place = create_place(name='Place name', lat=55.5, lon=66.6, category=category, user=user)

    client = APIClient()
    client.login(username='username1', password='password')
    client.delete(reverse('delete_place', kwargs={'pk': place.id}), format='json', charset='utf-8')

    assert caplog.records[0].levelname == 'INFO'
    assert (
        caplog.records[0].getMessage()
        == f'(API: Place): Deleting a place #{place.id}   /api/place/delete/{place.id}'
    )
