# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

from datetime import timedelta

from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from django.utils import timezone

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
        redirect_url = response.get('Location', '')
        assert 'signin' in redirect_url or 'login' in redirect_url

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
        assert response.get('Location') == 'https://yookassa.ru/pay'

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
        assert reverse('premium_promo') in (response.get('Location') or '')


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


@pytest.mark.integration
@pytest.mark.django_db
class TestSubscriptionsManagementView:
    """Тесты страницы управления premium-подписками."""

    def test_management_page_requires_login(self, client: Client) -> None:
        response = client.get(reverse('premium_subscriptions_management'))

        assert response.status_code == 302
        assert '/account/signin' in str(response.url)  # type: ignore[attr-defined]

    def test_management_page_denies_non_superuser(self, client: Client, user: User) -> None:
        client.force_login(user)

        response = client.get(reverse('premium_subscriptions_management'))

        assert response.status_code == 403

    def test_management_page_shows_active_and_expired_subscriptions(
        self,
        client: Client,
        django_user_model: type[User],
        active_subscription: PremiumSubscription,
        premium_plan: PremiumPlan,
    ) -> None:
        admin = django_user_model.objects.create_superuser(
            username='admin',
            password='adminpass',
            email='admin@example.com',
        )
        expired_user = django_user_model.objects.create_user(
            username='expired_user',
            password='testpass123',
            email='expired@example.com',
        )
        PremiumSubscription.objects.create(
            user=active_subscription.user,
            plan=premium_plan,
            billing_period=PremiumSubscription.BillingPeriod.MONTHLY,
            status=PremiumSubscription.Status.EXPIRED,
            started_at=timezone.now() - timedelta(days=80),
            expires_at=timezone.now() - timedelta(days=50),
        )
        PremiumSubscription.objects.create(
            user=expired_user,
            plan=premium_plan,
            billing_period=PremiumSubscription.BillingPeriod.MONTHLY,
            status=PremiumSubscription.Status.EXPIRED,
            started_at=timezone.now() - timedelta(days=90),
            expires_at=timezone.now() - timedelta(days=60),
        )
        PremiumSubscription.objects.create(
            user=expired_user,
            plan=premium_plan,
            billing_period=PremiumSubscription.BillingPeriod.MONTHLY,
            status=PremiumSubscription.Status.EXPIRED,
            started_at=timezone.now() - timedelta(days=40),
            expires_at=timezone.now() - timedelta(days=10),
        )
        client.force_login(admin)

        response = client.get(reverse('premium_subscriptions_management'))

        assert response.status_code == 200
        assert 'premium/subscriptions_management.html' in [t.name for t in response.templates]
        assert response.context['active_subscriptions'][0].subscription.pk == active_subscription.pk
        assert len(response.context['active_subscriptions'][0].previous_subscriptions) == 1
        assert response.context['expired_subscriptions'][0].days_since_expired == 10
        assert len(response.context['expired_subscriptions']) == 1
        assert len(response.context['expired_subscriptions'][0].previous_subscriptions) == 1

        content = response.content.decode()
        assert 'dui-status dui-status-success animate-bounce' in content
        assert 'dui-status dui-status-warning animate-bounce' in content
        assert 'dui-table dui-table-zebra' in content
        assert 'text-xs font-normal text-base-content/60' in content
        assert 'animate-ping' not in content
        assert 'Активна' in content
        assert '(ещё 30 дней)' in content
        assert 'dui-badge dui-badge-success">Активна' not in content
