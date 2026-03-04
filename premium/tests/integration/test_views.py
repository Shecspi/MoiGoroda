"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from premium.models import PremiumPlan, PremiumSubscription


@pytest.mark.integration
@pytest.mark.django_db
class TestPromoView:
    """Тесты view promo."""

    def test_promo_anonymous_returns_200(self) -> None:
        client = Client()
        response = client.get(reverse('premium_promo'))
        assert response.status_code == 200
        assert 'premium/promo.html' in [t.name for t in response.templates]

    def test_promo_authenticated_with_plans(
        self,
        user: User,
        premium_plan: PremiumPlan,
    ) -> None:
        client = Client()
        client.force_login(user)
        response = client.get(reverse('premium_promo'))
        assert response.status_code == 200
        assert 'plans' in response.context
        assert list(response.context['plans']) == [premium_plan]


@pytest.mark.integration
@pytest.mark.django_db
class TestCheckoutView:
    """Тесты view checkout."""

    def test_checkout_requires_login(self) -> None:
        client = Client()
        response = client.post(
            reverse('premium_checkout'),
            {'plan_id': 'x', 'billing_period': 'monthly'},
        )
        assert response.status_code == 302
        assert 'signin' in response.url or 'login' in response.url

    def test_checkout_requires_post(self, user: User) -> None:
        client = Client()
        client.force_login(user)
        response = client.get(reverse('premium_checkout'))
        assert response.status_code == 405

    @patch('premium.views.CheckoutService')
    def test_checkout_success_redirects(
        self,
        mock_service_class: MagicMock,
        user: User,
        premium_plan: PremiumPlan,
    ) -> None:
        from premium.dto import CheckoutResult

        mock_result = CheckoutResult(
            success=True,
            redirect_url='https://yookassa.ru/pay',
            payment_id='uuid-123',
            yookassa_payment_id='yk-123',
            yookassa_status='pending',
            raw_response={'id': 'yk-123'},
        )
        mock_service_class.return_value.create_checkout.return_value = mock_result

        client = Client()
        client.force_login(user)
        response = client.post(
            reverse('premium_checkout'),
            {
                'plan_id': str(premium_plan.pk),
                'billing_period': PremiumSubscription.BillingPeriod.MONTHLY,
            },
        )

        assert response.status_code == 302
        assert response.url == 'https://yookassa.ru/pay'

    @patch('premium.views.CheckoutService')
    def test_checkout_invalid_billing_period_redirects_to_promo(
        self,
        mock_service_class: MagicMock,
        user: User,
        premium_plan: PremiumPlan,
    ) -> None:
        client = Client()
        client.force_login(user)
        response = client.post(
            reverse('premium_checkout'),
            {
                'plan_id': str(premium_plan.pk),
                'billing_period': 'invalid',
            },
        )
        assert response.status_code == 302
        assert reverse('premium_promo') in response.url


@pytest.mark.integration
@pytest.mark.django_db
class TestSuccessView:
    """Тесты view success."""

    def test_success_returns_200(self) -> None:
        client = Client()
        response = client.get(reverse('premium_success'))
        assert response.status_code == 200
        assert 'premium/success.html' in [t.name for t in response.templates]


@pytest.mark.integration
@pytest.mark.django_db
class TestMySubscriptionView:
    """Тесты view my_subscription."""

    def test_my_subscription_requires_login(self) -> None:
        client = Client()
        response = client.get(reverse('premium_my_subscription'))
        assert response.status_code == 302

    def test_my_subscription_returns_200(
        self,
        user: User,
    ) -> None:
        client = Client()
        client.force_login(user)
        response = client.get(reverse('premium_my_subscription'))
        assert response.status_code == 200
        assert 'premium/my_subscription.html' in [t.name for t in response.templates]
        assert 'payments' in response.context
        assert 'active_subscription' in response.context
