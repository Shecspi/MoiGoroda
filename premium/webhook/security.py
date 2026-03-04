"""
Проверка IP-адресов для вебхука YooKassa.
Список IP взят из официальной документации: https://yookassa.ru/developers/using-api/webhooks#ip
"""

from __future__ import annotations

import ipaddress
import logging

from django.conf import settings
from django.http import HttpRequest

logger = logging.getLogger('premium.webhook')

# Официальные IP-адреса YooKassa для уведомлений
YOOKASSA_WEBHOOK_ALLOWED_NETWORKS = [
    '77.75.154.128/25',
    '77.75.156.35',
    '77.75.156.11',
    '77.75.153.0/25',
    '185.71.77.0/27',
    '185.71.76.0/27',
    '2a02:5180::/32',
]

_compiled_networks: list[ipaddress.IPv4Network | ipaddress.IPv6Network] | None = None


def _get_allowed_networks() -> list[ipaddress.IPv4Network | ipaddress.IPv6Network]:
    """Возвращает скомпилированные сети (с кэшированием)."""
    global _compiled_networks
    if _compiled_networks is None:
        networks = getattr(
            settings,
            'YOOKASSA_WEBHOOK_ALLOWED_IPS',
            YOOKASSA_WEBHOOK_ALLOWED_NETWORKS,
        )
        _compiled_networks = [ipaddress.ip_network(n) for n in networks]
    return _compiled_networks


def _get_client_ip(request: HttpRequest) -> str:
    """Извлекает IP клиента с учётом X-Forwarded-For (за прокси)."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return str(x_forwarded_for).split(',')[0].strip()
    return str(request.META.get('REMOTE_ADDR') or '')


def is_yookassa_webhook_ip_allowed(request: HttpRequest) -> bool:
    """
    Проверяет, что запрос пришёл с разрешённого IP YooKassa.

    Возвращает True, если проверка отключена (YOOKASSA_WEBHOOK_IP_VERIFICATION=False)
    или IP в whitelist.
    """
    if not getattr(settings, 'YOOKASSA_WEBHOOK_IP_VERIFICATION', True):
        return True

    client_ip_str = _get_client_ip(request)
    if not client_ip_str:
        return False

    try:
        client_ip = ipaddress.ip_address(client_ip_str)
    except ValueError:
        logger.warning(
            '(Premium webhook) Невалидный IP в запросе: %s',
            client_ip_str,
        )
        return False

    for network in _get_allowed_networks():
        if client_ip in network:
            return True

    logger.warning(
        '(Premium webhook) Запрос с неразрешённого IP: %s',
        client_ip_str,
    )
    return False
