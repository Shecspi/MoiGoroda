from django.urls import path
from analytics.views import prometheus_metrics_view

urlpatterns = [
    path('', prometheus_metrics_view, name='prometheus-metrics'),
]
