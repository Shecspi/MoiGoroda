import os
from django.http import HttpRequest, HttpResponse
from prometheus_client import CollectorRegistry, generate_latest, multiprocess, CONTENT_TYPE_LATEST


def prometheus_metrics_view(request: HttpRequest) -> HttpResponse:
    """
    Выводит метрики в мультипроцессном режиме (для Gunicorn).
    """
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)  # type: ignore[no-untyped-call]
    data = generate_latest(registry)
    return HttpResponse(data, content_type=CONTENT_TYPE_LATEST)
