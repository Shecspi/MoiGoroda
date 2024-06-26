from pydantic import BaseModel


class Coordinates(BaseModel):
    lat: float
    lon: float


class City(BaseModel):
    title: str
    coordinates: Coordinates


class SubscriptionCities(BaseModel):
    username: str
    cities: list[City]


class CitiesResponse(BaseModel):
    own: list[City] | None = None
    subscriptions: list[SubscriptionCities] | None = None
