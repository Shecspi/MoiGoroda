"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from __future__ import annotations

from typing import cast

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from django.contrib.auth.models import User

from premium.models import PremiumPlan, PremiumSubscription
from premium.services.checkout import CheckoutService
from premium.services.subscription_page import SubscriptionPageService
from premium.webhook.logging import log_yookassa_create_response


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
        )

    if result.success:
        request.session['premium_payment_return_id'] = result.payment_id

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


@login_required
def my_subscription(request: HttpRequest) -> HttpResponse:
    """
    Страница с текущим тарифом подписки, датой окончания и списком платежей пользователя.
    """
    payment_return_id = request.session.pop('premium_payment_return_id', None)
    page_data = SubscriptionPageService().get_page_data(
        user=cast(User, request.user),
        payment_return_id=payment_return_id,
    )

    return render(
        request,
        'premium/my_subscription.html',
        context={
            'page_title': 'Моя подписка',
            'page_description': 'Текущий тариф и история платежей',
            'active_page': 'premium_my_subscription',
            'payments': page_data.payments,
            'active_subscription': page_data.active_subscription,
            'paused_subscriptions': page_data.paused_subscriptions,
            'payment_result': page_data.payment_result,
        },
    )
