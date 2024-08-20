from django.contrib.auth.models import User
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


class VisitedCountry(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)

    class Meta:
        verbose_name = 'Посещенная страна'
        verbose_name_plural = 'Посещенные страны'
        unique_together = ('country', 'user')

    def __str__(self):
        return self.country

    def validate_city(self, city):
        if VisitedCountry.objects.filter(city=city, user=self.context['request'].user.pk).exists():
            logger.info(
                self.context['request'],
                '(API: Add visited city) An attempt to add a visited city that is already in the DB',
            )
            raise serializers.ValidationError(f'Город {city} уже добавлен.')
        return city
