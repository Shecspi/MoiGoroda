"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from datetime import datetime, timezone

from dashboard.schemas import (
    PersonalCollectionsOverviewResponse,
    PlacesOverviewResponse,
)
from dmr import Controller
from dmr.plugins.msgspec import MsgspecSerializer
from utils.decorators import is_superuser_json


from dashboard.statistics_helpers import (
    collect_personal_collections_total,
    collect_personal_collections_trend_card_overview,
    collect_places_total,
    collect_places_trend_card_overview,
    collect_places_visited_only_total,
    collect_public_personal_collections_total,
)


@is_superuser_json
class GetPlacesOverviewController(Controller[MsgspecSerializer]):
    def get(self) -> PlacesOverviewResponse:
        now_date = datetime.now(timezone.utc).date()

        return PlacesOverviewResponse(
            total_visited_places=collect_places_total(),
            total_visited_only_places=collect_places_visited_only_total(),
            last_30d=collect_places_trend_card_overview(now_date=now_date, days=30, group_by='day'),
            last_6m=collect_places_trend_card_overview(
                now_date=now_date, days=183, group_by='week'
            ),
            last_1y=collect_places_trend_card_overview(
                now_date=now_date, days=365, group_by='month'
            ),
        )


@is_superuser_json
class GetPersonalCollectionsOverviewController(Controller[MsgspecSerializer]):
    def get(self) -> PersonalCollectionsOverviewResponse:
        now_date = datetime.now(timezone.utc).date()

        return PersonalCollectionsOverviewResponse(
            total_personal_collections=collect_personal_collections_total(),
            total_public_personal_collections=collect_public_personal_collections_total(),
            last_30d=collect_personal_collections_trend_card_overview(
                now_date=now_date, days=30, group_by='day'
            ),
            last_6m=collect_personal_collections_trend_card_overview(
                now_date=now_date, days=183, group_by='week'
            ),
            last_1y=collect_personal_collections_trend_card_overview(
                now_date=now_date, days=365, group_by='month'
            ),
        )
