"""
Общие helper-функции для dashboard-статистики.
"""

from __future__ import annotations

from datetime import date, timedelta, timezone

from django.db.models.functions.datetime import TruncDay, TruncMonth, TruncWeek

from dashboard.schemas import PeriodComparisonStatistics


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
    'build_period_comparison_stats',
    'timezone',
]

