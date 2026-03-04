"""Репозиторий операций checkout."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

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
        except (PremiumPlan.DoesNotExist, ValueError, ValidationError):
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
