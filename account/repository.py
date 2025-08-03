from account.dto import SubscribedUserDTO, SubscriberUserDTO
from subscribe.models import Subscribe


def get_subscribed_users(user_id: int) -> list[SubscribedUserDTO]:
    """
    Возвращает список пользователей, на которых подписан указанный в user_id пользователь

    Args:
        user_id (int): Идентификатор пользователя, для которого запрашиваются подписки

    Returns:
        list[SubscribedUserDTO]: Список DTO пользователей, на которых оформлена подписка
    """
    subscribed_users = Subscribe.objects.filter(subscribe_from_id=user_id)

    return [
        SubscribedUserDTO(id=user.subscribe_to.id, username=user.subscribe_to.username)
        for user in subscribed_users
    ]


def get_subscriber_users(user_id: int) -> list[SubscriberUserDTO]:
    """
    Возвращает список пользователей, которые подписаны на указанный в user_id пользователя

    Args:
        user_id (int): Идентификатор пользователя, для которого запрашиваются подписчики

    Returns:
        list[SubscribedUserDTO]: Список DTO пользователей, которые оформили подписку
    """
    subscribed_users = Subscribe.objects.filter(subscribe_to_id=user_id)

    return [
        SubscriberUserDTO(id=user.subscribe_from.id, username=user.subscribe_from.username)
        for user in subscribed_users
    ]
