from pydantic import BaseModel


class Coordinates(BaseModel):
    lat: float
    lon: float


class City(BaseModel):
    title: str
    coordinates: Coordinates


class OwnCities(BaseModel):
    cities: list[City]


class SubscriptionCities(BaseModel):
    username: str
    cities: list[City]


class CitiesResponse(BaseModel):
    own: OwnCities | None = None
    subscriptions: SubscriptionCities | None = None
