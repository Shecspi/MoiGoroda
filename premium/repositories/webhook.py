"""Репозиторий данных для обработки вебхука YooKassa."""

from __future__ import annotations

from typing import Any

from premium.models import PremiumPayment, PremiumPaymentWebhookLog


class WebhookRepository:
    """Репозиторий данных для обработки вебхука YooKassa."""

    def get_payment_by_yookassa_id(
        self, yookassa_payment_id: str
    ) -> PremiumPayment | None:
        """Возвращает платёж по ID в YooKassa или None."""
        return (
            PremiumPayment.objects.filter(
                yookassa_payment_id=yookassa_payment_id,
            )
            .select_related('subscription', 'subscription__plan')
            .first()
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
