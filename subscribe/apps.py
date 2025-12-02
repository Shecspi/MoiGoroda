"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.apps import AppConfig


class SubscribeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'subscribe'
    verbose_name = 'Подписки'

    def ready(self) -> None:
        # Импортируем все модели, чтобы Django их зарегистрировал
        pass
