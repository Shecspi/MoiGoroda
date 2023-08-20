import environ

env = environ.Env()
environ.Env.read_env()


def general_settings(request):
    context = {
        'SITE_NAME': env('SITE_NAME'),
        'PROJECT_VERSION': env('PROJECT_VERSION'),
        'API_YANDEX_MAP': env('API_YANDEX_MAP'),
        'YANDEX_METRIKA': env('YANDEX_METRIKA'),
        'SUPPORT_EMAIL': env('DEFAULT_FROM_EMAIL')
    }

    return context
