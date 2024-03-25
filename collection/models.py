"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.db import models
from django.shortcuts import reverse

from city.models import City


class Collection(models.Model):
    title = models.CharField(
        max_length=256,
        verbose_name='Название',
        blank=False,
    )
    city = models.ManyToManyField(City, related_name='collections_list')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('collection-detail-list', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['title']
        verbose_name = 'Коллекция'
        verbose_name_plural = 'Коллекции'
