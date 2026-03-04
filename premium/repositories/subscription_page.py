"""Репозиторий данных для страницы «Моя подписка»."""

from __future__ import annotations

from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.utils import timezone

from premium.models import PremiumPayment, PremiumSubscription


class SubscriptionPageRepository:
    """Репозиторий данных для страницы «Моя подписка»."""

    def get_payments_for_user(self, user: User) -> list[PremiumPayment]:
        """Возвращает платежи пользователя, отсортированные по дате (новые первые)."""
        return list(
            PremiumPayment.objects.filter(user=user)
            .select_related('plan')
            .order_by('-created_at')
        )

    def get_active_subscription(
        self, user: User
    ) -> PremiumSubscription | None:
        """Возвращает активную подписку пользователя или None."""
        return (
            PremiumSubscription.objects.filter(
                user=user,
                status=PremiumSubscription.Status.ACTIVE,
            )
            .select_related('plan')
            .prefetch_related('plan__features')
            .first()
        )

    def get_paused_subscriptions(
        self,
        user: User,
        active_subscription: PremiumSubscription | None,
    ) -> list[tuple[PremiumSubscription, datetime, datetime]]:
        """
        Возвращает приостановленные и запланированные подписки с датами активации.
        Каждый элемент — (подписка, дата_начала, дата_окончания).
        """
        if active_subscription is None or active_subscription.expires_at is None:
            return []

        now = timezone.now()
        future_subs = (
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

        result: list[tuple[PremiumSubscription, datetime, datetime]] = []
        next_start = active_subscription.expires_at + timedelta(days=1)
        for sub in future_subs:
            if sub.expires_at is not None:
                result.append((sub, next_start, sub.expires_at))
                next_start = sub.expires_at + timedelta(days=1)
        return result

    def get_payment_by_id_and_user(
        self, payment_id: str, user: User
    ) -> PremiumPayment | None:
        """Возвращает платёж по ID и пользователю или None."""
        return PremiumPayment.objects.filter(
            pk=payment_id,
            user=user,
        ).first()
