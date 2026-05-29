from django.db import models


class OSMPolygonCache(models.Model):
    """
    Кеш полигонов OSM, полученных из Nominatim API.
    Хранит GeoJSON полигонов для повторного использования без запросов к внешнему API.
    """

    relation_id = models.BigIntegerField(unique=True, verbose_name='Nominatim relation ID')
    name = models.CharField(max_length=500, verbose_name='Название объекта', blank=True)
    geojson = models.JSONField(verbose_name='GeoJSON полигона')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'OSM полигон'
        verbose_name_plural = 'OSM полигоны'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.name or f"Relation {self.relation_id}"} (#{self.relation_id})'
