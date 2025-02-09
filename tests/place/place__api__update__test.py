from itertools import zip_longest

from django.urls import resolve, reverse
from rest_framework.permissions import IsAuthenticated
from rest_framework.test import APIClient

from place.api import UpdatePlace
from place.models import Place
from place.serializers import PlaceSerializer
from tests.create_db import create_user, create_category_of_place, create_place


def correct_resolve_by_url__test():
    assert resolve('/api/place/update/1').func.cls == UpdatePlace


def correct_url_for_updating_place__test():
    assert reverse('update_place', kwargs={'pk': 1}) == '/api/place/update/1'


def update_place_has_correct_permission_classes__test():
    place = UpdatePlace()
    assert place.permission_classes == (IsAuthenticated,)


def update_place_has_correct_http_methods__test():
    place = UpdatePlace()
    correct_methods = ['patch']
    assert all([i == j for i, j in zip_longest(correct_methods, place.http_method_names)])


def update_place_has_correct_serializer__test():
    place = UpdatePlace()
    assert place.serializer_class == PlaceSerializer


def can_update_own_place__test(django_user_model):
    user = create_user(django_user_model, 1)
    category1 = create_category_of_place()
    category2 = create_category_of_place(2)
    place = create_place(name='Place name', lat=55.5, lon=66.6, category=category1, user=user)

    client = APIClient()
    client.login(username='username1', password='password')
    response = client.patch(
        reverse('update_place', kwargs={'pk': place.id}),
        data={
            'name': 'Updated place name',
            'category': category2.id,
            'latitude': 100,
            'longitude': 200,
            'id': 777,
        },
        format='json',
        charset='utf-8',
    )

    assert response.status_code == 200
    assert Place.objects.get(id=place.id).name == 'Updated place name'
    assert Place.objects.get(id=place.id).category.id == category2.id
    # updated_at должно поменяться и, соответственно, не должно быть равно предыдущему значению
    assert Place.objects.get(id=place.id).updated_at != place.updated_at

    # Убеждаемся, что данные поля не редактируются, даже если переданы
    assert Place.objects.get(id=place.id).latitude == place.latitude
    assert Place.objects.get(id=place.id).longitude == place.longitude
    assert Place.objects.get(id=place.id).user == user
    assert Place.objects.get(id=place.id).id == place.id
    assert Place.objects.get(id=place.id).created_at == place.created_at


def can_not_update_other_users_place__test(django_user_model):
    user1 = create_user(django_user_model, 1)
    create_user(django_user_model, 2)
    category = create_category_of_place()

    # Запись создаётся от имени одного пользователя, а пытаемся изменить от другого
    place = create_place(name='Place name 1', lat=55.5, lon=66.6, category=category, user=user1)
    assert Place.objects.count() == 1

    client = APIClient()
    client.login(username='username2', password='password')
    response = client.patch(
        reverse('update_place', kwargs={'pk': place.id}),
        data={'name': 'Updated place name'},
        format='json',
        charset='utf-8',
    )

    assert response.status_code == 404


def update_places_has_correct_log_records__test(django_user_model, caplog):
    user = create_user(django_user_model, 1)
    category = create_category_of_place()
    place = create_place(name='Place name', lat=55.5, lon=66.6, category=category, user=user)

    client = APIClient()
    client.login(username='username1', password='password')
    client.patch(
        reverse('update_place', kwargs={'pk': place.id}),
        data={'name': 'Updated place name'},
        format='json',
        charset='utf-8',
    )

    new_place = Place.objects.get(id=place.id)
    assert caplog.records[0].levelname == 'INFO'
    assert (
        caplog.records[0].getMessage()
        == f'(API: Place): Updating a place #{place.id}. Name: "{place.name}" -> "{new_place.name}"   /api/place/update/{place.id}'
    )
