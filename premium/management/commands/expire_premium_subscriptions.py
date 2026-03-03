"""
Команда для перевода просроченных премиум-подписок в статус «Истекла».
Предназначена для ежедневного запуска по cron.
"""

import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from premium.models import PremiumSubscription

logger = logging.getLogger('premium.cron')


class Command(BaseCommand):
    help = 'Переводит премиум-подписки с истёкшим сроком в статус «Истекла».'

    def handle(self, *args: object, **options: object) -> None:
        now = timezone.now()
        qs = PremiumSubscription.objects.filter(
            status=PremiumSubscription.Status.ACTIVE,
            expires_at__lt=now,
        )
        ids = list(qs.values_list('pk', flat=True))
        expired_user_ids = list(qs.values_list('user_id', flat=True).distinct())
        count = qs.update(status=PremiumSubscription.Status.EXPIRED)

        if count:
            logger.info(f'Истекло подписок: {count}, ID: {[str(pk) for pk in ids]}')

        # Для каждого пользователя, у которого истекла подписка:
        # 1) активировать запланированную (SCHEDULED), если пришло время;
        # 2) иначе — приостановленную (PAUSED) с ближайшим сроком истечения.
        for user_id in expired_user_ids:
            next_scheduled = (
                PremiumSubscription.objects.filter(
                    user_id=user_id,
                    status=PremiumSubscription.Status.SCHEDULED,
                    started_at__lte=now,
                )
                .order_by('started_at')
                .first()
            )
            if next_scheduled is not None:
                next_scheduled.status = PremiumSubscription.Status.ACTIVE
                next_scheduled.save()
                logger.info(f'Активирована запланированная подписка: {next_scheduled.pk}')
            else:
                next_paused = (
                    PremiumSubscription.objects.filter(
                        user_id=user_id,
                        status=PremiumSubscription.Status.PAUSED,
                        expires_at__gt=now,
                    )
                    .order_by('expires_at')
                    .first()
                )
                if next_paused is not None:
                    next_paused.status = PremiumSubscription.Status.ACTIVE
                    next_paused.save()
                    logger.info(f'Активирована приостановленная подписка: {next_paused.pk}')

        if not count:
            logger.info('Нет подписок для перевода в «Истекла».')
