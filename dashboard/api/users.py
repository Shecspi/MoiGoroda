"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from datetime import datetime, timezone

from dashboard.schemas import UsersOverviewResponse
from dmr import Controller
from dmr.plugins.msgspec import MsgspecSerializer
from utils.decorators import is_superuser_json


from dashboard.statistics_helpers import (
    collect_number_of_users_without_visited_cities,
    collect_registrations_trend_card_overview,
    collect_total_users,
)


@is_superuser_json
class GetUsersOverviewController(Controller[MsgspecSerializer]):
    def get(self) -> UsersOverviewResponse:
        now_date = datetime.now(timezone.utc).date()
        return UsersOverviewResponse(
            total_users=collect_total_users(),
            users_without_visited_cities=collect_number_of_users_without_visited_cities(),
            registrations_last_30d=collect_registrations_trend_card_overview(
                now_date=now_date, days=30, group_by='day'
            ),
            registrations_last_6m=collect_registrations_trend_card_overview(
                now_date=now_date, days=183, group_by='week'
            ),
            registrations_last_1y=collect_registrations_trend_card_overview(
                now_date=now_date, days=365, group_by='month'
            ),
        )

