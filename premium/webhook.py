"""
Вебхук для приёма уведомлений от платёжного провайдера (например, YooKassa).
"""

from __future__ import annotations

import json
from datetime import timedelta

from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from yookassa.domain.notification import (
    WebhookNotificationEventType,
    WebhookNotificationFactory,
)

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

PAYMENT_EVENTS: frozenset[str] = frozenset(
    {
        WebhookNotificationEventType.PAYMENT_WAITING_FOR_CAPTURE,
        WebhookNotificationEventType.PAYMENT_SUCCEEDED,
        WebhookNotificationEventType.PAYMENT_CANCELED,
    }
)


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
    Принимает POST с JSON-телом уведомления YooKassa, валидирует его
    через библиотеку yookassa, находит платёж по object.id и обновляет
    статус с учётом допустимых переходов.
    Всегда возвращает 200, чтобы YooKassa не повторял запрос.
    """
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, TypeError) as e:
        log_invalid_json(request, e)
        return HttpResponse(status=200)

    try:
        notification = WebhookNotificationFactory().create(data)
    except (ValueError, TypeError) as e:
        log_invalid_payload(request, data, e)
        return HttpResponse(status=200)

    if notification.event not in PAYMENT_EVENTS:
        return HttpResponse(status=200)

    payment_id = notification.object.id
    new_status = notification.object.status

    try:
        payment = PremiumPayment.objects.select_related(
            'subscription', 'subscription__plan'
        ).get(yookassa_payment_id=payment_id)
    except PremiumPayment.DoesNotExist:
        log_payment_not_found(request, payment_id)
        return HttpResponse(status=200)

    PremiumPaymentWebhookLog.objects.create(
        payment=payment,
        status=new_status,
        raw_payload=data,
    )

    # Для всех статусов обновляем его в базе данных
    if not can_transition(payment.status, new_status):
        log_transition_denied(request, payment_id, payment.status, new_status)
        return HttpResponse(status=200)

    payment.status = new_status
    payment.save()
    log_status_updated(request, payment_id, new_status)

    # А для статуса SUCCEEDED обрабатываем подписку в зависимости от контекста:
    # новая, апгрейд (дороже), продление (тот же план), даунгрейд (дешевле)
    if (
        notification.event == WebhookNotificationEventType.PAYMENT_SUCCEEDED
        and new_status == PremiumPayment.Status.SUCCEEDED
    ):
        subscription = payment.subscription
        if subscription is not None and subscription.status == PremiumSubscription.Status.PENDING:
            now = timezone.now()
            if subscription.billing_period == PremiumSubscription.BillingPeriod.YEARLY:
                period_days = 365
            else:
                period_days = 30
            new_expires_at = (now + timedelta(days=period_days)).replace(
                hour=23, minute=59, second=59, microsecond=999999
            )

            old_active = (
                PremiumSubscription.objects.filter(
                    user=subscription.user,
                    status=PremiumSubscription.Status.ACTIVE,
                )
                .exclude(pk=subscription.pk)
                .select_related('plan')
                .first()
            )

            if old_active is None:
                # Новая подписка (у пользователя не было активной)
                subscription.started_at = now
                subscription.expires_at = new_expires_at
                subscription.status = PremiumSubscription.Status.ACTIVE
                subscription.save()
            else:
                new_plan = subscription.plan
                old_plan = old_active.plan
                new_price = new_plan.price_month
                old_price = old_plan.price_month

                if new_price > old_price:
                    # Апгрейд: сразу активируем новую, старую приостанавливаем
                    remaining_days = max(
                        0,
                        (old_active.expires_at - now).days if old_active.expires_at else 0,
                    )
                    old_active.expires_at = new_expires_at + timedelta(days=remaining_days)
                    old_active.status = PremiumSubscription.Status.PAUSED
                    old_active.save()

                    subscription.started_at = now
                    subscription.expires_at = new_expires_at
                    subscription.status = PremiumSubscription.Status.ACTIVE
                    subscription.save()
                elif new_price == old_price:
                    # Продление: продлеваем текущую подписку, новую отменяем
                    if old_active.expires_at is not None and old_active.expires_at > now:
                        base_date = old_active.expires_at
                    else:
                        base_date = now
                    old_active.expires_at = (base_date + timedelta(days=period_days)).replace(
                        hour=23, minute=59, second=59, microsecond=999999
                    )
                    old_active.save()

                    subscription.status = PremiumSubscription.Status.CANCELED
                    subscription.save()
                else:
                    # Даунгрейд: новая подписка активируется после окончания текущей
                    old_expires = old_active.expires_at or now
                    subscription.started_at = old_expires
                    subscription.expires_at = (old_expires + timedelta(days=period_days)).replace(
                        hour=23, minute=59, second=59, microsecond=999999
                    )
                    subscription.status = PremiumSubscription.Status.SCHEDULED
                    subscription.save()

    return HttpResponse(status=200)
