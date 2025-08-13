import pytest

from subscribe.serializers import NotificationSerializer


@pytest.mark.parametrize(
    'input_data,expected',
    [
        ({'is_read': True}, {'is_read': True}),
        ({'is_read': False}, {'is_read': False}),
        ({'is_read': True, 'sender': 999, 'city': 888}, {'is_read': True}),
    ],
)
def test_serializer_accepts_only_is_read(input_data, expected):
    serializer = NotificationSerializer(data=input_data)
    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data == expected


def test_serializer_missing_is_read():
    """
    Если is_read не передан, сериализатор всё равно валиден
    и просто возвращает пустые validated_data.
    """
    serializer = NotificationSerializer(data={})
    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data == {}


def test_serializer_invalid_type_for_is_read():
    """
    Если is_read неправильного типа, сериализатор невалиден.
    """
    serializer = NotificationSerializer(data={'is_read': 'fdsfsdfs'})
    assert not serializer.is_valid()
    assert 'is_read' in serializer.errors
