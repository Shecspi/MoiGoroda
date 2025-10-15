from datetime import datetime

from subscribe.domain.entities import (
    Notification,
    SubscriptionRequest,
    Action,
    DeleteSubscriberRequest,
)
from subscribe.domain.interfaces import (
    AbstractNotificationRepository,
    AbstractUserRepository,
    AbstractShareSettingsRepository,
    AbstractSubscribeRepository,
)


class SubscriptionService:
    def __init__(
        self,
        user_repo: AbstractUserRepository,
        share_settings_repo: AbstractShareSettingsRepository,
        subscribe_repo: AbstractSubscribeRepository,
    ):
        self.user_repo = user_repo
        self.share_settings_repo = share_settings_repo
        self.subscribe_repo = subscribe_repo

    def save(
        self, request: SubscriptionRequest, current_user_id: int, is_superuser: bool
    ) -> dict[str, str]:
        if request.from_id != current_user_id:
            raise PermissionError('Нельзя оформлять подписки за других пользователей')

        if not self.user_repo.exists(request.from_id) or not self.user_repo.exists(request.to_id):
            raise ValueError('Передан неверный ID пользователя')

        if not self.share_settings_repo.can_subscribe(request.to_id) and not is_superuser:
            raise PermissionError('Пользователь не разрешил подписываться на него')

        if request.action == Action.subscribe:
            if not self.subscribe_repo.is_subscribed(request.from_id, request.to_id):
                self.subscribe_repo.add(request.from_id, request.to_id)
            return {'status': 'subscribed'}

        elif request.action == Action.unsubscribe:
            if self.subscribe_repo.is_subscribed(request.from_id, request.to_id):
                self.subscribe_repo.delete(request.from_id, request.to_id)
            return {'status': 'unsubscribed'}

    def delete_subscriber(
        self, request: DeleteSubscriberRequest, current_user_id: int
    ) -> dict[str, str]:
        if not self.user_repo.exists(request.user_id):
            raise ValueError('Передан неверный ID пользователя')

        if not self.subscribe_repo.check(request.user_id, current_user_id):
            raise PermissionError('Пользователь не подписан')

        self.subscribe_repo.delete(request.user_id, current_user_id)
        return {'status': 'success'}


class NotificationService:
    def __init__(self, repo: AbstractNotificationRepository):
        self.repo = repo

    def list_notifications(self, user_id: int) -> list[Notification]:
        return self.repo.list_for_user(user_id)

    def mark_notification_as_read(self, user_id: int, notification_id: int) -> Notification:
        notification = self.repo.get_for_user(user_id, notification_id)
        if not notification.read_at:
            notification.read_at = datetime.now()
            notification.is_read = True
            self.repo.update_read_status(notification)
        return notification

    def delete_notification(self, user_id: int, notification_id: int) -> None:
        self.repo.delete(user_id, notification_id)
