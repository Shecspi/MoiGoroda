from datetime import datetime

from django import template
from advertisement.models import AdvertisementException

register = template.Library()


@register.simple_tag
def get_excluded_users():
    user_ids = tuple(
        AdvertisementException.objects.filter(deadline__gte=datetime.now()).values_list(
            'user__id', flat=True
        )
    )
    return user_ids
