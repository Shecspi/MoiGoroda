"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from datetime import datetime, timezone

from dashboard.schemas import BlogArticlesOverviewResponse
from dmr import Controller
from dmr.plugins.msgspec import MsgspecSerializer
from utils.decorators import is_superuser_json


from dashboard.statistics_helpers import (
    collect_blog_last_added_card_overview,
    collect_blog_top_viewed_card_overview,
)


@is_superuser_json
class GetBlogArticlesOverviewController(Controller[MsgspecSerializer]):
    """
    Агрегированный endpoint для dashboard-блока блога:
    - последние добавленные статьи (30 дней): таблица + сравнение + график
    - самые просматриваемые статьи (60 дней): таблица + сравнение + график
    """

    def get(self) -> BlogArticlesOverviewResponse:
        now_date = datetime.now(timezone.utc).date()
        added_card = collect_blog_last_added_card_overview(now_date=now_date, days=30)
        top_card = collect_blog_top_viewed_card_overview(now_date=now_date, days=60)

        return BlogArticlesOverviewResponse(added_last_30d=added_card, top_views_60d=top_card)
