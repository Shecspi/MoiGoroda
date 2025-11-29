import msgspec


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
