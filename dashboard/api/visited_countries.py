"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from datetime import datetime, timezone

from dashboard.schemas import VisitedCountriesOverviewResponse
from dmr import Controller
from dmr.plugins.msgspec import MsgspecSerializer
from utils.decorators import is_superuser_json


from dashboard.statistics_helpers import (
    collect_added_visited_countries_trend_card_overview,
    collect_users_with_visited_countries,
    collect_visited_countries_total,
)


@is_superuser_json
class GetVisitedCountriesOverviewController(Controller[MsgspecSerializer]):
    def get(self) -> VisitedCountriesOverviewResponse:
        now_date = datetime.now(timezone.utc).date()
        return VisitedCountriesOverviewResponse(
            total_visited_countries=collect_visited_countries_total(),
            users_with_visited_countries=collect_users_with_visited_countries(),
            added_last_30d=collect_added_visited_countries_trend_card_overview(
                now_date=now_date, days=30, group_by='day'
            ),
            added_last_6m=collect_added_visited_countries_trend_card_overview(
                now_date=now_date, days=183, group_by='week'
            ),
            added_last_1y=collect_added_visited_countries_trend_card_overview(
                now_date=now_date, days=365, group_by='month'
            ),
        )

