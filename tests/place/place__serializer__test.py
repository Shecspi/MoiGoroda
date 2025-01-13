import pytest

from place.models import Category, Place, TagOSM
from place.serializers import PlaceSerializer
from tests.create_db import create_user


def test__place_serializer_can_create_instance():
    assert PlaceSerializer()


@pytest.mark.django_db
def test__place_serializer_correct_data():
    category = Category.objects.create(name='Реки')
    data = {
        'name': 'Название места',
        'latitude': 55.63423,
        'longitude': 37.6176,
        'category': category.id,
    }
    serializer = PlaceSerializer(data=data)

    serializer.is_valid()
    assert len(serializer.validated_data) == 4
    assert isinstance(serializer.validated_data.get('name'), str)
    assert isinstance(serializer.validated_data.get('latitude'), float)
    assert isinstance(serializer.validated_data.get('longitude'), float)
    assert isinstance(serializer.validated_data.get('category'), Category)


def test__place_serializer_cant_create_instance_without_required_field():
    data = {'not_exists_field': 1}
    serializer = PlaceSerializer(data=data)
    assert not serializer.is_valid()

    assert len(serializer.errors) == 4
    assert serializer.errors.get('name')[0].code == 'required'
    assert serializer.errors.get('latitude')[0].code == 'required'
    assert serializer.errors.get('longitude')[0].code == 'required'
    assert serializer.errors.get('category')[0].code == 'required'


@pytest.mark.django_db
def test__place_serializer_can_insert_data_to_db(django_user_model):
    user = create_user(django_user_model, 1)
    category = Category.objects.create(name='Реки')
    data = {
        'name': 'Название места',
        'latitude': 55.63423,
        'longitude': 37.6176,
        'category': category.id,
        'user': user.id,
    }
    serializer = PlaceSerializer(data=data)
    assert serializer.is_valid()
    serializer.save()
    assert Place.objects.count() == 1

    place = Place.objects.first()
    assert place.name == 'Название места'
    assert place.latitude == 55.63423
    assert place.longitude == 37.6176
    assert place.category == category


@pytest.mark.django_db
def test__place_serializer_reading(django_user_model):
    user = create_user(django_user_model, 1)
    tag = TagOSM.objects.create(name='river')
    category = Category.objects.create(name='Реки')
    category.tags.add(tag)
    place = Place.objects.create(
        name='Название', latitude=55.63423, longitude=37.6176, category=category, user=user
    )

    serializer = PlaceSerializer(instance=Place.objects.first())
    assert len(serializer.data) == 7
    assert serializer.data.get('id') == place.id
    assert serializer.data.get('name') == place.name
    assert serializer.data.get('latitude') == place.latitude
    assert serializer.data.get('longitude') == place.longitude
    assert len(serializer.data.get('category_detail')) == 3
    assert serializer.data.get('category_detail').get('id') == category.id
    assert serializer.data.get('category_detail').get('name') == category.name
    # Сериализатор возвращает дату с разделителем Т между датой и временем
    assert serializer.data.get('created_at') == str(place.created_at).replace(' ', 'T')
    assert serializer.data.get('updated_at') == str(place.updated_at).replace(' ', 'T')
