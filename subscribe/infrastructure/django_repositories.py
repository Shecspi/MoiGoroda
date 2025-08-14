from datetime import datetime
from django.shortcuts import get_object_or_404
from subscribe.domain.entities import Notification
from subscribe.domain.repositories import AbstractNotificationRepository
from subscribe.models import VisitedCityNotification


class DjangoNotificationRepository(AbstractNotificationRepository):
    def list_for_user(self, user_id: int) -> list[Notification]:
        qs = (
            VisitedCityNotification.objects.filter(recipient_id=user_id)
            .select_related('sender', 'city__region', 'city__country')
            .order_by('is_read', '-id')
        )
        return [self._to_entity(obj) for obj in qs]

    def get_for_user(self, user_id: int, notification_id: int) -> Notification | None:
        obj = get_object_or_404(
            VisitedCityNotification.objects.filter(recipient_id=user_id).select_related(
                'sender', 'city__region', 'city__country'
            ),
            id=notification_id,
        )
        return self._to_entity(obj)

    def mark_as_read(self, user_id: int, notification_id: int) -> Notification:
        obj = get_object_or_404(
            VisitedCityNotification.objects.filter(recipient_id=user_id), id=notification_id
        )
        if not obj.read_at:
            obj.read_at = datetime.now()
            obj.is_read = True
            obj.save(update_fields=['read_at', 'is_read'])
        return self._to_entity(obj)

    def delete(self, user_id: int, notification_id: int) -> None:
        obj = get_object_or_404(
            VisitedCityNotification.objects.filter(recipient_id=user_id), id=notification_id
        )
        obj.delete()

    def _to_entity(self, obj: VisitedCityNotification) -> Notification:
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
