"""
Сервис страницы «Моя подписка».
Оркестрирует синхронизацию платежей и получение данных для отображения.
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from django.contrib.auth.models import User

from premium.dto import SubscriptionPageData
from premium.models import PremiumPayment, PremiumSubscription
from premium.repositories.subscription_page import SubscriptionPageRepository
from premium.domain.subscription_activation import activate_subscription_on_payment_success


class PaymentStatusSync(Protocol):
    """Протокол для получения статуса платежа у провайдера."""

    def get_payment_status(self, payment_id: str) -> str | None:
        """Возвращает статус платежа или None при ошибке."""
        ...


def _sync_pending_payments(
    user: User,
    payment_provider: PaymentStatusSync,
) -> None:
    """
    Проверяет статус ожидающих платежей у провайдера и активирует подписки при успешной оплате.
    Вызывается при возврате пользователя с страницы оплаты (вебхук может не дойти в локальной разработке).
    """
    pending_payments = (
        PremiumPayment.objects.filter(
            user=user,
            subscription__status=PremiumSubscription.Status.PENDING,
        )
        .exclude(status__in=(PremiumPayment.Status.SUCCEEDED, PremiumPayment.Status.CANCELED))
        .select_related('subscription', 'subscription__plan')
        .order_by('-created_at')
    )
    for premium_payment in pending_payments:
        new_status = payment_provider.get_payment_status(premium_payment.yookassa_payment_id)
        if new_status is None:
            continue

        if new_status == PremiumPayment.Status.SUCCEEDED:
            premium_payment.status = PremiumPayment.Status.SUCCEEDED
            premium_payment.save()
            if premium_payment.subscription is not None:
                activate_subscription_on_payment_success(premium_payment.subscription)
            break

        if new_status == PremiumPayment.Status.CANCELED:
            premium_payment.status = PremiumPayment.Status.CANCELED
            premium_payment.save()
            break


def _get_payment_result(
    payment_id: str | None,
    user: User,
    repository: SubscriptionPageRepository,
    payment_provider: PaymentStatusSync,
) -> str | None:
    """
    Определяет результат возврата с оплаты: succeeded, canceled, pending или None.
    При наличии payment_id синхронизирует статусы с провайдером.
    """
    if not payment_id:
        return None

    _sync_pending_payments(user, payment_provider)
    premium_payment = repository.get_payment_by_id_and_user(payment_id, user)

    if premium_payment is None:
        return None
    if premium_payment.status == PremiumPayment.Status.SUCCEEDED:
        return 'succeeded'
    if premium_payment.status == PremiumPayment.Status.CANCELED:
        return 'canceled'
    return 'pending'


class SubscriptionPageService:
    """Сервис подготовки данных для страницы «Моя подписка»."""

    def __init__(
        self,
        repository: SubscriptionPageRepository | None = None,
        payment_provider: PaymentStatusSync | None = None,
    ) -> None:
        from premium.adapters.yookassa_adapter import YooKassaPaymentAdapter

        self._repository = repository or SubscriptionPageRepository()
        self._payment_provider = payment_provider or YooKassaPaymentAdapter()

    def get_page_data(
        self,
        user: User,
        payment_return_id: str | None = None,
    ) -> SubscriptionPageData:
        """Возвращает все данные для отображения страницы «Моя подписка»."""
        payment_result = _get_payment_result(
            payment_return_id,
            user,
            self._repository,
            self._payment_provider,
        )
        payments = self._repository.get_payments_for_user(user)
        active_subscription = self._repository.get_active_subscription(user)
        paused_subscriptions: list[tuple[PremiumSubscription, datetime, datetime]] = (
            self._repository.get_paused_subscriptions(
                user,
                active_subscription,
            )
        )

        return SubscriptionPageData(
            payments=payments,
            active_subscription=active_subscription,
            paused_subscriptions=paused_subscriptions,
            payment_result=payment_result,
        )
