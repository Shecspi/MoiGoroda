from pydantic import BaseModel
from pydantic.types import conint


class Coordinates(BaseModel):
    lat: float
    lon: float


class City(BaseModel):
    id: int
    title: str
    coordinates: Coordinates


class SubscriptionCities(BaseModel):
    username: str
    cities: list[City]


class CitiesResponse(BaseModel):
    own: list[City] | None = None
    subscriptions: list[SubscriptionCities] | None = None


class UserIds(BaseModel):
    """
    Формат получаемых JSON-данных при запросе списка посещённых городов.
    ids - идентификаторы пользователей, для которых необходимо вернуть список городов.
    """

    ids: list[conint(gt=0)]
