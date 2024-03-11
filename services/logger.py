import logging

from django.http import HttpRequest


def info(request: HttpRequest, message: str, logger_name: str = "base") -> None:
    """
    Формирует сообщение, которое будет записано в логи, на основе текста 'message'.
    По-умолчанию используется базовый логгер 'base', но в случае необходимости его можно переопределить.
    """
    logger = logging.getLogger(logger_name)
    logger.info(
        f"{message}   {request.get_full_path()}",
        extra={
            "IP": __get_client_ip(request),
            "user": request.user.username or "<GUEST>",
        },
    )


def warning(request: HttpRequest, message: str, logger_name: str = "base") -> None:
    """
    Формирует сообщение уровня Warning, которое будет записано в логи, на основе текста 'message'.
    По-умолчанию используется базовый логгер 'base', но в случае необходимости его можно переопределить.
    """
    logger = logging.getLogger(logger_name)
    logger.warning(
        f"{message}   {request.get_full_path()}",
        extra={
            "IP": __get_client_ip(request),
            "user": request.user.username or "<GUEST>",
        },
    )


def __get_client_ip(request: HttpRequest) -> str:
    """
    Возвращает IP-адрес пользователя.
    """
    try:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
    except Exception:
        return "X.X.X.X"
