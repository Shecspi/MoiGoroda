"""
Вебхук для приёма уведомлений от платёжного провайдера (например, YooKassa).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from yookassa.domain.notification import (
    WebhookNotificationEventType,
    WebhookNotificationFactory,
)

from premium.models import (
    PremiumPayment,
    PremiumPaymentWebhookLog,
    PremiumPlan,
    PremiumSubscription,
)
from premium.webhook_logging import (
    log_invalid_json,
    log_invalid_payload,
    log_payment_not_found,
    log_status_updated,
    log_transition_denied,
)


def _period_days(billing_period: str) -> int:
    if billing_period == PremiumSubscription.BillingPeriod.YEARLY:
        return 365
    return 30


def _end_of_day(dt) -> "timezone.datetime":
    return dt.replace(hour=23, minute=59, second=59, microsecond=999999)


@dataclass
class _ChainItem:
    """Элемент цепочки подписок для перераспределения."""

    subscription: PremiumSubscription | None  # None для остатка дней (создаётся новый)
    plan: PremiumPlan
    duration_days: int
    billing_period: str
    is_remaining_days: bool = False


def _build_and_save_chain(
    user,
    chain_items: list[_ChainItem],
    chain_start,
) -> None:
    """
    Сохраняет цепочку подписок с непрерывными датами.
    chain_start — дата начала первой подписки в цепочке.
    """
    cursor = chain_start
    for item in chain_items:
        period = timedelta(days=item.duration_days)
        start = cursor
        end = _end_of_day(cursor + period)

        if item.subscription is not None:
            item.subscription.started_at = start
            item.subscription.expires_at = end
            item.subscription.status = PremiumSubscription.Status.SCHEDULED
            item.subscription.save()
        else:
            PremiumSubscription.objects.create(
                user=user,
                plan=item.plan,
                billing_period=item.billing_period,
                status=PremiumSubscription.Status.SCHEDULED,
                started_at=start,
                expires_at=end,
            )

        cursor = end + timedelta(days=1)


def _shift_chain_after_renewal(user, new_active_expires_at) -> None:
    """
    Сдвигает цепочку SCHEDULED/PAUSED после продления активной подписки.
    Сохраняет длительности, меняет даты начала/окончания для непрерывности.
    """
    now = timezone.now()
    future_subs = list(
        PremiumSubscription.objects.filter(
            user=user,
            status__in=(
                PremiumSubscription.Status.SCHEDULED,
                PremiumSubscription.Status.PAUSED,
            ),
            expires_at__gt=now,
        )
        .select_related('plan')
        .order_by('expires_at')
    )
    if not future_subs:
        return

    chain_start = new_active_expires_at + timedelta(days=1)
    cursor = chain_start

    for sub in future_subs:
        if sub.started_at is not None and sub.expires_at is not None:
            duration = max(1, (sub.expires_at - sub.started_at).days)
        else:
            duration = _period_days(sub.billing_period)

        start = cursor
        end = _end_of_day(cursor + timedelta(days=duration))

        sub.started_at = start
        sub.expires_at = end
        sub.status = PremiumSubscription.Status.SCHEDULED
        sub.save()

        cursor = end + timedelta(days=1)


def activate_subscription_on_payment_success(subscription: PremiumSubscription) -> bool:
    """
    Активирует подписку после успешной оплаты.

    Логика:
    - Если нет активной подписки: новая становится активной.
    - Если есть активная и новая дороже: старая → INTERRUPTED (expires_at=сегодня),
      новая → ACTIVE. Остаток дней от старой создаётся как новая подписка после новой.
      Ожидающие (SCHEDULED, PAUSED) перераспределяются по стоимости.
    - Если новая дешевле или равна: продление (равная) или отмена (дешевле, блокируется в checkout).
    """
    if subscription.status != PremiumSubscription.Status.PENDING:
        return False

    now = timezone.now()
    period_days = _period_days(subscription.billing_period)
    new_expires_at = _end_of_day(now + timedelta(days=period_days))

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
        subscription.started_at = now
        subscription.expires_at = new_expires_at
        subscription.status = PremiumSubscription.Status.ACTIVE
        subscription.save()
        return True

    new_plan = subscription.plan
    old_plan = old_active.plan
    new_price: Decimal = new_plan.price_month
    old_price: Decimal = old_plan.price_month

    if new_price > old_price:
        with transaction.atomic():
            _handle_upgrade(
                subscription=subscription,
                old_active=old_active,
                now=now,
                new_expires_at=new_expires_at,
                period_days=period_days,
            )
    elif new_price == old_price:
        if old_active.expires_at is not None and old_active.expires_at > now:
            base_date = old_active.expires_at
        else:
            base_date = now
        old_active.expires_at = _end_of_day(base_date + timedelta(days=period_days))
        old_active.save()

        _shift_chain_after_renewal(subscription.user, old_active.expires_at)

        subscription.status = PremiumSubscription.Status.CANCELED
        subscription.save()
    else:
        with transaction.atomic():
            _handle_downgrade(
                subscription=subscription,
                old_active=old_active,
                now=now,
                period_days=period_days,
            )

    return True


def _handle_downgrade(
    subscription: PremiumSubscription,
    old_active: PremiumSubscription,
    now,
    period_days: int,
) -> None:
    """
    Обрабатывает даунгрейд: новая подписка добавляется в цепочку SCHEDULED
    после текущей активной и существующих ожидающих, с учётом сортировки по стоимости.
    """
    chain_start = (
        (old_active.expires_at + timedelta(days=1))
        if old_active.expires_at is not None and old_active.expires_at > now
        else now + timedelta(days=1)
    )

    chain_items: list[_ChainItem] = [
        _ChainItem(
            subscription=subscription,
            plan=subscription.plan,
            duration_days=period_days,
            billing_period=subscription.billing_period,
            is_remaining_days=False,
        )
    ]

    future_subs = list(
        PremiumSubscription.objects.filter(
            user=subscription.user,
            status__in=(
                PremiumSubscription.Status.SCHEDULED,
                PremiumSubscription.Status.PAUSED,
            ),
        )
        .exclude(pk=subscription.pk)
        .exclude(pk=old_active.pk)
        .select_related('plan')
        .order_by('expires_at')
    )

    for sub in future_subs:
        if sub.expires_at is not None and sub.expires_at <= now:
            continue
        if sub.started_at is not None and sub.expires_at is not None:
            duration = max(1, (sub.expires_at - sub.started_at).days)
        else:
            duration = _period_days(sub.billing_period)
        chain_items.append(
            _ChainItem(
                subscription=sub,
                plan=sub.plan,
                duration_days=duration,
                billing_period=sub.billing_period,
                is_remaining_days=False,
            )
        )

    chain_items.sort(
        key=lambda x: (
            -float(x.plan.price_month),
            x.is_remaining_days,
        )
    )

    _build_and_save_chain(subscription.user, chain_items, chain_start)


def _handle_upgrade(
    subscription: PremiumSubscription,
    old_active: PremiumSubscription,
    now,
    new_expires_at,
    period_days: int,
) -> None:
    """
    Обрабатывает апгрейд: старая → INTERRUPTED, новая → ACTIVE,
    остаток дней и ожидающие подписки перераспределяются по стоимости.
    """
    today_end = _end_of_day(now)

    remaining_days = max(
        0,
        (old_active.expires_at - now).days if old_active.expires_at else 0,
    )

    old_active.expires_at = today_end
    old_active.status = PremiumSubscription.Status.INTERRUPTED
    old_active.save()

    subscription.started_at = now
    subscription.expires_at = new_expires_at
    subscription.status = PremiumSubscription.Status.ACTIVE
    subscription.save()

    chain_items: list[_ChainItem] = []

    if remaining_days > 0:
        chain_items.append(
            _ChainItem(
                subscription=None,
                plan=old_active.plan,
                duration_days=remaining_days,
                billing_period=old_active.billing_period,
                is_remaining_days=True,
            )
        )

    future_subs = list(
        PremiumSubscription.objects.filter(
            user=subscription.user,
            status__in=(
                PremiumSubscription.Status.SCHEDULED,
                PremiumSubscription.Status.PAUSED,
            ),
        )
        .exclude(pk=subscription.pk)
        .exclude(pk=old_active.pk)
        .select_related('plan')
        .order_by('expires_at')
    )

    for sub in future_subs:
        if sub.expires_at is not None and sub.expires_at <= now:
            continue
        if sub.started_at is not None and sub.expires_at is not None:
            duration = max(1, (sub.expires_at - sub.started_at).days)
        else:
            duration = _period_days(sub.billing_period)
        chain_items.append(
            _ChainItem(
                subscription=sub,
                plan=sub.plan,
                duration_days=duration,
                billing_period=sub.billing_period,
                is_remaining_days=False,
            )
        )

    chain_items.sort(
        key=lambda x: (
            -float(x.plan.price_month),
            x.is_remaining_days,
        )
    )

    chain_start = new_expires_at + timedelta(days=1)
    _build_and_save_chain(subscription.user, chain_items, chain_start)


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

    if (
        notification.event == WebhookNotificationEventType.PAYMENT_SUCCEEDED
        and new_status == PremiumPayment.Status.SUCCEEDED
    ):
        subscription = payment.subscription
        if subscription is not None:
            activate_subscription_on_payment_success(subscription)

    return HttpResponse(status=200)
