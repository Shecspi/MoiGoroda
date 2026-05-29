from django.http import HttpRequest
from django.views.generic import TemplateView


class GeoPolygonsViewer(TemplateView):
    template_name = 'geo_polygons/page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Полигоны OpenStreetMap'
        context['page_description'] = (
            'Просмотр и скачивание полигонов объектов OpenStreetMap в выбранной точке на карте'
        )
        context['active_page'] = 'geo_polygons'
        return context

    def get(self, request: HttpRequest, *args, **kwargs):
        return super().get(request, *args, **kwargs)
