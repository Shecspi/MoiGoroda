import logging

from django.http import HttpRequest


class LoggingMixin:
    def set_message(
            self,
            request: HttpRequest,
            message: str,
            logger_name: str = 'base'
    ):
        """
        Формирует сообщение, которое будет записано в логи, на основе текста 'message'.
        По-умолчанию используется базовый логгер 'base', но в случае необходимости его можно переопределить.
        """
        logger = logging.getLogger(logger_name)
        logger.info(
            f'{message}   {request.get_full_path()}',
            extra={
                'IP': self.__get_client_ip(request),
                'user': request.user.username or '<GUEST>'
            }
        )

    @staticmethod
    def __get_client_ip(request: HttpRequest):
        """
        Возвращает IP-адрес пользователя.
        """
        try:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            return ip
        except:
            return 'X.X.X.X'
