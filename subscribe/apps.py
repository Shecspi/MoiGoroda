from django.apps import AppConfig


class SubscribeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'subscribe'

    def ready(self):
        # Импортируем все модели, чтобы Django их зарегистрировал
        import subscribe.infrastructure.models
        import subscribe.infrastructure.models
