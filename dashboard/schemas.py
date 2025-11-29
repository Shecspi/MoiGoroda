import msgspec


class Quantity(msgspec.Struct):
    count: int


class DailyStatistics(msgspec.Struct):
    date: str
    count: int


class UserStatistics(msgspec.Struct):
    username: str
    count: int


class DaysPath(msgspec.Struct):
    days: int
