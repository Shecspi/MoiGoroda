# mypy: disable-error-code="no-untyped-def,no-any-return,attr-defined,return-value"
import pytest
from django.contrib.auth import get_user_model

from subscribe.infrastructure.django_repository import DjangoUserRepository

User = get_user_model()


@pytest.mark.django_db
def test_returns_true_for_existing_user() -> None:
    repo = DjangoUserRepository()
    user = User.objects.create(username='integration_user')

    assert repo.exists(user.id) is True


@pytest.mark.django_db
def test_returns_false_for_non_existing_user() -> None:
    repo = DjangoUserRepository()
    assert repo.exists(999999) is False


@pytest.mark.django_db
def test_returns_false_for_deleted_user() -> None:
    repo = DjangoUserRepository()
    user = User.objects.create(username='to_delete')
    user_id = user.id
    user.delete()

    assert repo.exists(user_id) is False


@pytest.mark.django_db
@pytest.mark.parametrize('user_id', [0, -1, 10**9])
def test_returns_false_for_invalid_ids(user_id) -> None:
    repo = DjangoUserRepository()
    assert repo.exists(user_id) is False
