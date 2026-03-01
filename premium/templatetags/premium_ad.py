"""
Теги для отображения рекламы с учётом премиум-подписки.
"""

from django import template
from django.http import HttpRequest

from premium.models import PremiumSubscription

register = template.Library()

_CACHE_ATTR = '_has_active_premium'


@register.simple_tag
def get_has_active_premium(request: HttpRequest | None) -> bool:
    """
    Возвращает True, если у пользователя есть активная премиум-подписка.
    Результат кешируется в request на время запроса.
    """
    if request is None or not request.user.is_authenticated:
        return False
    cached = getattr(request, _CACHE_ATTR, None)
    if cached is not None:
        return bool(cached)
    value = PremiumSubscription.objects.filter(
        user=request.user,
        status=PremiumSubscription.Status.ACTIVE,
    ).exists()
    setattr(request, _CACHE_ATTR, value)
    return value
