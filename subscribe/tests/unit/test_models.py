"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import Any

import pytest
from django.contrib.auth.models import User
from django.db import IntegrityError

from subscribe.infrastructure.models import Subscribe, VisitedCityNotification


@pytest.mark.unit
@pytest.mark.django_db
class TestSubscribeModel:
    """Тесты для модели Subscribe"""

    def test_subscribe_str_representation(self) -> None:
        """Тест строкового представления подписки"""
        user1 = User.objects.create_user(username='user1', password='password1')
        user2 = User.objects.create_user(username='user2', password='password2')
        subscribe = Subscribe.objects.create(subscribe_from=user1, subscribe_to=user2)

        assert str(subscribe) == f'Подписка {user1} на {user2}'

    def test_subscribe_unique_together(self) -> None:
        """Тест уникальности пары подписчик-подписка"""
        user1 = User.objects.create_user(username='user1', password='password1')
        user2 = User.objects.create_user(username='user2', password='password2')

        Subscribe.objects.create(subscribe_from=user1, subscribe_to=user2)

        # Попытка создать дубликат должна вызвать ошибку
        with pytest.raises(IntegrityError):
            Subscribe.objects.create(subscribe_from=user1, subscribe_to=user2)

    def test_subscribe_allows_reverse_subscription(self) -> None:
        """Тест что можно создать обратную подписку"""
        user1 = User.objects.create_user(username='user1', password='password1')
        user2 = User.objects.create_user(username='user2', password='password2')

        # user1 подписывается на user2
        Subscribe.objects.create(subscribe_from=user1, subscribe_to=user2)

        # user2 подписывается на user1 - должно работать
        subscribe_reverse = Subscribe.objects.create(subscribe_from=user2, subscribe_to=user1)
        assert subscribe_reverse.id is not None

    def test_subscribe_cascade_delete_from_user(self) -> None:
        """Тест каскадного удаления при удалении подписчика"""
        user1 = User.objects.create_user(username='user1', password='password1')
        user2 = User.objects.create_user(username='user2', password='password2')
        subscribe = Subscribe.objects.create(subscribe_from=user1, subscribe_to=user2)

        user1.delete()

        # Подписка должна быть удалена
        assert not Subscribe.objects.filter(id=subscribe.id).exists()

    def test_subscribe_cascade_delete_to_user(self) -> None:
        """Тест каскадного удаления при удалении пользователя, на которого подписаны"""
        user1 = User.objects.create_user(username='user1', password='password1')
        user2 = User.objects.create_user(username='user2', password='password2')
        subscribe = Subscribe.objects.create(subscribe_from=user1, subscribe_to=user2)

        user2.delete()

        # Подписка должна быть удалена
        assert not Subscribe.objects.filter(id=subscribe.id).exists()

    def test_subscribe_related_names(self) -> None:
        """Тест работы related_name для связей"""
        user1 = User.objects.create_user(username='user1', password='password1')
        user2 = User.objects.create_user(username='user2', password='password2')
        user3 = User.objects.create_user(username='user3', password='password3')

        Subscribe.objects.create(subscribe_from=user1, subscribe_to=user2)
        Subscribe.objects.create(subscribe_from=user1, subscribe_to=user3)
        Subscribe.objects.create(subscribe_from=user3, subscribe_to=user1)

        # user1 подписан на 2 пользователей
        assert user1.subscribe_from_set.count() == 2

        # на user1 подписан 1 пользователь
        assert user1.subscribe_to_set.count() == 1

    def test_subscribe_meta_verbose_name(self) -> None:
        """Тест verbose_name модели"""
        assert Subscribe._meta.verbose_name == 'Подписка'
        assert Subscribe._meta.verbose_name_plural == 'Подписки'


@pytest.mark.unit
@pytest.mark.django_db
class TestVisitedCityNotificationModel:
    """Тесты для модели VisitedCityNotification"""

    def test_notification_default_values(
        self, test_country: Any, test_region_type: Any, test_region: Any, test_city: Any
    ) -> None:
        """Тест значений по умолчанию при создании уведомления"""
        sender = User.objects.create_user(username='sender', password='password1')
        recipient = User.objects.create_user(username='recipient', password='password2')

        notification = VisitedCityNotification.objects.create(
            recipient=recipient, sender=sender, city=test_city
        )

        assert notification.is_read is False
        assert notification.read_at is None
        assert notification.created_at is not None

    def test_notification_ordering(
        self, test_country: Any, test_region_type: Any, test_region: Any, test_city: Any
    ) -> None:
        """Тест сортировки уведомлений по дате создания (новые первыми)"""
        sender = User.objects.create_user(username='sender', password='password1')
        recipient = User.objects.create_user(username='recipient', password='password2')

        notif1 = VisitedCityNotification.objects.create(
            recipient=recipient, sender=sender, city=test_city
        )
        notif2 = VisitedCityNotification.objects.create(
            recipient=recipient, sender=sender, city=test_city
        )

        # Проверяем что последнее созданное уведомление идёт первым
        notifications = list(VisitedCityNotification.objects.all())
        assert notifications[0].id == notif2.id
        assert notifications[1].id == notif1.id

    def test_notification_cascade_delete_recipient(
        self, test_country: Any, test_region_type: Any, test_region: Any, test_city: Any
    ) -> None:
        """Тест каскадного удаления при удалении получателя"""
        sender = User.objects.create_user(username='sender', password='password1')
        recipient = User.objects.create_user(username='recipient', password='password2')

        notification = VisitedCityNotification.objects.create(
            recipient=recipient, sender=sender, city=test_city
        )

        recipient.delete()

        # Уведомление должно быть удалено
        assert not VisitedCityNotification.objects.filter(id=notification.id).exists()

    def test_notification_cascade_delete_sender(
        self, test_country: Any, test_region_type: Any, test_region: Any, test_city: Any
    ) -> None:
        """Тест каскадного удаления при удалении отправителя"""
        sender = User.objects.create_user(username='sender', password='password1')
        recipient = User.objects.create_user(username='recipient', password='password2')

        notification = VisitedCityNotification.objects.create(
            recipient=recipient, sender=sender, city=test_city
        )

        sender.delete()

        # Уведомление должно быть удалено
        assert not VisitedCityNotification.objects.filter(id=notification.id).exists()

    def test_notification_cascade_delete_city(
        self, test_country: Any, test_region_type: Any, test_region: Any, test_city: Any
    ) -> None:
        """Тест каскадного удаления при удалении города"""
        sender = User.objects.create_user(username='sender', password='password1')
        recipient = User.objects.create_user(username='recipient', password='password2')

        notification = VisitedCityNotification.objects.create(
            recipient=recipient, sender=sender, city=test_city
        )

        test_city.delete()

        # Уведомление должно быть удалено
        assert not VisitedCityNotification.objects.filter(id=notification.id).exists()

    def test_notification_related_names(
        self, test_country: Any, test_region_type: Any, test_region: Any, test_city: Any
    ) -> None:
        """Тест работы related_name для связей"""
        sender = User.objects.create_user(username='sender', password='password1')
        recipient = User.objects.create_user(username='recipient', password='password2')

        VisitedCityNotification.objects.create(recipient=recipient, sender=sender, city=test_city)
        VisitedCityNotification.objects.create(recipient=recipient, sender=sender, city=test_city)

        # У получателя 2 уведомления
        assert recipient.notifications.count() == 2

        # Отправитель отправил 2 уведомления
        assert sender.sent_notifications.count() == 2

    def test_notification_meta_verbose_name(self) -> None:
        """Тест verbose_name модели"""
        assert VisitedCityNotification._meta.verbose_name == 'Уведомление'
        assert VisitedCityNotification._meta.verbose_name_plural == 'Уведомления'

    def test_notification_read_status_update(
        self, test_country: Any, test_region_type: Any, test_region: Any, test_city: Any
    ) -> None:
        """Тест обновления статуса прочитанности"""
        from datetime import datetime

        sender = User.objects.create_user(username='sender', password='password1')
        recipient = User.objects.create_user(username='recipient', password='password2')

        notification = VisitedCityNotification.objects.create(
            recipient=recipient, sender=sender, city=test_city, is_read=False
        )

        # Помечаем как прочитанное
        read_time = datetime.now()
        notification.is_read = True
        notification.read_at = read_time
        notification.save()

        # Проверяем что изменения сохранились
        notification.refresh_from_db()
        assert notification.is_read is True
        assert notification.read_at is not None
