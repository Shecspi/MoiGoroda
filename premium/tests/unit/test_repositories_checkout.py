"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from decimal import Decimal

import pytest
from django.contrib.auth.models import User

from premium.models import PremiumPayment, PremiumPlan, PremiumSubscription
from premium.repositories.checkout import CheckoutRepository


@pytest.mark.unit
@pytest.mark.django_db
class TestCheckoutRepository:
    """Тесты CheckoutRepository."""

    def test_get_plan_by_id_returns_plan(
        self,
        premium_plan: PremiumPlan,
    ) -> None:
        repo = CheckoutRepository()
        plan = repo.get_plan_by_id(str(premium_plan.pk))
        assert plan is not None
        assert plan.pk == premium_plan.pk
        assert plan.slug == 'basic'

    def test_get_plan_by_id_returns_none_for_invalid_id(self) -> None:
        repo = CheckoutRepository()
        assert repo.get_plan_by_id('00000000-0000-0000-0000-000000000000') is None
        assert repo.get_plan_by_id('not-a-uuid') is None

    def test_get_plan_by_id_returns_none_for_inactive_plan(
        self,
        premium_plan: PremiumPlan,
    ) -> None:
        premium_plan.is_active = False
        premium_plan.save()
        repo = CheckoutRepository()
        assert repo.get_plan_by_id(str(premium_plan.pk)) is None

    def test_create_subscription(
        self,
        user: User,
        premium_plan: PremiumPlan,
    ) -> None:
        repo = CheckoutRepository()
        sub = repo.create_subscription(
            user=user,
            plan=premium_plan,
            billing_period=PremiumSubscription.BillingPeriod.MONTHLY,
            provider_payment_id='yk-123',
        )
        assert sub.user == user
        assert sub.plan == premium_plan
        assert sub.billing_period == PremiumSubscription.BillingPeriod.MONTHLY
        assert sub.status == PremiumSubscription.Status.PENDING
        assert sub.provider_payment_id == 'yk-123'

    def test_create_payment(
        self,
        user: User,
        subscription: PremiumSubscription,
        premium_plan: PremiumPlan,
    ) -> None:
        repo = CheckoutRepository()
        payment = repo.create_payment(
            user=user,
            subscription=subscription,
            plan=premium_plan,
            amount_value=Decimal('299.00'),
            currency='RUB',
            billing_period=PremiumSubscription.BillingPeriod.MONTHLY,
            description='Test payment',
            yookassa_payment_id='yk-456',
            confirmation_url='https://pay.ru',
            status='pending',
        )
        assert payment.user == user
        assert payment.subscription == subscription
        assert payment.plan == premium_plan
        assert payment.yookassa_payment_id == 'yk-456'
        assert payment.amount_value == Decimal('299.00')
        assert payment.status == PremiumPayment.Status.PENDING

    def test_create_webhook_log(
        self,
        premium_payment: PremiumPayment,
    ) -> None:
        repo = CheckoutRepository()
        log = repo.create_webhook_log(
            payment=premium_payment,
            status='succeeded',
            raw_payload={'event': 'payment.succeeded'},
        )
        assert log.payment == premium_payment
        assert log.status == 'succeeded'
        assert log.raw_payload == {'event': 'payment.succeeded'}
