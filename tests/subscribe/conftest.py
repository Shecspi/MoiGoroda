import pytest

from django.contrib.auth.models import User

from account.models import ShareSettings
from subscribe.models import Subscribe
from tests.create_db import create_user, create_superuser


def create_permissions_in_db(user_id, permissions):
    setting = ShareSettings(
        user_id=user_id,
        can_share=permissions[0],
        can_share_dashboard=permissions[1],
        can_share_city_map=permissions[2],
        can_share_region_map=permissions[3],
        can_subscribe=permissions[4],
    )
    setting.save()


def create_subscription(subscribe_from_id: int, subscribe_to_id: int) -> None:
    subscription = Subscribe(subscribe_from_id=subscribe_from_id, subscribe_to_id=subscribe_to_id)
    subscription.save()


@pytest.fixture
def setup(client, django_user_model):
    create_user(django_user_model, 1)
    create_user(django_user_model, 2)
    create_superuser(django_user_model, 3)
