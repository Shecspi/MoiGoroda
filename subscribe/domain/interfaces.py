from abc import ABC, abstractmethod
from subscribe.domain.entities import Notification


class AbstractUserRepository(ABC):
    @abstractmethod
    def exists(self, user_id: int) -> bool: ...


class AbstractShareSettingsRepository(ABC):
    @abstractmethod
    def can_subscribe(self, user_id: int) -> bool: ...


class AbstractSubscribeRepository(ABC):
    @abstractmethod
    def is_subscribed(self, from_id: int, to_id: int) -> bool: ...

    @abstractmethod
    def add(self, from_id: int, to_id: int) -> None: ...

    @abstractmethod
    def delete(self, from_id: int, to_id: int) -> None: ...

    @abstractmethod
    def check(self, from_id: int, to_id: int) -> bool: ...

    @abstractmethod
    def get_all(self, from_id: int) -> list[dict]: ...


class AbstractNotificationRepository(ABC):
    @abstractmethod
    def list_for_user(self, user_id: int) -> list[Notification]: ...

    @abstractmethod
    def get_for_user(self, user_id: int, notification_id: int) -> Notification: ...

    @abstractmethod
    def delete(self, user_id: int, notification_id: int) -> None: ...

    @abstractmethod
    def update_read_status(self, notification: Notification) -> None: ...
