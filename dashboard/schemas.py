import msgspec
from datetime import date


class Quantity(msgspec.Struct):
    count: int


class DailyStatistics(msgspec.Struct):
    label: str
    count: int


class UserStatistics(msgspec.Struct):
    label: str
    count: int


class DaysPath(msgspec.Struct):
    days: int


class RegistrationsRangeQuery(msgspec.Struct):
    date_from: date
    date_to: date
    group_by: str = 'day'


class RegistrationsComparisonQuery(msgspec.Struct):
    date_from: date
    date_to: date


class PeriodComparisonStatistics(msgspec.Struct):
    current_count: int
    previous_count: int
    delta: int
    delta_percent: float
