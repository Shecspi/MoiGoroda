from django.contrib.auth.models import User

from premium.models import PremiumSubscription


def has_advanced_premium(user: User) -> bool:
    return PremiumSubscription.objects.filter(
        user=user,
        status=PremiumSubscription.Status.ACTIVE,
        plan__slug='advanced',
    ).exists()
