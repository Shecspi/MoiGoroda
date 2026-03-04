"""
Сервис checkout — бизнес-логика оформления премиум-подписки.
Оркестрирует репозиторий и платёжный адаптер.
"""

from __future__ import annotations

import uuid

from django.contrib.auth.models import User

from premium.adapters.payment_provider import PaymentProvider
from premium.adapters.yookassa_adapter import YooKassaPaymentAdapter
from premium.dto import CheckoutResult
from premium.models import PremiumSubscription
from premium.repository import CheckoutRepository


class CheckoutService:
    """Сервис оформления премиум-подписки."""

    def __init__(
        self,
        repository: CheckoutRepository | None = None,
        payment_provider: PaymentProvider | None = None,
    ) -> None:
        self._repository = repository or CheckoutRepository()
        self._payment_provider = payment_provider or YooKassaPaymentAdapter()

    def create_checkout(
        self,
        user: User,
        plan_id: str,
        billing_period: str,
        return_url: str,
        promo_url: str,
    ) -> CheckoutResult:
        """
        Создаёт платёж и возвращает результат для редиректа.

        При неудаче (невалидный план, ошибка API) возвращает success=False
        с redirect_url на страницу промо.
        """
        plan = self._repository.get_plan_by_id(plan_id)

        if plan is None:
            return CheckoutResult(
                success=False,
                redirect_url=promo_url,
            )

        period = billing_period
        if period == PremiumSubscription.BillingPeriod.YEARLY:
            amount_value = plan.price_year
            period_label = 'на год'
        else:
            period = PremiumSubscription.BillingPeriod.MONTHLY
            amount_value = plan.price_month
            period_label = 'на месяц'

        description = f'Тариф «{plan.name}» для пользователя {user.username} {period_label}'

        try:
            payment_result = self._payment_provider.create_payment(
                amount_value=f'{amount_value:.2f}',
                currency=plan.currency,
                description=description,
                return_url=return_url,
                idempotency_key=str(uuid.uuid4()),
            )
        except Exception:
            return CheckoutResult(
                success=False,
                redirect_url=promo_url,
            )

        subscription = self._repository.create_subscription(
            user=user,
            plan=plan,
            billing_period=period,
            provider_payment_id=payment_result.payment_id,
        )

        premium_payment = self._repository.create_payment(
            user=user,
            subscription=subscription,
            plan=plan,
            amount_value=amount_value,
            currency=plan.currency,
            billing_period=period,
            description=description,
            yookassa_payment_id=payment_result.payment_id,
            confirmation_url=payment_result.confirmation_url,
            status=payment_result.status,
        )

        self._repository.create_webhook_log(
            payment=premium_payment,
            status=payment_result.status,
            raw_payload=payment_result.raw_response,
        )

        redirect_url_final = (
            payment_result.confirmation_url
            if payment_result.confirmation_url
            else return_url
        )

        return CheckoutResult(
            success=True,
            redirect_url=redirect_url_final,
            payment_id=str(premium_payment.pk),
            yookassa_payment_id=payment_result.payment_id,
            yookassa_status=payment_result.status,
            raw_response=payment_result.raw_response,
        )
