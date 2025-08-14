from subscribe.domain.entities import Notification
from subscribe.domain.repositories import AbstractNotificationRepository


class NotificationService:
    def __init__(self, repo: AbstractNotificationRepository):
        self.repo = repo

    def list_notifications(self, user_id: int) -> list[Notification]:
        return self.repo.list_for_user(user_id)

    def mark_notification_as_read(self, user_id: int, notification_id: int) -> Notification:
        return self.repo.mark_as_read(user_id, notification_id)

    def delete_notification(self, user_id: int, notification_id: int) -> None:
        self.repo.delete(user_id, notification_id)
