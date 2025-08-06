from account.dto import SubscribedUserDTO, SubscriberUserDTO
from account.models import ShareSettings
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

    result = []

    for subscribe in subscribed_users:
        share_settings = ShareSettings.objects.filter(user=subscribe.subscribe_from)

        result.append(
            SubscriberUserDTO(
                id=subscribe.subscribe_from.id,
                username=subscribe.subscribe_from.username,
                can_subscribe=share_settings.can_share if share_settings.exists() else False,
            )
        )

    return result
