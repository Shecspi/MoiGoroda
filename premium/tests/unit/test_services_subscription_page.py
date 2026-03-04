"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth.models import User

from premium.models import PremiumPayment, PremiumSubscription
from premium.services.subscription_page import SubscriptionPageService


@pytest.mark.unit
@pytest.mark.django_db
class TestSubscriptionPageService:
    """Тесты SubscriptionPageService."""

    def test_get_page_data_no_payment_return(
        self,
        user: User,
    ) -> None:
        service = SubscriptionPageService()
        data = service.get_page_data(user, payment_return_id=None)
        assert data.payments == []
        assert data.active_subscription is None
        assert data.paused_subscriptions == []
        assert data.payment_result is None

    def test_get_page_data_with_active_subscription(
        self,
        user: User,
        active_subscription: PremiumSubscription,
    ) -> None:
        service = SubscriptionPageService()
        data = service.get_page_data(user, payment_return_id=None)
        assert data.active_subscription is not None
        assert data.active_subscription.pk == active_subscription.pk

    def test_get_page_data_with_payment_return_succeeded(
        self,
        user: User,
        premium_payment: PremiumPayment,
    ) -> None:
        premium_payment.status = PremiumPayment.Status.SUCCEEDED
        premium_payment.save()

        with patch(
            'premium.services.subscription_page._sync_pending_payments',
        ) as mock_sync:
            service = SubscriptionPageService()
            data = service.get_page_data(
                user,
                payment_return_id=str(premium_payment.pk),
            )
            mock_sync.assert_called_once_with(user)
            assert data.payment_result == 'succeeded'

    def test_get_page_data_with_payment_return_canceled(
        self,
        user: User,
        premium_payment: PremiumPayment,
    ) -> None:
        premium_payment.status = PremiumPayment.Status.CANCELED
        premium_payment.save()

        with patch(
            'premium.services.subscription_page._sync_pending_payments',
        ):
            service = SubscriptionPageService()
            data = service.get_page_data(
                user,
                payment_return_id=str(premium_payment.pk),
            )
            assert data.payment_result == 'canceled'

    def test_get_page_data_with_payment_return_pending(
        self,
        user: User,
        premium_payment: PremiumPayment,
    ) -> None:
        with patch(
            'premium.services.subscription_page._sync_pending_payments',
        ):
            service = SubscriptionPageService()
            data = service.get_page_data(
                user,
                payment_return_id=str(premium_payment.pk),
            )
            assert data.payment_result == 'pending'
