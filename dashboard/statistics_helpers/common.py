"""
Общие helper-функции для dashboard-статистики.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from typing import Any

from django.db.models import Count, QuerySet
from django.db.models.functions.datetime import TruncDate
from django.db.models.functions.datetime import TruncDay, TruncMonth, TruncWeek

from dashboard.schemas import DailyStatistics, PeriodComparisonStatistics


def _get_group_trunc_function(group_by: str) -> type[TruncDay] | type[TruncWeek] | type[TruncMonth]:
    if group_by == 'day':
        return TruncDay
    if group_by == 'week':
        return TruncWeek
    if group_by == 'month':
        return TruncMonth
    raise ValueError('group_by must be one of: day, week, month')


def _format_group_label(group_date: date, group_by: str) -> str:
    if group_by == 'day':
        return group_date.strftime('%d.%m.%Y')
    if group_by == 'week':
        iso_year, iso_week, _ = group_date.isocalendar()
        return f'{iso_week:02d}.{iso_year}'
    return group_date.strftime('%m.%Y')


def _next_group_date(group_date: date, group_by: str) -> date:
    if group_by == 'day':
        return group_date + timedelta(days=1)
    if group_by == 'week':
        return group_date + timedelta(weeks=1)

    # Переход на первый день следующего месяца
    if group_date.month == 12:
        return date(group_date.year + 1, 1, 1)
    return date(group_date.year, group_date.month + 1, 1)


def _normalize_group_start(group_date: date, group_by: str) -> date:
    if group_by == 'day':
        return group_date
    if group_by == 'week':
        return group_date - timedelta(days=group_date.weekday())
    return date(group_date.year, group_date.month, 1)


def build_blog_overview_period(now_date: date, days: int) -> tuple[date, date, date, date]:
    """
    Возвращает границы для:
    - текущего периода: [date_from, date_to] (включительно)
    - предыдущего периода: [previous_date_from, previous_date_to] (равной длины)
    """
    date_to = now_date
    date_from = date_to - timedelta(days=days - 1)
    previous_date_to = date_from - timedelta(days=1)
    previous_date_from = previous_date_to - timedelta(days=days - 1)
    return date_from, date_to, previous_date_from, previous_date_to


def build_datetime_range(date_from: date, date_to: date) -> tuple[datetime, datetime]:
    """
    Возвращает полуинтервал [start, end) в UTC для диапазона дат [date_from, date_to].
    """
    start = datetime.combine(date_from, time.min, tzinfo=timezone.utc)
    end = datetime.combine(date_to + timedelta(days=1), time.min, tzinfo=timezone.utc)
    return start, end


def build_grouped_daily_statistics(
    *,
    base_queryset: QuerySet[Any],
    datetime_field: str,
    date_from: date,
    date_to: date,
    group_by: str,
    count_field: str = 'id',
) -> list[DailyStatistics]:
    trunc_fn = _get_group_trunc_function(group_by)
    dt_from, dt_to = build_datetime_range(date_from, date_to)
    queryset = (
        base_queryset.filter(**{f'{datetime_field}__gte': dt_from, f'{datetime_field}__lt': dt_to})
        .annotate(group_date=TruncDate(trunc_fn(datetime_field, tzinfo=timezone.utc)))
        .values('group_date')
        .annotate(count=Count(count_field))
        .order_by('group_date')
    )
    grouped_data = {item['group_date']: item['count'] for item in queryset}

    result: list[DailyStatistics] = []
    current_date = _normalize_group_start(date_from, group_by)
    while current_date <= date_to:
        result.append(
            DailyStatistics(
                label=_format_group_label(current_date, group_by),
                count=grouped_data.get(current_date, 0),
            )
        )
        current_date = _next_group_date(current_date, group_by)

    return result


def build_period_comparison_stats(current_count: int, previous_count: int) -> PeriodComparisonStatistics:
    delta = current_count - previous_count
    delta_percent = 0.0 if previous_count == 0 else round((delta / previous_count) * 100, 2)
    return PeriodComparisonStatistics(
        current_count=current_count,
        previous_count=previous_count,
        delta=delta,
        delta_percent=delta_percent,
    )


__all__ = [
    '_get_group_trunc_function',
    '_format_group_label',
    '_next_group_date',
    'build_blog_overview_period',
    'build_datetime_range',
    'build_grouped_daily_statistics',
    'build_period_comparison_stats',
    'timezone',
]

