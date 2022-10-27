import environ

env = environ.Env()
environ.Env.read_env()


def general_settings(request):
    context = {
        'SITE_NAME': env('SITE_NAME'),

        'API_YANDEX_MAP': env('API_YANDEX_MAP')
    }

    return context
