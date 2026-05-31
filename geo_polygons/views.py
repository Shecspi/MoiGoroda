from typing import Any

from django.views.generic import TemplateView


class GeoPolygonsViewer(TemplateView):
    template_name = 'geo_polygons/page.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Полигоны OpenStreetMap'
        context['page_description'] = (
            'Просмотр и скачивание полигонов объектов OpenStreetMap в выбранной точке на карте'
        )
        context['active_page'] = 'geo_polygons'
        return context
