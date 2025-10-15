from django.apps import AppConfig


class SubscribeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'subscribe'

    def ready(self) -> None:
        # Импортируем все модели, чтобы Django их зарегистрировал
        pass
