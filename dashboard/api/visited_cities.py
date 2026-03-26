"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from datetime import datetime, timezone

from dashboard.schemas import VisitedCitiesOverviewResponse
from dmr import Controller
from dmr.plugins.msgspec import MsgspecSerializer
from utils.decorators import is_superuser_json


from dashboard.statistics_helpers import (
    collect_added_visited_cities_trend_card_overview,
    collect_total_visited_cities_visits,
    collect_unique_visited_cities_by_user_chart,
    collect_unique_visited_cities,
    collect_visited_cities_by_user_chart,
)


@is_superuser_json
class GetVisitedCitiesOverviewController(Controller[MsgspecSerializer]):
    def get(self) -> VisitedCitiesOverviewResponse:
        now_date = datetime.now(timezone.utc).date()

        return VisitedCitiesOverviewResponse(
            total_visited_cities_visits=collect_total_visited_cities_visits(),
            unique_visited_cities=collect_unique_visited_cities(),
            added_last_30d=collect_added_visited_cities_trend_card_overview(
                now_date=now_date, days=30, group_by='day'
            ),
            added_last_6m=collect_added_visited_cities_trend_card_overview(
                now_date=now_date, days=183, group_by='week'
            ),
            added_last_1y=collect_added_visited_cities_trend_card_overview(
                now_date=now_date, days=365, group_by='month'
            ),
            visited_by_user_chart=collect_visited_cities_by_user_chart(limit=50),
            unique_visited_by_user_chart=collect_unique_visited_cities_by_user_chart(limit=50),
        )
