from django.urls import include
from dmr.routing import Router, path

from analytics.api import ModeSwitchLogController


router = Router(
    'api/analytics',
    [
        path('mode-switch/', ModeSwitchLogController.as_view(), name='api__mode_switch'),
    ],
)

urlpatterns = [
    path('', include(router.urls)),
]
