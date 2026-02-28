"""
Админка для управления тарифами и подписками премиум-доступа.
"""

from __future__ import annotations

from django.contrib import admin

from premium.models import (
    PremiumPayment,
    PremiumPaymentWebhookLog,
    PremiumPlan,
    PremiumPlanFeature,
    PremiumSubscription,
)


class PremiumPlanFeatureInline(admin.TabularInline):
    model = PremiumPlanFeature
    extra = 1
    fields = ('text', 'sort_order')
    ordering = ('sort_order', 'id')


@admin.register(PremiumPlan)
class PremiumPlanAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
        'price_month',
        'price_year',
        'currency',
        'is_active',
        'sort_order',
    )
    list_filter = ('is_active', 'currency')
    search_fields = ('name', 'slug')
    ordering = ('sort_order', 'name')
    inlines = [PremiumPlanFeatureInline]


@admin.register(PremiumSubscription)
class PremiumSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'plan',
        'billing_period',
        'status',
        'started_at',
        'expires_at',
        'created_at',
    )
    list_filter = ('status', 'billing_period', 'plan')
    search_fields = ('user__username', 'user__email', 'plan__name')
    autocomplete_fields = ('plan',)
    ordering = ('-created_at',)


class PremiumPaymentWebhookLogInline(admin.TabularInline):
    model = PremiumPaymentWebhookLog
    extra = 0
    fields = ('status', 'created_at')
    readonly_fields = ('status', 'created_at')
    ordering = ('-created_at',)
    show_change_link = True
    can_delete = True
    max_num = 0

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(PremiumPaymentWebhookLog)
class PremiumPaymentWebhookLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('payment__yookassa_payment_id',)
    readonly_fields = ('payment', 'status', 'raw_payload', 'created_at')
    ordering = ('-created_at',)

    def has_add_permission(self, request):
        return False


@admin.register(PremiumPayment)
class PremiumPaymentAdmin(admin.ModelAdmin):
    list_display = (
        'yookassa_payment_id',
        'user',
        'plan',
        'billing_period',
        'amount_value',
        'currency',
        'status',
        'created_at',
    )
    list_filter = ('status', 'billing_period', 'currency', 'plan')
    search_fields = ('yookassa_payment_id', 'user__username', 'user__email')
    autocomplete_fields = ('subscription', 'plan')
    ordering = ('-created_at',)
    inlines = [PremiumPaymentWebhookLogInline]
