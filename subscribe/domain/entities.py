from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum, auto

from pydantic import BaseModel


class Action(StrEnum):
    subscribe = auto()
    unsubscribe = auto()


class SubscriptionRequest(BaseModel):
    from_id: int
    to_id: int
    action: Action


class DeleteSubscriberRequest(BaseModel):
    user_id: int


@dataclass
class Notification:
    id: int
    city_id: int
    city_title: str
    region_id: int
    region_title: str
    country_code: str
    country_title: str
    is_read: bool
    sender_id: int
    sender_username: str
    read_at: datetime | None = None
