"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from subscribe.models import Subscribe


def is_subscribed(subscribe_from_id: int, subscribe_to_id: int):
    try:
        Subscribe.objects.get(subscribe_from=subscribe_from_id, subscribe_to=subscribe_to_id)
    except Subscribe.DoesNotExist:
        return False
    else:
        return True
