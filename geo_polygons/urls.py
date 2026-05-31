from django.urls import path

from geo_polygons.views import GeoPolygonsViewer

urlpatterns = [
    path('', GeoPolygonsViewer.as_view(), name='geo-polygons'),
]
