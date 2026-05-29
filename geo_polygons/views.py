from django.http import HttpRequest
from django.views.generic import TemplateView


class GeoPolygonsViewer(TemplateView):
    template_name = 'geo_polygons/page.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        return super().get(request, *args, **kwargs)
