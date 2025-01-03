import pytest

from place.models import TypeObject, Place
from place.serializers import PlaceSerializer


def test__place_serializer_can_create_instance():
    assert PlaceSerializer()


@pytest.mark.django_db
def test__place_serializer_correct_data():
    type_object = TypeObject.objects.create(name='Реки')
    data = {
        'name': 'Название места',
        'latitude': 55.63423,
        'longitude': 37.6176,
        'type_object': type_object.id,
    }
    serializer = PlaceSerializer(data=data)

    serializer.is_valid()
    assert len(serializer.validated_data) == 4
    assert isinstance(serializer.validated_data.get('name'), str)
    assert isinstance(serializer.validated_data.get('latitude'), float)
    assert isinstance(serializer.validated_data.get('longitude'), float)
    assert isinstance(serializer.validated_data.get('type_object'), TypeObject)


def test__place_serializer_cant_create_instance_without_required_field():
    data = {'not_exists_field': 1}
    serializer = PlaceSerializer(data=data)
    assert not serializer.is_valid()

    assert len(serializer.errors) == 4
    assert serializer.errors.get('name')[0].code == 'required'
    assert serializer.errors.get('latitude')[0].code == 'required'
    assert serializer.errors.get('longitude')[0].code == 'required'
    assert serializer.errors.get('type_object')[0].code == 'required'


@pytest.mark.django_db
def test__place_serializer_can_insert_data_to_db_1():
    type_object = TypeObject.objects.create(name='Реки')
    data = {
        'name': 'Название места',
        'latitude': 55.63423,
        'longitude': 37.6176,
        'type_object': type_object.id,
    }
    serializer = PlaceSerializer(data=data)
    assert serializer.is_valid()

    serializer.save()
    assert Place.objects.count() == 1

    place = Place.objects.first()
    assert place.name == 'Название места'
    assert place.latitude == 55.63423
    assert place.longitude == 37.6176
    assert place.type_object == type_object
