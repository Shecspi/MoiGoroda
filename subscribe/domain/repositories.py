from abc import ABC, abstractmethod
from subscribe.domain.entities import Notification


class AbstractNotificationRepository(ABC):
    @abstractmethod
    def list_for_user(self, user_id: int) -> list[Notification]:
        pass

    @abstractmethod
    def get_for_user(self, user_id: int, notification_id: int) -> Notification | None:
        pass

    @abstractmethod
    def mark_as_read(self, user_id: int, notification_id: int) -> Notification:
        pass

    @abstractmethod
    def delete(self, user_id: int, notification_id: int) -> None:
        pass
