from django.urls import include, path
from dmr.routing import Router

from geo_polygons.api import DownloadOSMPolygonController, GetOSMPolygonController

router = Router(
    'api/geo-polygons',
    [
        path(
            'polygon/<int:relation_id>/download/',
            DownloadOSMPolygonController.as_view(),
            name='api__geo_polygon_download',
        ),
        path('polygon/<int:relation_id>/', GetOSMPolygonController.as_view(), name='api__geo_polygon'),
    ],
)

urlpatterns = [
    path('', include(router.urls)),
]
