"""
Вебхук для приёма уведомлений от платёжного провайдера (например, YooKassa).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Literal

from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from premium.models import PremiumPayment, PremiumPaymentWebhookLog

ALLOWED_EVENTS: tuple[str, ...] = (
    'payment.waiting_for_capture',
    'payment.succeeded',
    'payment.canceled',
)
FINAL_STATUSES: frozenset[str] = frozenset({
    PremiumPayment.Status.SUCCEEDED,
    PremiumPayment.Status.CANCELED,
})


@dataclass(frozen=True)
class PaymentObject:
    """Объект платежа из тела уведомления YooKassa."""
    id: str
    status: str


@dataclass(frozen=True)
class WebhookPayload:
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

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WebhookPayload:
        if data.get('type') != 'notification':
            raise ValueError('type must be "notification"')
        event = data.get('event')
        if event not in ALLOWED_EVENTS:
            raise ValueError(f'event must be one of {ALLOWED_EVENTS}')
        obj = data.get('object')
        if not isinstance(obj, dict):
            raise ValueError('object must be a dict')
        payment_id = obj.get('id')
        status = obj.get('status')
        if not payment_id or not status:
            raise ValueError('object must have id and status')
        return cls(
            type='notification',
            event=event,
            object=PaymentObject(id=str(payment_id), status=str(status)),
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
    Принимает POST с JSON-телом уведомления YooKassa, валидирует его,
    находит платёж по object.id и обновляет статус с учётом допустимых переходов.
    Всегда возвращает 200, чтобы YooKassa не повторял запрос.
    """
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return HttpResponse(status=200)

    try:
        payload = WebhookPayload.from_dict(data)
    except (ValueError, KeyError, TypeError):
        return HttpResponse(status=200)

    try:
        payment = PremiumPayment.objects.get(yookassa_payment_id=payload.object.id)
    except PremiumPayment.DoesNotExist:
        return HttpResponse(status=200)

    PremiumPaymentWebhookLog.objects.create(
        payment=payment,
        status=payload.object.status,
        raw_payload=data,
    )

    if not can_transition(payment.status, payload.object.status):
        return HttpResponse(status=200)

    payment.status = payload.object.status
    payment.save()
    return HttpResponse(status=200)


# Пример запроса для проверки вебхука (payment.waiting_for_capture):
#
# curl -X POST http://127.0.0.1:8000/premium/webhook/yookassa/ \
#   -H "Content-Type: application/json" \
#   -d '{
#   "type": "notification",
#   "event": "payment.waiting_for_capture",
#   "object": {
#     "id": "22d6d597-000f-5000-9000-145f6df21d6f",
#     "status": "waiting_for_capture",
#     "paid": true,
#     "amount": {"value": "2.00", "currency": "RUB"},
#     "authorization_details": {
#       "rrn": "603668680243",
#       "auth_code": "000000",
#       "three_d_secure": {"applied": true}
#     },
#     "created_at": "2018-07-10T14:27:54.691Z",
#     "description": "Заказ №72",
#     "expires_at": "2018-07-17T14:28:32.484Z",
#     "metadata": {},
#     "payment_method": {
#       "type": "bank_card",
#       "id": "22d6d597-000f-5000-9000-145f6df21d6f",
#       "saved": false,
#       "card": {
#         "first6": "555555",
#         "last4": "4444",
#         "expiry_month": "07",
#         "expiry_year": "2021",
#         "card_type": "MasterCard",
#         "issuer_country": "RU",
#         "issuer_name": "Sberbank"
#       },
#       "title": "Bank card *4444"
#     },
#     "refundable": false,
#     "test": false
#   }
# }'
