"""Эндпоинты `dashboard`.

Пакет — тонкий агрегатор: контроллеры вынесены в `dashboard/api/*.py`, а здесь
они реэкспортируются для совместимости с импортами вида
`from dashboard.api import GetXController`.
"""

from __future__ import annotations

from .blog import (  # noqa: F401
    GetBlogArticlesOverviewController,
)
from .places import (  # noqa: F401
    GetPersonalCollectionsOverviewController,
    GetPlacesOverviewController,
)
from .users import (  # noqa: F401
    GetNumberOfUsersController,
    GetRegistrationsByRangeController,
    GetRegistrationsComparisonController,
    GetRegistrationsCumulativeChartController,
    GetNumberOfUsersWithoutVisitedCitiesController,
)
from .visited_cities import (  # noqa: F401
    GetVisitedCitiesOverviewController,
)
from .visited_countries import (  # noqa: F401
    GetVisitedCountriesOverviewController,
)

__all__ = [
    # Blog
    'GetBlogArticlesOverviewController',
    # Users/Registrations
    'GetNumberOfUsersController',
    'GetRegistrationsByRangeController',
    'GetRegistrationsComparisonController',
    'GetRegistrationsCumulativeChartController',
    'GetNumberOfUsersWithoutVisitedCitiesController',
    # Places/Collections
    'GetPlacesOverviewController',
    'GetPersonalCollectionsOverviewController',
    # Visited cities
    'GetVisitedCitiesOverviewController',
    # Visited countries
    'GetVisitedCountriesOverviewController',
]
