# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

from __future__ import annotations

from dataclasses import dataclass, field

from django.utils import timezone

from premium.models import PremiumSubscription
from services.morphology import plural_by_number


def format_days_text(days: int) -> str:
    return f'{days} {plural_by_number("день", days)}'


@dataclass(frozen=True)
class SubscriptionManagementRow:
    subscription: PremiumSubscription
    previous_subscriptions: list[PremiumSubscription] = field(default_factory=list)
    days_until_expired: int | None = None
    days_until_expired_text: str = ''
    days_since_expired: int | None = None
    days_since_expired_text: str = ''


@dataclass(frozen=True)
class SubscriptionManagementPageData:
    active_subscriptions: list[SubscriptionManagementRow]
    expired_subscriptions: list[SubscriptionManagementRow]


class SubscriptionManagementService:
    def get_page_data(self) -> SubscriptionManagementPageData:
        today = timezone.now().date()
        historical_statuses = (
            PremiumSubscription.Status.EXPIRED,
            PremiumSubscription.Status.CANCELED,
            PremiumSubscription.Status.INTERRUPTED,
        )
        active_user_ids = set(
            PremiumSubscription.objects.filter(
                status=PremiumSubscription.Status.ACTIVE,
            ).values_list('user_id', flat=True)
        )

        history_by_user: dict[int, list[PremiumSubscription]] = {}
        for subscription in (
            PremiumSubscription.objects.filter(status__in=historical_statuses)
            .select_related('user', 'plan')
            .order_by('user_id', '-expires_at', '-created_at')
        ):
            history_by_user.setdefault(subscription.user_id, []).append(subscription)

        active_subscriptions = []
        for subscription in (
            PremiumSubscription.objects.filter(
                status=PremiumSubscription.Status.ACTIVE,
            )
            .select_related('user', 'plan')
            .order_by('expires_at', 'user__username')
        ):
            days_until_expired = None
            if subscription.expires_at is not None:
                days_until_expired = max((subscription.expires_at.date() - today).days, 0)
            active_subscriptions.append(
                SubscriptionManagementRow(
                    subscription=subscription,
                    previous_subscriptions=history_by_user.get(subscription.user_id, []),
                    days_until_expired=days_until_expired,
                    days_until_expired_text=(
                        format_days_text(days_until_expired)
                        if days_until_expired is not None
                        else ''
                    ),
                )
            )
        expired_subscriptions = []
        latest_expired_by_user: dict[int, PremiumSubscription] = {}
        for subscription in (
            PremiumSubscription.objects.filter(
                status=PremiumSubscription.Status.EXPIRED,
                expires_at__isnull=False,
            )
            .exclude(user_id__in=active_user_ids)
            .select_related('user', 'plan')
            .order_by('user_id', '-expires_at', '-created_at')
        ):
            latest_expired_by_user.setdefault(subscription.user_id, subscription)

        for subscription in sorted(
            latest_expired_by_user.values(),
            key=lambda sub: (sub.expires_at is None, sub.expires_at),
            reverse=True,
        ):
            assert subscription.expires_at is not None
            days_since_expired = max((today - subscription.expires_at.date()).days, 0)
            previous_subscriptions = [
                item
                for item in history_by_user.get(subscription.user_id, [])
                if item.pk != subscription.pk
            ]
            expired_subscriptions.append(
                SubscriptionManagementRow(
                    subscription=subscription,
                    previous_subscriptions=previous_subscriptions,
                    days_since_expired=days_since_expired,
                    days_since_expired_text=format_days_text(days_since_expired),
                )
            )
        return SubscriptionManagementPageData(
            active_subscriptions=active_subscriptions,
            expired_subscriptions=expired_subscriptions,
        )
