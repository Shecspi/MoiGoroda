from subscribe.infrastructure.django_repository import DjangoNotificationRepository
from subscribe.application.services import NotificationService


def get_notification_service() -> NotificationService:
    repo = DjangoNotificationRepository()
    return NotificationService(repo)
