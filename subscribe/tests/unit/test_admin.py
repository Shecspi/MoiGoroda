"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import Any

import pytest
from django.contrib import admin
from django.contrib.auth.models import User

from subscribe.admin import SubscribeAdmin, VisitedCityNotificationAdmin
from subscribe.infrastructure.models import Subscribe, VisitedCityNotification


@pytest.mark.unit
class TestSubscribeAdmin:
    """Тесты для SubscribeAdmin"""

    def test_subscribe_admin_registered(self) -> None:
        """Тест что SubscribeAdmin зарегистрирован в админке"""
        assert admin.site.is_registered(Subscribe)

    def test_subscribe_admin_list_display(self) -> None:
        """Тест настройки list_display"""
        admin_instance = SubscribeAdmin(Subscribe, admin.site)
        assert admin_instance.list_display == ('id', 'subscribe_from', 'subscribe_to')

    def test_subscribe_admin_model_class(self) -> None:
        """Тест что используется правильная модель"""
        admin_instance = SubscribeAdmin(Subscribe, admin.site)
        assert admin_instance.model == Subscribe


@pytest.mark.unit
class TestVisitedCityNotificationAdmin:
    """Тесты для VisitedCityNotificationAdmin"""

    def test_notification_admin_registered(self) -> None:
        """Тест что VisitedCityNotificationAdmin зарегистрирован в админке"""
        assert admin.site.is_registered(VisitedCityNotification)

    def test_notification_admin_list_display(self) -> None:
        """Тест настройки list_display"""
        admin_instance = VisitedCityNotificationAdmin(VisitedCityNotification, admin.site)
        assert admin_instance.list_display == (
            'id',
            'recipient',
            'sender',
            'city',
            'is_read',
            'created_at',
            'read_at',
        )

    def test_notification_admin_model_class(self) -> None:
        """Тест что используется правильная модель"""
        admin_instance = VisitedCityNotificationAdmin(VisitedCityNotification, admin.site)
        assert admin_instance.model == VisitedCityNotification


@pytest.mark.unit
@pytest.mark.django_db
class TestSubscribeAdminIntegration:
    """Интеграционные тесты для SubscribeAdmin"""

    def test_subscribe_admin_displays_correct_fields(self) -> None:
        """Тест что админка отображает правильные поля для подписки"""
        user1 = User.objects.create_user(username='user1', password='password1')
        user2 = User.objects.create_user(username='user2', password='password2')
        subscribe = Subscribe.objects.create(subscribe_from=user1, subscribe_to=user2)

        admin_instance = SubscribeAdmin(Subscribe, admin.site)

        # Проверяем что все поля из list_display доступны
        for field in admin_instance.list_display:
            assert hasattr(subscribe, field)


@pytest.mark.unit
@pytest.mark.django_db
class TestVisitedCityNotificationAdminIntegration:
    """Интеграционные тесты для VisitedCityNotificationAdmin"""

    def test_notification_admin_displays_correct_fields(
        self, test_country: Any, test_region_type: Any, test_region: Any, test_city: Any
    ) -> None:
        """Тест что админка отображает правильные поля для уведомления"""
        sender = User.objects.create_user(username='sender', password='password1')
        recipient = User.objects.create_user(username='recipient', password='password2')
        notification = VisitedCityNotification.objects.create(
            recipient=recipient, sender=sender, city=test_city
        )

        admin_instance = VisitedCityNotificationAdmin(VisitedCityNotification, admin.site)

        # Проверяем что все поля из list_display доступны
        for field in admin_instance.list_display:
            assert hasattr(notification, field)
