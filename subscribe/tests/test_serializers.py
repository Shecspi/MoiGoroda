import pytest
from subscribe.serializers import NotificationSerializer


@pytest.fixture
def valid_data():
    return {
        'is_read': True,
    }


@pytest.fixture
def invalid_data():
    return {
        'id': 1,  # read_only поле, попытка изменить
        'message': 'Text',  # read_only поле, попытка изменить
        'is_read': 'not_bool',  # неверный тип
    }


def test_serializer_accepts_valid_data(valid_data):
    serializer = NotificationSerializer(data=valid_data)
    assert serializer.is_valid()
    assert serializer.validated_data == {'is_read': True}


def test_serializer_rejects_invalid_data(invalid_data):
    serializer = NotificationSerializer(data=invalid_data)
    # Проверяем, что при попытке изменить readonly поля данные не валидируются
    assert not serializer.is_valid()
    errors = serializer.errors
    assert 'id' in errors or 'message' in errors or 'is_read' in errors  # Ошибки по readonly и типу


def test_serializer_serializes_instance(mocker):
    instance = mocker.Mock()
    instance.id = 10
    instance.message = 'Notification'
    instance.is_read = False

    serializer = NotificationSerializer(instance)
    data = serializer.data
    assert data['id'] == 10
    assert data['message'] == 'Notification'
    assert data['is_read'] is False
