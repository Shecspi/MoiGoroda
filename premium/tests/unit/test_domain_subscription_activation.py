"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from datetime import timedelta

import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from premium.domain.subscription_activation import activate_subscription_on_payment_success
from premium.models import PremiumPlan, PremiumSubscription


@pytest.fixture
def subscription(
    user: User,
    premium_plan: PremiumPlan,
) -> PremiumSubscription:
    """Подписка в статусе PENDING."""
    return PremiumSubscription.objects.create(
        user=user,
        plan=premium_plan,
        billing_period=PremiumSubscription.BillingPeriod.MONTHLY,
        status=PremiumSubscription.Status.PENDING,
        provider_payment_id='yookassa_123',
    )


@pytest.mark.unit
@pytest.mark.django_db
class TestActivateSubscriptionOnPaymentSuccess:
    """Тесты activate_subscription_on_payment_success."""

    def test_returns_false_when_not_pending(
        self,
        subscription: PremiumSubscription,
    ) -> None:
        subscription.status = PremiumSubscription.Status.ACTIVE
        subscription.save()
        assert activate_subscription_on_payment_success(subscription) is False

    def test_activates_when_no_old_active(
        self,
        subscription: PremiumSubscription,
    ) -> None:
        result = activate_subscription_on_payment_success(subscription)
        assert result is True
        subscription.refresh_from_db()
        assert subscription.status == PremiumSubscription.Status.ACTIVE
        assert subscription.started_at is not None
        assert subscription.expires_at is not None

    def test_renewal_when_same_plan_price(
        self,
        user: User,
        premium_plan: PremiumPlan,
    ) -> None:
        now = timezone.now()
        old_active = PremiumSubscription.objects.create(
            user=user,
            plan=premium_plan,
            billing_period=PremiumSubscription.BillingPeriod.MONTHLY,
            status=PremiumSubscription.Status.ACTIVE,
            started_at=now - timedelta(days=10),
            expires_at=now + timedelta(days=20),
        )
        new_sub = PremiumSubscription.objects.create(
            user=user,
            plan=premium_plan,
            billing_period=PremiumSubscription.BillingPeriod.MONTHLY,
            status=PremiumSubscription.Status.PENDING,
        )

        result = activate_subscription_on_payment_success(new_sub)
        assert result is True

        old_active.refresh_from_db()
        new_sub.refresh_from_db()
        # Старая подписка продлена, новая отменена
        assert old_active.status == PremiumSubscription.Status.ACTIVE
        assert new_sub.status == PremiumSubscription.Status.CANCELED

    def test_upgrade_when_new_plan_more_expensive(
        self,
        user: User,
        premium_plan: PremiumPlan,
        premium_plan_cheap: PremiumPlan,
    ) -> None:
        now = timezone.now()
        # Старая активная — дешёвый план
        old_active = PremiumSubscription.objects.create(
            user=user,
            plan=premium_plan_cheap,
            billing_period=PremiumSubscription.BillingPeriod.MONTHLY,
            status=PremiumSubscription.Status.ACTIVE,
            started_at=now - timedelta(days=10),
            expires_at=now + timedelta(days=20),
        )
        # Новая — дорогой план
        new_sub = PremiumSubscription.objects.create(
            user=user,
            plan=premium_plan,
            billing_period=PremiumSubscription.BillingPeriod.MONTHLY,
            status=PremiumSubscription.Status.PENDING,
        )

        result = activate_subscription_on_payment_success(new_sub)
        assert result is True

        old_active.refresh_from_db()
        new_sub.refresh_from_db()
        assert old_active.status == PremiumSubscription.Status.INTERRUPTED
        assert new_sub.status == PremiumSubscription.Status.ACTIVE

    def test_downgrade_when_new_plan_cheaper(
        self,
        user: User,
        premium_plan: PremiumPlan,
        premium_plan_cheap: PremiumPlan,
    ) -> None:
        now = timezone.now()
        PremiumSubscription.objects.create(
            user=user,
            plan=premium_plan,
            billing_period=PremiumSubscription.BillingPeriod.MONTHLY,
            status=PremiumSubscription.Status.ACTIVE,
            started_at=now - timedelta(days=10),
            expires_at=now + timedelta(days=20),
        )
        new_sub = PremiumSubscription.objects.create(
            user=user,
            plan=premium_plan_cheap,
            billing_period=PremiumSubscription.BillingPeriod.MONTHLY,
            status=PremiumSubscription.Status.PENDING,
        )

        result = activate_subscription_on_payment_success(new_sub)
        assert result is True

        new_sub.refresh_from_db()
        # Новая добавляется в цепочку SCHEDULED
        assert new_sub.status == PremiumSubscription.Status.SCHEDULED
