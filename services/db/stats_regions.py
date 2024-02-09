from django.db.models import Q

from region.models import Region


def get_number_of_visited_regions(user_id: int) -> int:
    return (
        Region.objects
        .all()
        .exclude(visitedcity__city=None)
        .exclude(~Q(visitedcity__user__id=user_id))
        .count()
    )
