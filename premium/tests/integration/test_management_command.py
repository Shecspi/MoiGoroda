"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from datetime import timedelta

import pytest
from django.core.management import call_command
from django.utils import timezone

from premium.models import PremiumPlan, PremiumSubscription


@pytest.mark.integration
@pytest.mark.django_db
class TestExpirePremiumSubscriptionsCommand:
    """Тесты команды expire_premium_subscriptions."""

    def test_expires_active_subscriptions(
        self,
        user,
        premium_plan: PremiumPlan,
    ) -> None:
        now = timezone.now()
        sub = PremiumSubscription.objects.create(
            user=user,
            plan=premium_plan,
            billing_period=PremiumSubscription.BillingPeriod.MONTHLY,
            status=PremiumSubscription.Status.ACTIVE,
            started_at=now - timedelta(days=40),
            expires_at=now - timedelta(days=10),
        )

        call_command('expire_premium_subscriptions')

        sub.refresh_from_db()
        assert sub.status == PremiumSubscription.Status.EXPIRED

    def test_activates_scheduled_when_active_expires(
        self,
        user,
        premium_plan: PremiumPlan,
    ) -> None:
        from django.conf import settings

        now = timezone.now()
        today = (
            timezone.localtime(now).date()
            if getattr(settings, 'USE_TZ', False)
            else now.date()
        )
        active = PremiumSubscription.objects.create(
            user=user,
            plan=premium_plan,
            billing_period=PremiumSubscription.BillingPeriod.MONTHLY,
            status=PremiumSubscription.Status.ACTIVE,
            started_at=now - timedelta(days=40),
            expires_at=now - timedelta(days=1),
        )
        scheduled = PremiumSubscription.objects.create(
            user=user,
            plan=premium_plan,
            billing_period=PremiumSubscription.BillingPeriod.MONTHLY,
            status=PremiumSubscription.Status.SCHEDULED,
            started_at=today,
            expires_at=now + timedelta(days=30),
        )

        call_command('expire_premium_subscriptions')

        active.refresh_from_db()
        scheduled.refresh_from_db()
        assert active.status == PremiumSubscription.Status.EXPIRED
        assert scheduled.status == PremiumSubscription.Status.ACTIVE

    def test_no_subscriptions_to_expire(self) -> None:
        call_command('expire_premium_subscriptions')
        # Не должно быть исключений
