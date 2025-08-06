from dataclasses import dataclass


@dataclass
class SubscribedUserDTO:
    """
    Пользователь, на которого оформлена подписка
    """

    id: int
    username: str


@dataclass
class SubscriberUserDTO:
    """
    Пользователь, который оформил подписку
    """

    id: int
    username: str
    can_subscribe: bool
