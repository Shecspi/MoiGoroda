"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.contrib.auth.models import User

from account.models import ShareSettings
from subscribe.models import Subscribe


def is_user_exists(id: int) -> bool:
    try:
        User.objects.get(pk=id)
    except User.DoesNotExist:
        return False
    else:
        return True


def is_user_has_subscriptions(from_id: int) -> bool:
    return Subscribe.objects.filter(subscribe_from=from_id).exists()


def is_subscribed(subscribe_from_id: int, subscribe_to_id: int) -> bool:
    try:
        Subscribe.objects.get(subscribe_from=subscribe_from_id, subscribe_to=subscribe_to_id)
    except Subscribe.DoesNotExist:
        return False
    else:
        return True


def can_subscribe(to_id: int) -> bool:
    try:
        return ShareSettings.objects.get(user_id=to_id).can_subscribe
    except ShareSettings.DoesNotExist:
        return False


def add_subscription(from_id: int, to_id: int) -> None:
    Subscribe.objects.create(subscribe_from_id=from_id, subscribe_to=User.objects.get(pk=to_id))


def delete_subscription(from_id: int, to_id: int) -> None:
    Subscribe.objects.get(subscribe_from_id=from_id, subscribe_to_id=to_id).delete()


def check_subscription(from_id: int, to_id: int) -> bool:
    return Subscribe.objects.filter(subscribe_from=from_id, subscribe_to=to_id).exists()


def get_all_subscriptions(from_id: int) -> list:
    subscriptions = Subscribe.objects.filter(subscribe_from_id=from_id)

    return [
        {
            'to_id': subscription.subscribe_to_id,
            'username': User.objects.get(pk=subscription.subscribe_to_id).username,
        }
        for subscription in subscriptions
    ]
