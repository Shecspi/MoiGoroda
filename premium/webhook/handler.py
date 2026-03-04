"""
Вебхук для приёма уведомлений от платёжного провайдера (например, YooKassa).
"""

from __future__ import annotations

import json

from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from premium.services.webhook import WebhookService
from premium.webhook.security import is_yookassa_webhook_ip_allowed
from premium.webhook.logging import (
    log_invalid_json,
    log_invalid_payload,
    log_payment_not_found,
    log_status_updated,
    log_transition_denied,
)


@csrf_exempt
@require_POST
def yookassa_webhook(request: HttpRequest) -> HttpResponse:
    """
    Принимает POST с JSON-телом уведомления YooKassa, валидирует его
    через библиотеку yookassa, находит платёж по object.id и обновляет
    статус с учётом допустимых переходов.
    Всегда возвращает 200, чтобы YooKassa не повторял запрос.
    """
    if not is_yookassa_webhook_ip_allowed(request):
        return HttpResponse(status=200)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, TypeError) as e:
        log_invalid_json(request, e)
        return HttpResponse(status=200)

    result = WebhookService().process(data)

    if result.status == 'invalid_payload' and result.data is not None and result.error is not None:
        log_invalid_payload(request, result.data, result.error)
    elif result.status == 'payment_not_found':
        log_payment_not_found(request, result.payment_id)
    elif result.status == 'transition_denied':
        log_transition_denied(
            request,
            result.payment_id,
            result.current_status,
            result.new_status,
        )
    elif result.status == 'ok':
        log_status_updated(request, result.payment_id, result.new_status)

    return HttpResponse(status=200)
