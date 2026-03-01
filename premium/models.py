"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from __future__ import annotations

from decimal import Decimal
import uuid

from django.contrib.auth.models import User
from django.db import models
from django.db.models import CASCADE, PROTECT, JSONField


class PremiumPlan(models.Model):
    """
    Тариф премиум-подписки.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='ID',
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Системное имя тарифа',
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Название тарифа',
    )
    description = models.TextField(
        verbose_name='Описание тарифа',
        blank=True,
    )
    price_month = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Стоимость в месяц',
    )
    price_year = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Стоимость в год',
    )
    currency = models.CharField(
        max_length=3,
        verbose_name='Валюта',
        default='RUB',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен',
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name='Порядок сортировки',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления',
    )

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = 'Тариф премиум-подписки'
        verbose_name_plural = 'Тарифы премиум-подписки'

    def __str__(self) -> str:
        return self.name


class PremiumPlanFeature(models.Model):
    """
    Отдельное преимущество тарифа премиум-подписки.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='ID',
    )
    plan = models.ForeignKey(
        PremiumPlan,
        on_delete=CASCADE,
        related_name='features',
        verbose_name='Тариф',
    )
    text = models.CharField(
        max_length=255,
        verbose_name='Преимущество',
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name='Порядок сортировки',
    )

    class Meta:
        ordering = ['sort_order', 'id']
        verbose_name = 'Преимущество тарифа'
        verbose_name_plural = 'Преимущества тарифа'

    def __str__(self) -> str:
        return self.text


class PremiumSubscription(models.Model):
    """
    Подписка пользователя на премиум-доступ.
    """

    class BillingPeriod(models.TextChoices):
        MONTHLY = 'monthly', '1 месяц'
        YEARLY = 'yearly', '1 год'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидает активации'
        ACTIVE = 'active', 'Активна'
        PAUSED = 'paused', 'Приостановлена'
        CANCELED = 'canceled', 'Отменена'
        EXPIRED = 'expired', 'Истекла'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='ID',
    )
    user = models.ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='premium_subscriptions',
        verbose_name='Пользователь',
    )
    plan = models.ForeignKey(
        PremiumPlan,
        on_delete=PROTECT,
        related_name='subscriptions',
        verbose_name='Тариф',
    )
    billing_period = models.CharField(
        max_length=10,
        choices=BillingPeriod.choices,
        verbose_name='Период оплаты',
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Статус подписки',
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата начала',
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата окончания',
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата отмены',
    )
    auto_renew = models.BooleanField(
        default=False,
        verbose_name='Автопродление',
    )
    provider_payment_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='ID платежа в YooKassa',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления',
    )

    class Meta:
        verbose_name = 'Премиум-подписка пользователя'
        verbose_name_plural = 'Премиум-подписки пользователей'
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                condition=models.Q(status='active'),
                name='unique_active_premium_subscription_per_user',
            )
        ]

    def __str__(self) -> str:
        return f'{self.user.username} — {self.plan.name} ({self.get_billing_period_display()})'


class PremiumPayment(models.Model):
    """
    Платёж в YooKassa, связанный с премиум-подпиской.
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидает оплаты'
        WAITING_FOR_CAPTURE = 'waiting_for_capture', 'Ожидает списания'
        SUCCEEDED = 'succeeded', 'Успешно оплачен'
        CANCELED = 'canceled', 'Отменён'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='ID',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='premium_payments',
        verbose_name='Пользователь',
    )
    subscription = models.ForeignKey(
        PremiumSubscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name='Подписка',
    )
    plan = models.ForeignKey(
        PremiumPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name='Тариф',
    )

    yookassa_payment_id = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='ID платежа в YooKassa',
    )
    amount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Сумма',
    )
    currency = models.CharField(
        max_length=3,
        verbose_name='Валюта',
        default='RUB',
    )
    billing_period = models.CharField(
        max_length=10,
        choices=PremiumSubscription.BillingPeriod.choices,
        verbose_name='Период оплаты',
    )
    description = models.CharField(
        max_length=255,
        verbose_name='Описание',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Статус платежа',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления',
    )

    class Meta:
        verbose_name = 'Платёж премиум-подписки'
        verbose_name_plural = 'Платежи премиум-подписки'
        indexes = [
            models.Index(fields=['yookassa_payment_id']),
            models.Index(fields=['user']),
        ]

    def __str__(self) -> str:
        return f'{self.yookassa_payment_id} — {self.get_status_display()}'

    @property
    def amount(self) -> Decimal:
        return self.amount_value


class PremiumPaymentWebhookLog(models.Model):
    """
    Лог входящих уведомлений вебхука YooKassa по платежу.
    Для одного платежа может быть несколько записей (по мере смены статуса).
    """

    payment = models.ForeignKey(
        PremiumPayment,
        on_delete=models.CASCADE,
        related_name='webhook_logs',
        verbose_name='Платёж',
    )
    status = models.CharField(
        max_length=20,
        verbose_name='Статус в уведомлении',
    )
    raw_payload: JSONField = JSONField(
        verbose_name='Входящий JSON',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата получения',
    )

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Лог вебхука платежа'
        verbose_name_plural = 'Логи вебхуков платежей'

    def __str__(self) -> str:
        return f'{self.payment.yookassa_payment_id} — {self.status} ({self.created_at})'

