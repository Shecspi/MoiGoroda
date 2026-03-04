"""
Сервис обработки вебхука YooKassa.
Парсит уведомления, обновляет статусы платежей, активирует подписки.
"""

from __future__ import annotations

from yookassa.domain.notification import (
    WebhookNotificationEventType,
    WebhookNotificationFactory,
)

from premium.dto import WebhookProcessResult
from premium.models import PremiumPayment
from premium.repository import WebhookRepository
from premium.subscription_activation import activate_subscription_on_payment_success


PAYMENT_EVENTS: frozenset[str] = frozenset(
    {
        WebhookNotificationEventType.PAYMENT_WAITING_FOR_CAPTURE,
        WebhookNotificationEventType.PAYMENT_SUCCEEDED,
        WebhookNotificationEventType.PAYMENT_CANCELED,
    }
)

FINAL_STATUSES: frozenset[str] = frozenset(
    {
        PremiumPayment.Status.SUCCEEDED,
        PremiumPayment.Status.CANCELED,
    }
)


def _can_transition(current_status: str, new_status: str) -> bool:
    """
    Нельзя переводить платёж из succeeded/canceled обратно в waiting_for_capture.
    """
    if new_status != PremiumPayment.Status.WAITING_FOR_CAPTURE:
        return True
    return current_status not in FINAL_STATUSES


class WebhookService:
    """Сервис обработки уведомлений YooKassa."""

    def __init__(
        self,
        repository: WebhookRepository | None = None,
    ) -> None:
        self._repository = repository or WebhookRepository()

    def process(self, data: dict) -> WebhookProcessResult:
        """
        Обрабатывает уведомление вебхука.
        Возвращает результат для логирования в view.
        """
        try:
            notification = WebhookNotificationFactory().create(data)
        except (ValueError, TypeError) as e:
            return WebhookProcessResult(
                status='invalid_payload',
                data=data,
                error=e,
            )

        if notification.event not in PAYMENT_EVENTS:
            return WebhookProcessResult(status='ignored')

        payment_id = notification.object.id
        new_status = notification.object.status

        payment = self._repository.get_payment_by_yookassa_id(payment_id)
        if payment is None:
            return WebhookProcessResult(
                status='payment_not_found',
                payment_id=payment_id,
            )

        self._repository.create_webhook_log(
            payment=payment,
            status=new_status,
            raw_payload=data,
        )

        if not _can_transition(payment.status, new_status):
            return WebhookProcessResult(
                status='transition_denied',
                payment_id=payment_id,
                current_status=payment.status,
                new_status=new_status,
            )

        payment.status = new_status
        payment.save()

        if (
            notification.event == WebhookNotificationEventType.PAYMENT_SUCCEEDED
            and new_status == PremiumPayment.Status.SUCCEEDED
        ):
            subscription = payment.subscription
            if subscription is not None:
                activate_subscription_on_payment_success(subscription)

        return WebhookProcessResult(
            status='ok',
            payment_id=payment_id,
            new_status=new_status,
        )
