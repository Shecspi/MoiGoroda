"""
Репозитории для работы с данными premium-приложения.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

from django.contrib.auth.models import User
from django.utils import timezone

from premium.models import (
    PremiumPayment,
    PremiumPaymentWebhookLog,
    PremiumPlan,
    PremiumSubscription,
)


class CheckoutRepository:
    """Репозиторий операций checkout: планы, подписки, платежи."""

    def get_plan_by_id(self, plan_id: str) -> PremiumPlan | None:
        """Возвращает активный план по ID или None."""
        try:
            return PremiumPlan.objects.get(pk=plan_id, is_active=True)
        except (PremiumPlan.DoesNotExist, ValueError):
            return None

    def create_subscription(
        self,
        user: User,
        plan: PremiumPlan,
        billing_period: str,
        provider_payment_id: str,
    ) -> PremiumSubscription:
        """Создаёт подписку в статусе PENDING."""
        return PremiumSubscription.objects.create(
            user=user,
            plan=plan,
            billing_period=billing_period,
            status=PremiumSubscription.Status.PENDING,
            provider_payment_id=provider_payment_id,
        )

    def create_payment(
        self,
        user: User,
        subscription: PremiumSubscription,
        plan: PremiumPlan,
        amount_value: str | float | Decimal,
        currency: str,
        billing_period: str,
        description: str,
        yookassa_payment_id: str,
        confirmation_url: str,
        status: str,
    ) -> PremiumPayment:
        """Создаёт запись платежа."""
        return PremiumPayment.objects.create(
            user=user,
            subscription=subscription,
            plan=plan,
            yookassa_payment_id=yookassa_payment_id,
            amount_value=amount_value,
            currency=currency,
            billing_period=billing_period,
            description=description,
            confirmation_url=confirmation_url,
            status=PremiumPayment.Status(status),
        )

    def create_webhook_log(
        self,
        payment: PremiumPayment,
        status: str,
        raw_payload: dict[str, Any],
    ) -> PremiumPaymentWebhookLog:
        """Создаёт лог вебхука для платежа."""
        return PremiumPaymentWebhookLog.objects.create(
            payment=payment,
            status=status,
            raw_payload=raw_payload,
        )


class SubscriptionPageRepository:
    """Репозиторий данных для страницы «Моя подписка»."""

    def get_payments_for_user(self, user: User) -> list[PremiumPayment]:
        """Возвращает платежи пользователя, отсортированные по дате (новые первые)."""
        return list(
            PremiumPayment.objects.filter(user=user)
            .select_related('plan')
            .order_by('-created_at')
        )

    def get_active_subscription(
        self, user: User
    ) -> PremiumSubscription | None:
        """Возвращает активную подписку пользователя или None."""
        return (
            PremiumSubscription.objects.filter(
                user=user,
                status=PremiumSubscription.Status.ACTIVE,
            )
            .select_related('plan')
            .prefetch_related('plan__features')
            .first()
        )

    def get_paused_subscriptions(
        self,
        user: User,
        active_subscription: PremiumSubscription | None,
    ) -> list[tuple[PremiumSubscription, datetime, datetime]]:
        """
        Возвращает приостановленные и запланированные подписки с датами активации.
        Каждый элемент — (подписка, дата_начала, дата_окончания).
        """
        if active_subscription is None or active_subscription.expires_at is None:
            return []

        now = timezone.now()
        future_subs = (
            PremiumSubscription.objects.filter(
                user=user,
                status__in=(
                    PremiumSubscription.Status.SCHEDULED,
                    PremiumSubscription.Status.PAUSED,
                ),
                expires_at__gt=now,
            )
            .select_related('plan')
            .order_by('expires_at')
        )

        result: list[tuple[PremiumSubscription, datetime, datetime]] = []
        next_start = active_subscription.expires_at + timedelta(days=1)
        for sub in future_subs:
            if sub.expires_at is not None:
                result.append((sub, next_start, sub.expires_at))
                next_start = sub.expires_at + timedelta(days=1)
        return result

    def get_payment_by_id_and_user(
        self, payment_id: str, user: User
    ) -> PremiumPayment | None:
        """Возвращает платёж по ID и пользователю или None."""
        return PremiumPayment.objects.filter(
            pk=payment_id,
            user=user,
        ).first()
