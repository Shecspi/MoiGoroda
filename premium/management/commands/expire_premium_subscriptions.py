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
        count = qs.update(status=PremiumSubscription.Status.EXPIRED)

        if count:
            logger.info(f'Истекло подписок: {count}, ID: {[str(pk) for pk in ids]}')
        else:
            logger.info('Нет подписок для перевода в «Истекла».')
