import pytest

from place.models import TagOSM
from place.serializers import TagOSMSerializer


def test__tagosm_serializer_can_create_instance():
    assert TagOSMSerializer()


def test__tagosm_serializer_correct_data():
    data = {'name': 'river', 'not_exists_field': 1}
    serializer = TagOSMSerializer(data=data)
    assert serializer.is_valid()
    assert len(serializer.validated_data) == 1
    assert isinstance(serializer.validated_data.get('name'), str)


def test__tagosm_serializer_cant_create_instance_without_required_field():
    data = {'not_exists_field': 1}
    serializer = TagOSMSerializer(data=data)

    assert not serializer.is_valid()
    assert len(serializer.errors) == 1
    assert serializer.errors.get('name')[0].code == 'required'


def test__tagosm_serializer_incorrect_data():
    # Тест основан на том, что сериализатор не может True превратить в строку
    data = {'name': True}
    serializer = TagOSMSerializer(data=data)
    assert not serializer.is_valid()


@pytest.mark.django_db
def test__tagosm_serializer_can_insert_data_to_db():
    data = {'name': 'river'}
    serializer = TagOSMSerializer(data=data)
    assert serializer.is_valid()

    serializer.create(serializer.validated_data)
    assert TagOSM.objects.count() == 1
    tag = TagOSM.objects.first()
    assert tag.name == 'river'
