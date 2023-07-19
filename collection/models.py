from django.db import models

from city.models import City


class Collection(models.Model):
    title = models.CharField(
        max_length=256,
        verbose_name='Название',
        blank=False,

    )
    city = models.ManyToManyField(
        City,
        related_name='collections_list'
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
        verbose_name = 'Коллекция'
        verbose_name_plural = 'Коллекции'
