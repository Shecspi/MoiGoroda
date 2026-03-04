"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from decimal import Decimal

import pytest
from django.contrib.auth.models import User

from premium.models import (
    PremiumPayment,
    PremiumPaymentWebhookLog,
    PremiumPlan,
    PremiumPlanFeature,
    PremiumSubscription,
)


@pytest.mark.unit
@pytest.mark.django_db
class TestPremiumPlan:
    """Тесты модели PremiumPlan."""

    def test_str(self, premium_plan: PremiumPlan) -> None:
        assert str(premium_plan) == 'Базовый'

    def test_yearly_discount_percent_normal(self) -> None:
        """Скидка при годовой оплате рассчитывается корректно."""
        plan = PremiumPlan.objects.create(
            slug='test',
            name='Test',
            price_month=Decimal('100'),
            price_year=Decimal('1000'),
            currency='RUB',
        )
        # 12 * 100 = 1200, год 1000 -> скидка (1 - 1000/1200)*100 ≈ 16.67 -> 17
        assert plan.yearly_discount_percent == 17

    def test_yearly_discount_percent_zero_when_price_month_zero(self) -> None:
        plan = PremiumPlan.objects.create(
            slug='free',
            name='Free',
            price_month=Decimal('0'),
            price_year=Decimal('0'),
            currency='RUB',
        )
        assert plan.yearly_discount_percent == 0

    def test_yearly_discount_percent_no_discount(self) -> None:
        """Если годовая цена = 12*месячной, скидка 0."""
        plan = PremiumPlan.objects.create(
            slug='flat',
            name='Flat',
            price_month=Decimal('100'),
            price_year=Decimal('1200'),
            currency='RUB',
        )
        assert plan.yearly_discount_percent == 0

    def test_yearly_discount_percent_full_discount(self) -> None:
        """100% скидка при нулевой годовой цене (крайний случай)."""
        plan = PremiumPlan.objects.create(
            slug='special',
            name='Special',
            price_month=Decimal('100'),
            price_year=Decimal('0'),
            currency='RUB',
        )
        assert plan.yearly_discount_percent == 100


@pytest.mark.unit
@pytest.mark.django_db
class TestPremiumPlanFeature:
    """Тесты модели PremiumPlanFeature."""

    def test_str(self, premium_plan_feature: PremiumPlanFeature) -> None:
        assert str(premium_plan_feature) == 'Без рекламы'


@pytest.mark.unit
@pytest.mark.django_db
class TestPremiumSubscription:
    """Тесты модели PremiumSubscription."""

    def test_str(
        self,
        user: User,
        premium_plan: PremiumPlan,
    ) -> None:
        sub = PremiumSubscription.objects.create(
            user=user,
            plan=premium_plan,
            billing_period=PremiumSubscription.BillingPeriod.MONTHLY,
            status=PremiumSubscription.Status.PENDING,
        )
        assert 'testuser' in str(sub)
        assert 'Базовый' in str(sub)
        assert '1 месяц' in str(sub)

    def test_billing_period_choices(self) -> None:
        assert PremiumSubscription.BillingPeriod.MONTHLY.value == 'monthly'
        assert PremiumSubscription.BillingPeriod.YEARLY.value == 'yearly'

    def test_status_choices(self) -> None:
        assert PremiumSubscription.Status.PENDING.value == 'pending'
        assert PremiumSubscription.Status.ACTIVE.value == 'active'
        assert PremiumSubscription.Status.EXPIRED.value == 'expired'


@pytest.mark.unit
@pytest.mark.django_db
class TestPremiumPayment:
    """Тесты модели PremiumPayment."""

    def test_str(self, premium_payment: PremiumPayment) -> None:
        assert '22d6d597' in str(premium_payment)
        assert 'Ожидает оплаты' in str(premium_payment)

    def test_amount_property(self, premium_payment: PremiumPayment) -> None:
        assert premium_payment.amount == Decimal('299.00')


@pytest.mark.unit
@pytest.mark.django_db
class TestPremiumPaymentWebhookLog:
    """Тесты модели PremiumPaymentWebhookLog."""

    def test_str(
        self,
        premium_payment: PremiumPayment,
    ) -> None:
        log = PremiumPaymentWebhookLog.objects.create(
            payment=premium_payment,
            status='succeeded',
            raw_payload={'event': 'payment.succeeded'},
        )
        assert '22d6d597' in str(log)
        assert 'succeeded' in str(log)
