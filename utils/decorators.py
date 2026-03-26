from http import HTTPStatus

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse

from dmr import ResponseSpec
from dmr.decorators import wrap_middleware
from dmr.plugins.msgspec import MsgspecSerializer
from dmr.response import build_response


@wrap_middleware(
    user_passes_test(lambda user: user.is_superuser),
    ResponseSpec(
        return_type=dict[str, str],
        status_code=HTTPStatus.FOUND,
    ),
)
def is_superuser_json(response: HttpResponse) -> HttpResponse:
    """
    Декоратор, который оборачивает представление для проверки прав доступа пользователя.
    Если попытка доступа осуществляется не привилегированным пользователем и возвращается статус 302 (FOUND),
    декоратор преобразует ответ в JSON с кодом 401 (UNAUTHORIZED) и сообщением о том, что доступ разрешён
    только администраторам.

    Аргументы:
        response (HttpResponse): HTTP-ответ, который необходимо обработать.

    Возвращает:
        HttpResponse: Оригинальный ответ, если редирект не требуется,
        либо JSON-ответ с ошибкой, если пользователь не имеет прав администратора.
    """
    if response.status_code == HTTPStatus.FOUND:
        return build_response(
            MsgspecSerializer,
            raw_data={'detail': 'Access restricted to administrators only.'},
            status_code=HTTPStatus.UNAUTHORIZED,
        )

    return response
