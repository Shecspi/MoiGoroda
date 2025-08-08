from django.db.models.signals import post_save
from django.dispatch import receiver

from city.models import VisitedCity
from subscribe.models import Subscribe, Notification


@receiver(post_save, sender=VisitedCity)
def notify_subscribers_on_city_add(sender, instance, created, **kwargs):
    if not created:
        return

    user = instance.user
    subscribers = Subscribe.objects.select_related('subscribe_from').filter(subscribe_to=user)
    city = VisitedCity.objects.select_related('city', 'city__country').get(pk=instance.pk).city

    for subscriber in subscribers:
        Notification.objects.create(
            recipient=subscriber.subscribe_from,
            sender=user,
            message=f'**{user}** добавил посещённый город **{city.title} ({city.country})**',
        )
