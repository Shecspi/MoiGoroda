"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from unittest.mock import MagicMock

import pytest
from django.contrib.auth.models import User

from premium.models import PremiumPlan, PremiumSubscription
from premium.services.checkout import CheckoutService


@pytest.mark.unit
@pytest.mark.django_db
class TestCheckoutService:
    """Тесты CheckoutService."""

    def test_create_checkout_success(
        self,
        user: User,
        premium_plan: PremiumPlan,
        mock_payment_provider: MagicMock,
    ) -> None:
        service = CheckoutService(payment_provider=mock_payment_provider)
        result = service.create_checkout(
            user=user,
            plan_id=str(premium_plan.pk),
            billing_period=PremiumSubscription.BillingPeriod.MONTHLY,
            return_url='https://site.com/return',
            promo_url='https://site.com/promo',
        )

        assert result.success is True
        assert result.redirect_url == 'https://yookassa.ru/confirm/test'
        assert result.payment_id is not None
        assert result.yookassa_payment_id == 'yookassa_test_123'

    def test_create_checkout_yearly(
        self,
        user: User,
        premium_plan: PremiumPlan,
        mock_payment_provider: MagicMock,
    ) -> None:
        service = CheckoutService(payment_provider=mock_payment_provider)
        result = service.create_checkout(
            user=user,
            plan_id=str(premium_plan.pk),
            billing_period=PremiumSubscription.BillingPeriod.YEARLY,
            return_url='https://site.com/return',
            promo_url='https://site.com/promo',
        )

        assert result.success is True
        mock_payment_provider.create_payment.assert_called_once()
        call_kwargs = mock_payment_provider.create_payment.call_args[1]
        assert call_kwargs['amount_value'] == '2990.00'

    def test_create_checkout_invalid_plan_returns_failure(
        self,
        user: User,
        mock_payment_provider: MagicMock,
    ) -> None:
        service = CheckoutService(payment_provider=mock_payment_provider)
        result = service.create_checkout(
            user=user,
            plan_id='00000000-0000-0000-0000-000000000000',
            billing_period=PremiumSubscription.BillingPeriod.MONTHLY,
            return_url='https://site.com/return',
            promo_url='https://site.com/promo',
        )

        assert result.success is False
        assert result.redirect_url == 'https://site.com/promo'
        mock_payment_provider.create_payment.assert_not_called()

    def test_create_checkout_provider_exception_returns_failure(
        self,
        user: User,
        premium_plan: PremiumPlan,
        mock_payment_provider: MagicMock,
    ) -> None:
        mock_payment_provider.create_payment.side_effect = Exception('API error')
        service = CheckoutService(payment_provider=mock_payment_provider)
        result = service.create_checkout(
            user=user,
            plan_id=str(premium_plan.pk),
            billing_period=PremiumSubscription.BillingPeriod.MONTHLY,
            return_url='https://site.com/return',
            promo_url='https://site.com/promo',
        )

        assert result.success is False
        assert result.redirect_url == 'https://site.com/promo'
