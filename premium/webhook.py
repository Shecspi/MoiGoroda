"""
Вебхук для приёма уведомлений от платёжного провайдера (например, YooKassa).
"""

from __future__ import annotations

import json
from datetime import timedelta
from typing import Literal

import msgspec
from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from premium.models import PremiumPayment, PremiumPaymentWebhookLog, PremiumSubscription
from premium.webhook_logging import (
    log_invalid_json,
    log_invalid_payload,
    log_payment_not_found,
    log_status_updated,
    log_transition_denied,
)

FINAL_STATUSES: frozenset[str] = frozenset(
    {
        PremiumPayment.Status.SUCCEEDED,
        PremiumPayment.Status.CANCELED,
    }
)


class PaymentObject(msgspec.Struct, frozen=True):
    """Объект платежа из тела уведомления YooKassa."""

    id: str
    status: str


class WebhookPayload(msgspec.Struct, frozen=True):
    """
    Валидированное тело вебхука.
    type — строго "notification", event — один из разрешённых событий.
    """

    type: Literal['notification']
    event: Literal[
        'payment.waiting_for_capture',
        'payment.succeeded',
        'payment.canceled',
    ]
    object: PaymentObject


def can_transition(current_status: str, new_status: str) -> bool:
    """
    Нельзя переводить платёж из succeeded/canceled обратно в waiting_for_capture.
    """
    if new_status != PremiumPayment.Status.WAITING_FOR_CAPTURE:
        return True
    return current_status not in FINAL_STATUSES


@csrf_exempt
@require_POST
def yookassa_webhook(request: HttpRequest) -> HttpResponse:
    """
    Принимает POST с JSON-телом уведомления YooKassa, валидирует его,
    находит платёж по object.id и обновляет статус с учётом допустимых переходов.
    Всегда возвращает 200, чтобы YooKassa не повторял запрос.
    """
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, TypeError) as e:
        log_invalid_json(request, e)
        return HttpResponse(status=200)

    try:
        payload = msgspec.convert(data, WebhookPayload)
    except msgspec.ValidationError as e:
        log_invalid_payload(request, data, e)
        return HttpResponse(status=200)

    payment_id = payload.object.id
    new_status = payload.object.status

    try:
        payment = PremiumPayment.objects.get(yookassa_payment_id=payment_id)
    except PremiumPayment.DoesNotExist:
        log_payment_not_found(request, payment_id)
        return HttpResponse(status=200)

    PremiumPaymentWebhookLog.objects.create(
        payment=payment,
        status=new_status,
        raw_payload=data,
    )

    if not can_transition(payment.status, new_status):
        log_transition_denied(request, payment_id, payment.status, new_status)
        return HttpResponse(status=200)

    payment.status = new_status
    payment.save()
    log_status_updated(request, payment_id, new_status)

    if payload.event == 'payment.succeeded' and new_status == PremiumPayment.Status.SUCCEEDED:
        subscription = payment.subscription
        # В момент создания платежа была создана и подписка со статусом PENDING
        if subscription is not None and subscription.status == PremiumSubscription.Status.PENDING:
            now = timezone.now()
            if subscription.billing_period == PremiumSubscription.BillingPeriod.YEARLY:
                end_date = now + timedelta(days=365)
            else:
                end_date = now + timedelta(days=30)
            new_expires_at = end_date.replace(
                hour=23, minute=59, second=59, microsecond=999999
            )

            # Если у пользователя уже есть активная подписка — переводим её в приостановленную
            # и переносим дату истечения на «конец новой подписки» + оставшиеся дни
            old_active = (
                PremiumSubscription.objects.filter(
                    user=subscription.user,
                    status=PremiumSubscription.Status.ACTIVE,
                )
                .exclude(pk=subscription.pk)
                .first()
            )
            if old_active is not None and old_active.expires_at is not None:
                remaining_days = max(
                    0,
                    (old_active.expires_at - now).days,
                )
                old_active.expires_at = new_expires_at + timedelta(days=remaining_days)
                old_active.status = PremiumSubscription.Status.PAUSED
                old_active.save()

            subscription.started_at = now
            subscription.expires_at = new_expires_at
            subscription.status = PremiumSubscription.Status.ACTIVE
            subscription.save()

    return HttpResponse(status=200)
