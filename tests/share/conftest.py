import pytest

from account.models import ShareSettings


def create_user(user_id: int, django_user_model):
    return django_user_model.objects.create_user(
        id=user_id, username=f'username{user_id}', password='password'
    )


def create_permissions_in_db(user_id, permissions):
    setting = ShareSettings(
        user_id=user_id,
        can_share=permissions[0],
        can_share_dashboard=permissions[1],
        can_share_city_map=permissions[2],
        can_share_region_map=permissions[3],
    )
    setting.save()


@pytest.fixture
def setup(client, django_user_model):
    user1 = create_user(1, django_user_model)
    user2 = create_user(2, django_user_model)
