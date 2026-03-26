"""
Helper-функции для подсчёта статистики dashboard.

Пакет с реэкспортом функций по сущностям, чтобы импорты вида
`from dashboard.statistics_helpers import ...` оставались стабильными.
"""

from __future__ import annotations

from .blog import (  # noqa: F401
    _collect_blog_article_views_by_group,
    _collect_blog_articles_added_by_group,
    collect_blog_last_added_articles_items,
    collect_blog_last_added_card_overview,
    collect_blog_top_viewed_articles_items,
    collect_blog_top_viewed_card_overview,
    count_blog_article_views_in_range,
    count_blog_articles_added_in_range,
)
from .collections import (  # noqa: F401
    _collect_personal_collections_by_group,
    collect_personal_collections_total,
    collect_personal_collections_trend_card_overview,
    collect_public_personal_collections_total,
    count_personal_collections_created_in_range,
)
from .common import (  # noqa: F401
    _format_group_label,
    _get_group_trunc_function,
    _next_group_date,
    build_blog_overview_period,
    build_period_comparison_stats,
)
from .places import (  # noqa: F401
    _collect_places_by_group,
    collect_places_total,
    collect_places_trend_card_overview,
    collect_places_visited_only_total,
    count_places_created_in_range,
)
from .users import (  # noqa: F401
    _collect_registrations_by_group,
    collect_number_of_users_without_visited_cities,
    collect_registrations_trend_card_overview,
    collect_total_users,
    count_registrations_in_range,
)
from .visited_cities import (  # noqa: F401
    _collect_added_visited_cities_by_group,
    collect_added_visited_cities_trend_card_overview,
    collect_total_visited_cities_visits,
    collect_unique_visited_cities_by_user_chart,
    collect_unique_visited_cities,
    collect_visited_cities_by_user_chart,
    count_added_visited_cities_in_range,
)
from .visited_countries import (  # noqa: F401
    _collect_added_visited_countries_by_group,
    collect_added_visited_countries_trend_card_overview,
    collect_users_with_visited_countries,
    collect_visited_countries_total,
    count_added_visited_countries_in_range,
)

__all__ = [
    # common
    '_get_group_trunc_function',
    '_format_group_label',
    '_next_group_date',
    'build_blog_overview_period',
    'build_period_comparison_stats',
    # users
    '_collect_registrations_by_group',
    'collect_total_users',
    'collect_number_of_users_without_visited_cities',
    'count_registrations_in_range',
    'collect_registrations_trend_card_overview',
    # visited cities/countries
    '_collect_added_visited_cities_by_group',
    'collect_total_visited_cities_visits',
    'collect_unique_visited_cities',
    'count_added_visited_cities_in_range',
    'collect_added_visited_cities_trend_card_overview',
    'collect_visited_cities_by_user_chart',
    'collect_unique_visited_cities_by_user_chart',
    '_collect_added_visited_countries_by_group',
    'collect_visited_countries_total',
    'collect_users_with_visited_countries',
    'count_added_visited_countries_in_range',
    'collect_added_visited_countries_trend_card_overview',
    # places
    '_collect_places_by_group',
    'collect_places_total',
    'collect_places_visited_only_total',
    'count_places_created_in_range',
    'collect_places_trend_card_overview',
    # collections
    '_collect_personal_collections_by_group',
    'collect_personal_collections_total',
    'collect_public_personal_collections_total',
    'count_personal_collections_created_in_range',
    'collect_personal_collections_trend_card_overview',
    # blog
    '_collect_blog_article_views_by_group',
    '_collect_blog_articles_added_by_group',
    'collect_blog_last_added_articles_items',
    'collect_blog_top_viewed_articles_items',
    'count_blog_articles_added_in_range',
    'count_blog_article_views_in_range',
    'collect_blog_last_added_card_overview',
    'collect_blog_top_viewed_card_overview',
]
