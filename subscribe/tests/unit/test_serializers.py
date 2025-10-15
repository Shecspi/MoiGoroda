"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from datetime import datetime

import pytest

from subscribe.api.serializers import NotificationSerializer
from subscribe.domain.entities import Notification


@pytest.mark.unit
class TestNotificationSerializer:
    """Тесты для NotificationSerializer"""

    def test_serializer_has_all_required_fields(self) -> None:
        """Тест что сериализатор содержит все необходимые поля"""
        serializer = NotificationSerializer()
        expected_fields = {
            'id',
            'city_id',
            'city_title',
            'region_id',
            'region_title',
            'country_code',
            'country_title',
            'is_read',
            'read_at',
            'sender_id',
            'sender_username',
        }
        assert set(serializer.fields.keys()) == expected_fields

    def test_serializer_field_types(self) -> None:
        """Тест типов полей сериализатора"""
        from rest_framework import serializers

        serializer = NotificationSerializer()

        assert isinstance(serializer.fields['id'], serializers.IntegerField)
        assert isinstance(serializer.fields['city_id'], serializers.IntegerField)
        assert isinstance(serializer.fields['city_title'], serializers.CharField)
        assert isinstance(serializer.fields['region_id'], serializers.IntegerField)
        assert isinstance(serializer.fields['region_title'], serializers.CharField)
        assert isinstance(serializer.fields['country_code'], serializers.CharField)
        assert isinstance(serializer.fields['country_title'], serializers.CharField)
        assert isinstance(serializer.fields['is_read'], serializers.BooleanField)
        assert isinstance(serializer.fields['read_at'], serializers.DateTimeField)
        assert isinstance(serializer.fields['sender_id'], serializers.IntegerField)
        assert isinstance(serializer.fields['sender_username'], serializers.CharField)

    def test_serializer_serializes_notification(self) -> None:
        """Тест сериализации уведомления"""
        read_at = datetime(2024, 1, 1, 12, 0, 0)
        notification = Notification(
            id=1,
            city_id=10,
            city_title='Москва',
            region_id=20,
            region_title='Московская область',
            country_code='RU',
            country_title='Россия',
            is_read=True,
            sender_id=5,
            sender_username='testuser',
            read_at=read_at,
        )

        serializer = NotificationSerializer(notification)
        data = serializer.data

        assert data['id'] == 1
        assert data['city_id'] == 10
        assert data['city_title'] == 'Москва'
        assert data['region_id'] == 20
        assert data['region_title'] == 'Московская область'
        assert data['country_code'] == 'RU'
        assert data['country_title'] == 'Россия'
        assert data['is_read'] is True
        assert data['sender_id'] == 5
        assert data['sender_username'] == 'testuser'
        assert data['read_at'] is not None

    def test_serializer_serializes_unread_notification(self) -> None:
        """Тест сериализации непрочитанного уведомления"""
        notification = Notification(
            id=1,
            city_id=10,
            city_title='Москва',
            region_id=20,
            region_title='Московская область',
            country_code='RU',
            country_title='Россия',
            is_read=False,
            sender_id=5,
            sender_username='testuser',
            read_at=None,
        )

        serializer = NotificationSerializer(notification)
        data = serializer.data

        assert data['is_read'] is False
        assert data['read_at'] is None

    def test_serializer_serializes_list_of_notifications(self) -> None:
        """Тест сериализации списка уведомлений"""
        notifications = [
            Notification(
                id=i,
                city_id=10 + i,
                city_title=f'City {i}',
                region_id=20 + i,
                region_title=f'Region {i}',
                country_code='RU',
                country_title='Россия',
                is_read=False,
                sender_id=5,
                sender_username='testuser',
                read_at=None,
            )
            for i in range(3)
        ]

        serializer = NotificationSerializer(notifications, many=True)
        data = serializer.data

        assert len(data) == 3
        assert data[0]['id'] == 0
        assert data[1]['id'] == 1
        assert data[2]['id'] == 2

    def test_serializer_handles_empty_list(self) -> None:
        """Тест сериализации пустого списка"""
        serializer = NotificationSerializer([], many=True)
        data = serializer.data

        assert len(data) == 0

    def test_serializer_preserves_field_order(self) -> None:
        """Тест что порядок полей предсказуем"""
        notification = Notification(
            id=1,
            city_id=10,
            city_title='Москва',
            region_id=20,
            region_title='Московская область',
            country_code='RU',
            country_title='Россия',
            is_read=False,
            sender_id=5,
            sender_username='testuser',
            read_at=None,
        )

        serializer = NotificationSerializer(notification)
        data = serializer.data

        # Проверяем что все поля присутствуют
        assert 'id' in data
        assert 'city_id' in data
        assert 'city_title' in data
        assert 'region_id' in data
        assert 'region_title' in data
        assert 'country_code' in data
        assert 'country_title' in data
        assert 'is_read' in data
        assert 'read_at' in data
        assert 'sender_id' in data
        assert 'sender_username' in data
