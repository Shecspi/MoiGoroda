from subscribe.infrastructure.django_repositories import DjangoNotificationRepository
from subscribe.application.services import NotificationService


def get_notification_service() -> NotificationService:
    repo = DjangoNotificationRepository()
    return NotificationService(repo)
