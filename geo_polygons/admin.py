import json

from django.contrib import admin
from django.db.models import QuerySet, Sum, TextField
from django.db.models.functions import Cast, Length
from django.http import HttpRequest, HttpResponse
from django.template.defaultfilters import filesizeformat

from geo_polygons.infrastructure.models import OSMPolygonCache


@admin.register(OSMPolygonCache)
class OSMPolygonCacheAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    change_list_template = 'admin/geo_polygons/osmpolygoncache/change_list.html'
    list_display = ('relation_id', 'name', 'get_geojson_size', 'created_at', 'updated_at')
    search_fields = ('relation_id', 'name')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['delete_selected']
    ordering = ('-created_at',)

    def get_queryset(self, request: HttpRequest) -> QuerySet[OSMPolygonCache]:
        qs = super().get_queryset(request)
        return qs.annotate(geojson_size=Length(Cast('geojson', TextField())))  # type: ignore[no-any-return]

    def changelist_view(
        self,
        request: HttpRequest,
        extra_context: dict[str, object] | None = None,
    ) -> HttpResponse:
        response = super().changelist_view(request, extra_context=extra_context)
        if hasattr(response, 'context_data'):
            changelist = response.context_data.get('cl')
            if changelist is not None:
                total_bytes = changelist.queryset.aggregate(total=Sum('geojson_size'))['total'] or 0
                response.context_data['total_geojson_size'] = filesizeformat(total_bytes)
        return response

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def get_geojson_size(self, obj: OSMPolygonCache) -> str:
        size = getattr(obj, 'geojson_size', None)
        if size is None:
            size = len(
                json.dumps(obj.geojson, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
            )
        return filesizeformat(size)

    get_geojson_size.short_description = 'Размер'  # type: ignore[attr-defined]
    get_geojson_size.admin_order_field = 'geojson_size'  # type: ignore[attr-defined]
