"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import cast

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from yookassa import Configuration, Payment  # type: ignore[import-untyped]
from yookassa.domain.exceptions import ApiError  # type: ignore[import-untyped]

from django.contrib.auth.models import User

from premium.models import (
    PremiumPayment,
    PremiumPlan,
    PremiumSubscription,
)
from premium.service import CheckoutService
from premium.webhook import activate_subscription_on_payment_success
from premium.webhook_logging import log_yookassa_create_response


def promo(request: HttpRequest) -> HttpResponse:
    """
    Страница с промо-предложением премиум-подписки на сервис.
    Доступна всем пользователям.
    """
    plans = (
        PremiumPlan.objects.filter(is_active=True)
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


@login_required
@require_POST
def checkout(request: HttpRequest) -> HttpResponse:
    """
    Создаёт платёж в YooKassa и перенаправляет пользователя на страницу оплаты.
    """
    billing_period = request.POST.get('billing_period', PremiumSubscription.BillingPeriod.MONTHLY)
    if billing_period not in (
        PremiumSubscription.BillingPeriod.MONTHLY,
        PremiumSubscription.BillingPeriod.YEARLY,
    ):
        return redirect(request.build_absolute_uri(reverse('premium_promo')))

    plan_id = request.POST.get('plan_id') or ''
    return_url = request.build_absolute_uri(reverse('premium_my_subscription'))
    promo_url = request.build_absolute_uri(reverse('premium_promo'))

    result = CheckoutService().create_checkout(
        user=cast(User, request.user),
        plan_id=plan_id,
        billing_period=billing_period,
        return_url=return_url,
        promo_url=promo_url,
    )

    if result.success and result.raw_response is not None:
        log_yookassa_create_response(
            request,
            result.yookassa_payment_id,
            result.yookassa_status,
            result.raw_response,
        )

    if result.success:
        request.session['premium_payment_return_id'] = result.payment_id
        request.session['premium_payment_return_at'] = timezone.now().isoformat()

    return redirect(result.redirect_url)


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
