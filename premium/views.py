"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from yookassa import Configuration, Payment  # type: ignore[import-untyped]
from yookassa.domain.exceptions import ApiError  # type: ignore[import-untyped]

from premium.models import (
    PremiumPayment,
    PremiumPaymentWebhookLog,
    PremiumPlan,
    PremiumSubscription,
)
from premium.webhook import activate_subscription_on_payment_success
from premium.webhook_logging import log_yookassa_create_response


def promo(request: HttpRequest) -> HttpResponse:
    """
    Страница с промо-предложением премиум-подписки на сервис.
    Доступна всем пользователям.
    """
    plans = (
        PremiumPlan.objects.filter(is_active=True)
        .exclude(price_month=0)
        .prefetch_related('features')
        .order_by('sort_order', 'pk')
    )

    return render(
        request,
        'premium/promo.html',
        context={
            'page_title': 'Премиум-подписка на сервис «Мои города»',
            'page_description': (
                'Выберите бесплатный или премиум-тариф на сервис «Мои города» '
                'и поддержите развитие проекта'
            ),
            'plans': plans,
        },
    )


@require_POST
def checkout(request: HttpRequest) -> HttpResponse:
    """
    Создаёт платёж в YooKassa и перенаправляет пользователя на страницу оплаты.
    """
    if not request.user.is_authenticated:
        return redirect(settings.LOGIN_URL)

    billing_period = request.POST.get('billing_period', PremiumSubscription.BillingPeriod.MONTHLY)
    plan_id = request.POST.get('plan_id')

    plan = None
    if plan_id is not None:
        try:
            plan = PremiumPlan.objects.get(pk=plan_id, is_active=True)
        except PremiumPlan.DoesNotExist:
            plan = None

    if plan is None:
        return redirect('premium_promo')

    if billing_period == PremiumSubscription.BillingPeriod.YEARLY:
        amount_value = plan.price_year
        period_label = 'на год'
    else:
        billing_period = PremiumSubscription.BillingPeriod.MONTHLY
        amount_value = plan.price_month
        period_label = 'на месяц'

    description = f'Тариф «{plan.name}» для пользователя {request.user.username} {period_label}'

    Configuration.account_id = settings.YOOKASSA_SHOP_ID
    Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

    return_url = request.build_absolute_uri(reverse('premium_my_subscription'))

    try:
        payment = Payment.create(
            {
                'amount': {
                    'value': f'{amount_value:.2f}',
                    'currency': plan.currency,
                },
                'confirmation': {
                    'type': 'redirect',
                    'return_url': return_url,
                },
                'capture': True,
                'description': description,
            },
            uuid.uuid4(),
        )
    except ApiError:
        return redirect('premium_promo')

    try:
        response_data = json.loads(payment.json())
    except (TypeError, ValueError):
        response_data = {}
    log_yookassa_create_response(request, payment.id, payment.status, response_data)

    subscription = PremiumSubscription.objects.create(
        user=request.user,
        plan=plan,
        billing_period=billing_period,
        status=PremiumSubscription.Status.PENDING,
        provider_payment_id=payment.id,
    )

    premium_payment = PremiumPayment.objects.create(
        user=request.user,
        subscription=subscription,
        plan=plan,
        yookassa_payment_id=payment.id,
        amount_value=amount_value,
        currency=plan.currency,
        billing_period=billing_period,
        description=description,
        status=PremiumPayment.Status(payment.status),
    )

    PremiumPaymentWebhookLog.objects.create(
        payment=premium_payment,
        status=payment.status,
        raw_payload=response_data,
    )

    request.session['premium_payment_return_id'] = str(premium_payment.pk)
    request.session['premium_payment_return_at'] = timezone.now().isoformat()

    confirmation_url = payment.confirmation.confirmation_url
    return redirect(confirmation_url)


def success(request: HttpRequest) -> HttpResponse:
    """
    Страница благодарности после успешной оплаты премиум-подписки.
    """
    return render(
        request,
        'premium/success.html',
        context={
            'page_title': 'Премиум-подписка оформлена',
            'page_description': 'Вы успешно оформили премиум-подписку на сервис «Мои города»',
        },
    )


def _sync_pending_payments(user) -> None:
    """
    Проверяет статус ожидающих платежей в YooKassa и активирует подписки при успешной оплате.
    Вызывается при возврате пользователя с страницы оплаты (вебхук может не дойти в локальной разработке).
    """
    Configuration.account_id = settings.YOOKASSA_SHOP_ID
    Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

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
        try:
            yookassa_payment = Payment.find_one(premium_payment.yookassa_payment_id)
        except ApiError:
            continue
        new_status = yookassa_payment.status
        if new_status == PremiumPayment.Status.SUCCEEDED:
            premium_payment.status = PremiumPayment.Status.SUCCEEDED
            premium_payment.save()
            if premium_payment.subscription is not None:
                activate_subscription_on_payment_success(premium_payment.subscription)
            break  # Обработали один платёж — достаточно
        if new_status == PremiumPayment.Status.CANCELED:
            premium_payment.status = PremiumPayment.Status.CANCELED
            premium_payment.save()
            break


@login_required
def my_subscription(request: HttpRequest) -> HttpResponse:
    """
    Страница с текущим тарифом подписки, датой окончания и списком платежей пользователя.
    """
    payment_result: str | None = None

    payment_id = request.session.pop('premium_payment_return_id', None)
    returned_at_str = request.session.pop('premium_payment_return_at', None)

    if payment_id and returned_at_str:
        try:
            returned_at = datetime.fromisoformat(returned_at_str)
            if (timezone.now() - returned_at).total_seconds() < 3600:
                _sync_pending_payments(request.user)
                premium_payment = PremiumPayment.objects.filter(
                    pk=payment_id,
                    user=request.user,
                ).first()
                if premium_payment:
                    if premium_payment.status == PremiumPayment.Status.SUCCEEDED:
                        payment_result = 'succeeded'
                    elif premium_payment.status == PremiumPayment.Status.CANCELED:
                        payment_result = 'canceled'
                    else:
                        payment_result = 'pending'
        except (ValueError, TypeError):
            pass

    payments = (
        PremiumPayment.objects.filter(user=request.user)
        .select_related('plan')
        .order_by('-created_at')
    )

    # Приостановленные и запланированные подписки с датами активации (с какого по какое число будут активны)
    paused_subscriptions: list[tuple[PremiumSubscription, datetime, datetime]] = []
    active_sub = (
        PremiumSubscription.objects.filter(
            user=request.user,
            status=PremiumSubscription.Status.ACTIVE,
        )
        .select_related('plan')
        .first()
    )
    now = timezone.now()
    if active_sub is not None and active_sub.expires_at is not None:
        # SCHEDULED и PAUSED: подписки в очереди после текущей
        future_subs = (
            PremiumSubscription.objects.filter(
                user=request.user,
                status__in=(
                    PremiumSubscription.Status.SCHEDULED,
                    PremiumSubscription.Status.PAUSED,
                ),
                expires_at__gt=now,
            )
            .select_related('plan')
            .order_by('expires_at')
        )
        next_start = active_sub.expires_at + timedelta(days=1)
        for sub in future_subs:
            if sub.expires_at is not None:
                paused_subscriptions.append((sub, next_start, sub.expires_at))
                next_start = sub.expires_at + timedelta(days=1)

    return render(
        request,
        'premium/my_subscription.html',
        context={
            'page_title': 'Моя подписка',
            'page_description': 'Текущий тариф и история платежей',
            'active_page': 'premium_my_subscription',
            'payments': payments,
            'payment_result': payment_result,
            'paused_subscriptions': paused_subscriptions,
        },
    )
