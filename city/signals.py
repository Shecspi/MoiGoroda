# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

from typing import Any, Type
from django.db.models import QuerySet
from django.db.models.signals import post_delete, post_save
from django.db import transaction
from django.dispatch import receiver

from account.use_cases.visited_cities_countries_coverage import (
    invalidate_personal_visited_cities_countries_coverage_cache,
)
from city.models import City, VisitedCity
from subscribe.infrastructure.models import Subscribe, VisitedCityNotification


def _invalidate_visited_cities_countries_coverage_cache(user_id: int) -> None:
    transaction.on_commit(
        lambda: invalidate_personal_visited_cities_countries_coverage_cache(user_id)
    )


@receiver(post_save, sender=VisitedCity)
def invalidate_visited_city_statistics_cache_on_save(
    sender: Type[VisitedCity], instance: VisitedCity, **kwargs: Any
) -> None:
    _invalidate_visited_cities_countries_coverage_cache(instance.user_id)


@receiver(post_delete, sender=VisitedCity)
def invalidate_visited_city_statistics_cache_on_delete(
    sender: Type[VisitedCity], instance: VisitedCity, **kwargs: Any
) -> None:
    _invalidate_visited_cities_countries_coverage_cache(instance.user_id)


@receiver(post_save, sender=VisitedCity)
def notify_subscribers_on_city_add(
    sender: Type[VisitedCity], instance: VisitedCity, created: bool, **kwargs: Any
) -> None:
    if not created:
        return

    user = instance.user
    subscribers: 'QuerySet[Subscribe]' = Subscribe.objects.select_related('subscribe_from').filter(
        subscribe_to=user
    )
    city: 'City' = (
        VisitedCity.objects.select_related('city', 'city__country').get(pk=instance.pk).city
    )

    for subscriber in subscribers:
        VisitedCityNotification.objects.create(
            recipient=subscriber.subscribe_from,
            sender=user,
            city=city,
        )
