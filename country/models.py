from django.db import models


class PartOfTheWorld(models.Model):
    name = models.CharField(
        max_length=20, unique=True, blank=False, null=False, verbose_name='Название'
    )

    class Meta:
        verbose_name = 'Часть света'
        verbose_name_plural = 'Части света'

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(
        max_length=50, unique=True, blank=False, null=False, verbose_name='Название'
    )
    part_of_the_world = models.ForeignKey(
        PartOfTheWorld, on_delete=models.CASCADE, null=True, blank=True
    )

    class Meta:
        verbose_name = 'Расположение'
        verbose_name_plural = 'Расположения'

    def __str__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(
        max_length=100, unique=True, blank=False, null=False, verbose_name='Название'
    )
    fullname = models.CharField(
        max_length=100, unique=True, blank=True, null=True, verbose_name='Полное название'
    )
    code = models.CharField(max_length=2, unique=True, blank=False, null=False, verbose_name='Код')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = 'Страна'
        verbose_name_plural = 'Страны'

    def __str__(self):
        return self.name
