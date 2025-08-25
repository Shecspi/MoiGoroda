from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from account.models import ShareSettings
from subscribe.domain.entities import Notification
from subscribe.domain.interfaces import (
    AbstractNotificationRepository,
    AbstractUserRepository,
    AbstractShareSettingsRepository,
    AbstractSubscribeRepository,
)
from subscribe.infrastructure.models import VisitedCityNotification
from subscribe.infrastructure.models import Subscribe


class DjangoUserRepository(AbstractUserRepository):
    def exists(self, user_id: int) -> bool:
        return User.objects.filter(pk=user_id).exists()


class DjangoShareSettingsRepository(AbstractShareSettingsRepository):
    def can_subscribe(self, user_id: int) -> bool:
        try:
            return ShareSettings.objects.get(user_id=user_id).can_subscribe
        except ShareSettings.DoesNotExist:
            return False


class DjangoSubscribeRepository(AbstractSubscribeRepository):
    def is_subscribed(self, from_id: int, to_id: int) -> bool:
        return Subscribe.objects.filter(subscribe_from_id=from_id, subscribe_to_id=to_id).exists()

    def add(self, from_id: int, to_id: int) -> None:
        Subscribe.objects.create(subscribe_from_id=from_id, subscribe_to_id=to_id)

    def delete(self, from_id: int, to_id: int) -> None:
        Subscribe.objects.filter(subscribe_from_id=from_id, subscribe_to_id=to_id).delete()

    def check(self, from_id: int, to_id: int) -> bool:
        return Subscribe.objects.filter(subscribe_from_id=from_id, subscribe_to_id=to_id).exists()

    def get_all(self, from_id: int):
        return [
            {'to_id': s.subscribe_to_id, 'username': s.subscribe_to.username}
            for s in Subscribe.objects.filter(subscribe_from_id=from_id).select_related(
                'subscribe_to'
            )
        ]


class DjangoNotificationRepository(AbstractNotificationRepository):
    """
    Репозиторий для работы с уведомлениями через Django ORM.

    Отвечает за преобразование Django-моделей `VisitedCityNotification`
    в доменные сущности `Notification` и выполнение CRUD-операций
    с учётом бизнес-ограничений (например, доступ только к своим уведомлениям).
    """

    def list_for_user(self, user_id: int) -> list[Notification]:
        """
        Вернуть список уведомлений пользователя.

        Уведомления сортируются так, чтобы непрочитанные шли первыми,
        а затем по убыванию ID (новые сверху).

        Args:
            user_id (int): ID пользователя (получателя уведомлений).

        Returns:
            list[Notification]: Список уведомлений пользователя.
        """
        qs = (
            VisitedCityNotification.objects.filter(recipient_id=user_id)
            .select_related('sender', 'city__region', 'city__country')
            .order_by('is_read', '-id')
        )
        return [self._to_entity(obj) for obj in qs]

    def get_for_user(self, user_id: int, notification_id: int) -> Notification:
        """
        Получить уведомление пользователя по его ID.

        Args:
            user_id (int): ID пользователя (получателя уведомления).
            notification_id (int): ID уведомления.

        Returns:
            Notification: Уведомление в виде доменной сущности.
                          Если не найдено, будет вызвано исключение 404.
        """
        obj = get_object_or_404(
            VisitedCityNotification.objects.filter(recipient_id=user_id).select_related(
                'sender', 'city__region', 'city__country'
            ),
            id=notification_id,
        )
        return self._to_entity(obj)

    def delete(self, user_id: int, notification_id: int) -> None:
        """
        Удалить уведомление пользователя.

        Args:
            user_id (int): ID пользователя (получателя уведомления).
            notification_id (int): ID уведомления.

        Raises:
            Http404: Если уведомление не найдено.
        """
        obj = get_object_or_404(
            VisitedCityNotification.objects.filter(recipient_id=user_id), id=notification_id
        )
        obj.delete()

    def update_read_status(self, notification: Notification) -> None:
        """
        Обновить статус прочитанности уведомления.

        Args:
            notification (Notification): Доменная сущность уведомления,
                                         в которой выставлены новые значения
                                         `read_at` и `is_read`.
        """
        obj = VisitedCityNotification.objects.get(pk=notification.id)
        obj.read_at = notification.read_at
        obj.is_read = notification.is_read
        obj.save(update_fields=['read_at', 'is_read'])

    def _to_entity(self, obj: VisitedCityNotification) -> Notification:
        """
        Преобразовать Django-модель в доменную сущность.

        Args:
            obj (VisitedCityNotification): Django ORM-объект.

        Returns:
            Notification: Доменная сущность уведомления.
        """
        return Notification(
            id=obj.id,
            city_id=obj.city_id,
            city_title=obj.city.title,
            region_id=obj.city.region.id,
            region_title=obj.city.region.full_name,
            country_code=obj.city.country.code,
            country_title=obj.city.country.name,
            is_read=obj.is_read,
            sender_id=obj.sender_id,
            sender_username=obj.sender.username,
            read_at=obj.read_at,
        )
