"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.contrib.auth.models import User

from subscribe.infrastructure.models import Subscribe


def is_user_has_subscriptions(from_id: int) -> bool:
    return Subscribe.objects.filter(subscribe_from=from_id).exists()


def is_subscribed(subscribe_from_id: int, subscribe_to_id: int) -> bool:
    try:
        Subscribe.objects.get(subscribe_from=subscribe_from_id, subscribe_to=subscribe_to_id)
    except Subscribe.DoesNotExist:
        return False
    else:
        return True


def get_all_subscriptions(from_id: int) -> list[dict[str, int | str]]:
    subscriptions = Subscribe.objects.filter(subscribe_from_id=from_id)

    return [
        {
            'to_id': subscription.subscribe_to_id,
            'username': User.objects.get(pk=subscription.subscribe_to_id).username,
        }
        for subscription in subscriptions
    ]
