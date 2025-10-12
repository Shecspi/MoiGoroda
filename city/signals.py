from typing import Any, Type
from django.db.models import QuerySet
from django.db.models.signals import post_save
from django.dispatch import receiver

from city.models import City, VisitedCity
from subscribe.infrastructure.models import Subscribe, VisitedCityNotification


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
