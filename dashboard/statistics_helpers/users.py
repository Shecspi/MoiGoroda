"""
Статистика пользователей (регистрации).
"""

from __future__ import annotations

from datetime import date

from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.functions.datetime import TruncDate

from dashboard.schemas import DailyStatistics
from dashboard.statistics_helpers.common import (
    _format_group_label,
    _get_group_trunc_function,
    _next_group_date,
    timezone,
)


def _collect_registrations_by_group(
    date_from: date,
    date_to: date,
    group_by: str,
) -> list[DailyStatistics]:
    trunc_fn = _get_group_trunc_function(group_by)
    queryset = (
        User.objects.filter(
            date_joined__date__range=[date_from, date_to],
        )
        .annotate(group_date=TruncDate(trunc_fn('date_joined', tzinfo=timezone.utc)))
        .values('group_date')
        .annotate(count=Count('id'))
        .order_by('group_date')
    )

    grouped_data = {item['group_date']: item['count'] for item in queryset}

    if not grouped_data:
        return []

    first_date = min(grouped_data.keys())
    last_date = max(grouped_data.keys())

    result: list[DailyStatistics] = []
    current_date = first_date
    while current_date <= last_date:
        result.append(
            DailyStatistics(
                label=_format_group_label(current_date, group_by),
                count=grouped_data.get(current_date, 0),
            )
        )
        current_date = _next_group_date(current_date, group_by)

    return result


__all__ = ['_collect_registrations_by_group']

