"""
Логирование вебхука YooKassa — вынесено, чтобы не загромождать основную функцию.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from django.http import HttpRequest

logger = logging.getLogger('premium.webhook')


def _get_client_ip(request: HttpRequest) -> str:
    try:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip() or 'X.X.X.X'
        return str(request.META.get('REMOTE_ADDR') or 'X.X.X.X')
    except Exception:
        return 'X.X.X.X'


def _extra(request: HttpRequest, user: str | None = None) -> dict[str, str]:
    if user is None:
        user = 'WEBHOOK'
    return {'IP': _get_client_ip(request), 'user': user}


def log_invalid_json(request: HttpRequest, error: BaseException) -> None:
    body_preview = (request.body or b'')[:500].decode('utf-8', errors='replace')
    logger.warning(
        '(Premium webhook) Невалидный JSON в теле запроса   %s   error=%s body_preview=%s',
        request.get_full_path(),
        repr(error),
        body_preview,
        extra=_extra(request),
    )


def log_invalid_payload(
    request: HttpRequest,
    data: dict[str, Any],
    error: BaseException,
) -> None:
    payment_id = (data.get('object') or {}).get('id', '?')
    logger.warning(
        '(Premium webhook) Невалидный payload: type=%s event=%s object.id=%s   %s   validation_error=%s',
        data.get('type', '?'),
        data.get('event', '?'),
        payment_id,
        request.get_full_path(),
        str(error),
        extra=_extra(request),
    )


def log_payment_not_found(request: HttpRequest, payment_id: str) -> None:
    logger.info(
        '(Premium webhook) Платёж не найден в БД: payment_id=%s   %s',
        payment_id,
        request.get_full_path(),
        extra=_extra(request),
    )


def log_transition_denied(
    request: HttpRequest,
    payment_id: str,
    current_status: str,
    new_status: str,
) -> None:
    logger.info(
        '(Premium webhook) Переход статуса отклонён: payment_id=%s current=%s new=%s   %s',
        payment_id,
        current_status,
        new_status,
        request.get_full_path(),
        extra=_extra(request),
    )


def log_status_updated(
    request: HttpRequest,
    payment_id: str,
    new_status: str,
) -> None:
    logger.info(
        '(Premium webhook) Статус обновлён: payment_id=%s new_status=%s   %s',
        payment_id,
        new_status,
        request.get_full_path(),
        extra=_extra(request),
    )


def log_yookassa_create_response(
    request: HttpRequest,
    payment_id: str,
    status: str,
    response_data: dict[str, Any],
) -> None:
    """Ответ YooKassa на создание платежа (checkout)."""
    user = request.user.username if getattr(request.user, 'is_authenticated', False) else 'WEBHOOK'
    logger.info(
        '(Premium checkout) YooKassa создан платёж: id=%s status=%s   %s   response=%s',
        payment_id,
        status,
        request.get_full_path(),
        json.dumps(response_data, ensure_ascii=False),
        extra=_extra(request, user=user),
    )
