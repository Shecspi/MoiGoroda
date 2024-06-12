"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from account.models import ShareSettings
from subscribe.models import Subscribe


def is_subscribed(subscribe_from_id: int, subscribe_to_id: int):
    try:
        Subscribe.objects.get(subscribe_from=subscribe_from_id, subscribe_to=subscribe_to_id)
    except Subscribe.DoesNotExist:
        return False
    else:
        return True


def can_subscribe(to_id: int):
    try:
        return ShareSettings.objects.get(user_id=to_id).can_subscribe
    except ShareSettings.DoesNotExist:
        return False
