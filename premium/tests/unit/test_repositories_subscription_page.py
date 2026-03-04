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

from premium.models import PremiumPayment, PremiumPlan, PremiumSubscription
from premium.repositories.subscription_page import SubscriptionPageRepository


@pytest.mark.unit
@pytest.mark.django_db
class TestSubscriptionPageRepository:
    """Тесты SubscriptionPageRepository."""

    def test_get_payments_for_user(
        self,
        user: User,
        premium_payment: PremiumPayment,
    ) -> None:
        repo = SubscriptionPageRepository()
        payments = repo.get_payments_for_user(user)
        assert len(payments) == 1
        assert payments[0].pk == premium_payment.pk

    def test_get_payments_for_user_empty(self, user: User) -> None:
        repo = SubscriptionPageRepository()
        assert repo.get_payments_for_user(user) == []

    def test_get_active_subscription(
        self,
        user: User,
        active_subscription: PremiumSubscription,
    ) -> None:
        repo = SubscriptionPageRepository()
        sub = repo.get_active_subscription(user)
        assert sub is not None
        assert sub.pk == active_subscription.pk
        assert sub.status == PremiumSubscription.Status.ACTIVE

    def test_get_active_subscription_none(self, user: User) -> None:
        repo = SubscriptionPageRepository()
        assert repo.get_active_subscription(user) is None

    def test_get_paused_subscriptions_empty_when_no_active(
        self,
        user: User,
    ) -> None:
        repo = SubscriptionPageRepository()
        assert repo.get_paused_subscriptions(user, None) == []

    def test_get_paused_subscriptions_empty_when_active_no_expires(
        self,
        user: User,
        premium_plan: PremiumPlan,
    ) -> None:
        now = timezone.now()
        active = PremiumSubscription.objects.create(
            user=user,
            plan=premium_plan,
            billing_period=PremiumSubscription.BillingPeriod.MONTHLY,
            status=PremiumSubscription.Status.ACTIVE,
            started_at=now,
            expires_at=None,
        )
        repo = SubscriptionPageRepository()
        assert repo.get_paused_subscriptions(user, active) == []

    def test_get_paused_subscriptions_returns_scheduled(
        self,
        user: User,
        premium_plan: PremiumPlan,
    ) -> None:
        now = timezone.now()
        active = PremiumSubscription.objects.create(
            user=user,
            plan=premium_plan,
            billing_period=PremiumSubscription.BillingPeriod.MONTHLY,
            status=PremiumSubscription.Status.ACTIVE,
            started_at=now,
            expires_at=now + timedelta(days=10),
        )
        scheduled = PremiumSubscription.objects.create(
            user=user,
            plan=premium_plan,
            billing_period=PremiumSubscription.BillingPeriod.MONTHLY,
            status=PremiumSubscription.Status.SCHEDULED,
            started_at=now + timedelta(days=11),
            expires_at=now + timedelta(days=41),
        )
        repo = SubscriptionPageRepository()
        result = repo.get_paused_subscriptions(user, active)
        assert len(result) == 1
        sub, start, end = result[0]
        assert sub.pk == scheduled.pk
        assert start <= end

    def test_get_payment_by_id_and_user(
        self,
        user: User,
        premium_payment: PremiumPayment,
    ) -> None:
        repo = SubscriptionPageRepository()
        payment = repo.get_payment_by_id_and_user(str(premium_payment.pk), user)
        assert payment is not None
        assert payment.pk == premium_payment.pk

    def test_get_payment_by_id_and_user_none_for_wrong_user(
        self,
        premium_payment: PremiumPayment,
        django_user_model: type[User],
    ) -> None:
        other_user = django_user_model.objects.create_user(
            username='other',
            password='pass',
        )
        repo = SubscriptionPageRepository()
        assert repo.get_payment_by_id_and_user(str(premium_payment.pk), other_user) is None
