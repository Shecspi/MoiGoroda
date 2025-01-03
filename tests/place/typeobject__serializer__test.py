import pytest

from place.models import TagOSM, TypeObject
from place.serializers import TypeObjectSerializer


def test__create_typeobject_serializer_can_create_instance():
    assert TypeObjectSerializer()


@pytest.mark.django_db
def test__create_typeobject_serializer_correct_data_1():
    tag1 = TagOSM.objects.create(name='river')
    tag2 = TagOSM.objects.create(name='water')

    data = {'name': 'Реки', 'tags': [tag1.id, tag2.id]}

    serializer = TypeObjectSerializer(data=data)
    assert serializer.is_valid()
    assert len(serializer.validated_data) == 2
    assert isinstance(serializer.validated_data.get('name'), str)
    assert isinstance(serializer.validated_data.get('tags'), list)
    assert len(serializer.validated_data.get('tags')) == 2


def test__create_typeobject_serializer_correct_data_2():
    data = {'name': 'Реки'}

    serializer = TypeObjectSerializer(data=data)
    assert serializer.is_valid()
    assert len(serializer.validated_data) == 1
    assert isinstance(serializer.validated_data.get('name'), str)


def test__typeobject_serializer_incorrect_data_1():
    # Тест основан на том, что сериализатор не может True превратить в строку
    data = {'name': True}
    serializer = TypeObjectSerializer(data=data)
    assert not serializer.is_valid()


@pytest.mark.django_db
def test__typeobject_serializer_incorrect_data_2():
    # Проверка ссылки на несуществующий тег
    data = {'name': 'Реки', 'tags': [1]}
    serializer = TypeObjectSerializer(data=data)
    assert not serializer.is_valid()


def test__typeobject_serializer_cant_create_instance_without_required_field():
    data = {'not_exists_field': 1}
    serializer = TypeObjectSerializer(data=data)
    assert not serializer.is_valid()

    # Поле 'name' обязательно, но tags может быть не заполнен
    assert len(serializer.errors) == 1
    assert serializer.errors.get('name')[0].code == 'required'
    assert 'tags' not in serializer.errors.get('name')[0]


@pytest.mark.django_db
def test__typeobject_serializer_can_insert_data_to_db_1():
    data = {'name': 'Реки'}
    serializer = TypeObjectSerializer(data=data)
    assert serializer.is_valid()

    serializer.save()
    assert TypeObject.objects.count() == 1

    type_object = TypeObject.objects.first()
    assert type_object.name == 'Реки'
    assert len(type_object.tags.all()) == 0


@pytest.mark.django_db
def test__typeobject_serializer_can_insert_data_to_db_2():
    tag1 = TagOSM.objects.create(name='river')
    tag2 = TagOSM.objects.create(name='water')

    data = {'name': 'Реки', 'tags': [tag1.id, tag2.id]}

    serializer = TypeObjectSerializer(data=data)
    assert serializer.is_valid()

    serializer.save()
    assert TypeObject.objects.count() == 1

    type_object = TypeObject.objects.first()
    assert type_object.name == 'Реки'
    assert len(type_object.tags.all()) == 2


@pytest.mark.django_db
def test__typeobject_serializer_reading():
    tag1 = TagOSM.objects.create(name='river')
    tag2 = TagOSM.objects.create(name='water')
    type_object = TypeObject.objects.create(name='Реки')
    type_object.tags.add(tag1)
    type_object.tags.add(tag2)

    serializer = TypeObjectSerializer(instance=TypeObject.objects.first())
    assert len(serializer.data) == 3
    assert serializer.data.get('id') == 1
    assert serializer.data['name'] == 'Реки'
    assert len(serializer.data.get('tags')) == 2
    assert serializer.data.get('tags')[0].get('id') == tag1.id
    assert serializer.data.get('tags')[0].get('name') == tag1.name
    assert serializer.data.get('tags')[1].get('id') == tag2.id
    assert serializer.data.get('tags')[1].get('name') == tag2.name
