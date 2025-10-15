# mypy: disable-error-code="no-untyped-def,no-any-return,attr-defined,return-value"
from subscribe.infrastructure.django_repository import DjangoUserRepository


def test_exists_returns_true_when_user_found(mocker) -> None:
    repo = DjangoUserRepository()

    mock_queryset = mocker.Mock()
    mock_queryset.exists.return_value = True

    mock_filter = mocker.patch(
        'subscribe.infrastructure.django_repository.User.objects.filter',
        return_value=mock_queryset,
    )

    result = repo.exists(123)

    assert result is True
    mock_filter.assert_called_once_with(pk=123)
    mock_queryset.exists.assert_called_once_with()


def test_exists_returns_false_when_user_not_found(mocker) -> None:
    repo = DjangoUserRepository()

    mock_queryset = mocker.Mock()
    mock_queryset.exists.return_value = False

    mock_filter = mocker.patch(
        'subscribe.infrastructure.django_repository.User.objects.filter',
        return_value=mock_queryset,
    )

    result = repo.exists(999)

    assert result is False
    mock_filter.assert_called_once_with(pk=999)
    mock_queryset.exists.assert_called_once_with()
