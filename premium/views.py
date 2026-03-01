"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from __future__ import annotations

import json
import uuid

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from yookassa import Configuration, Payment  # type: ignore[import-untyped]

from premium.models import (
    PremiumPayment,
    PremiumPaymentWebhookLog,
    PremiumPlan,
    PremiumSubscription,
)
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

    user_label = request.user.username if request.user.is_authenticated else 'гость'
    description = f'Тариф «{plan.name}» для пользователя {user_label} {period_label}'

    Configuration.account_id = settings.YOOKASSA_SHOP_ID
    Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

    return_url = request.build_absolute_uri(reverse('premium_success'))

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


@login_required
def my_subscription(request: HttpRequest) -> HttpResponse:
    """
    Страница с текущим тарифом подписки, датой окончания и списком платежей пользователя.
    """
    payments = (
        PremiumPayment.objects.filter(user=request.user)
        .select_related('plan')
        .order_by('-created_at')
    )

    return render(
        request,
        'premium/my_subscription.html',
        context={
            'page_title': 'Моя подписка',
            'page_description': 'Текущий тариф и история платежей',
            'active_page': 'premium_my_subscription',
            'payments': payments,
        },
    )
