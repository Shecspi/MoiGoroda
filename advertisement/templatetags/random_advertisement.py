from django import template
from advertisement.models import LinkAdvertisement

register = template.Library()


@register.simple_tag
def random_advertisement():
    advertisement = LinkAdvertisement.objects.order_by('?').first()
    return advertisement
