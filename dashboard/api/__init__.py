"""Эндпоинты `dashboard`.

Пакет — тонкий агрегатор: контроллеры вынесены в `dashboard/api/*.py`, а здесь
они реэкспортируются для совместимости с импортами вида
`from dashboard.api import GetXController`.
"""

from __future__ import annotations

from .blog import (  # noqa: F401
    GetBlogArticlesAddedByRangeController,
    GetBlogArticlesAddedComparisonController,
    GetBlogArticlesByPageController,
    GetBlogArticlesViewsByRangeController,
    GetBlogArticlesViewsComparisonController,
    GetBlogArticlesViewsTotalController,
    GetBlogLastAddedArticlesController,
    GetBlogTopViewedArticlesController,
)
from .places import (  # noqa: F401
    GetPersonalCollectionsByRangeController,
    GetPersonalCollectionsComparisonController,
    GetPersonalCollectionsTotalController,
    GetPublicPersonalCollectionsTotalController,
    GetPlacesByRangeController,
    GetPlacesComparisonController,
    GetTotalVisitedOnlyPlacesController,
    GetTotalVisitedPlacesController,
)
from .users import (  # noqa: F401
    GetNumberOfUsersController,
    GetRegistrationsByRangeController,
    GetRegistrationsComparisonController,
    GetRegistrationsCumulativeChartController,
    GetNumberOfUsersWithoutVisitedCitiesController,
)
from .visited_cities import (  # noqa: F401
    GetAddedVisitedCitiesByRangeController,
    GetAddedVisitedCitiesComparisonController,
    GetTotalVisitedCitiesVisitsController,
    GetUniqueVisitedCitiesController,
    GetMaxQtyUniqueVisitedCitiesController,
    GetMaxQtyVisitedCitiesController,
    GetAverageQtyVisitedCitiesController,
    GetAverageQtyUniqueVisitedCitiesController,
    GetVisitedCitiesByUserChartController,
    GetUniqueVisitedCitiesByUserChartController,
)
from .visited_countries import (  # noqa: F401
    GetAddedVisitedCountryController,
    GetAddedVisitedCountriesByRangeController,
    GetAddedVisitedCountriesComparisonController,
    GetAddedVisitedCountriesChartController,
    GetAverageQtyVisitedCountriesController,
    GetMaxQtyVisitedCountriesController,
    GetTotalVisitedCountriesController,
    GetUsersWithVisitedCountriesController,
)

__all__ = [
    # Blog
    'GetBlogArticlesByPageController',
    'GetBlogArticlesViewsTotalController',
    'GetBlogArticlesViewsByRangeController',
    'GetBlogArticlesViewsComparisonController',
    'GetBlogArticlesAddedByRangeController',
    'GetBlogArticlesAddedComparisonController',
    'GetBlogLastAddedArticlesController',
    'GetBlogTopViewedArticlesController',
    # Users/Registrations
    'GetNumberOfUsersController',
    'GetRegistrationsByRangeController',
    'GetRegistrationsComparisonController',
    'GetRegistrationsCumulativeChartController',
    'GetNumberOfUsersWithoutVisitedCitiesController',
    # Places/Collections
    'GetTotalVisitedPlacesController',
    'GetTotalVisitedOnlyPlacesController',
    'GetPersonalCollectionsTotalController',
    'GetPublicPersonalCollectionsTotalController',
    'GetPersonalCollectionsByRangeController',
    'GetPersonalCollectionsComparisonController',
    'GetPlacesByRangeController',
    'GetPlacesComparisonController',
    # Visited cities
    'GetAddedVisitedCitiesByRangeController',
    'GetAddedVisitedCitiesComparisonController',
    'GetTotalVisitedCitiesVisitsController',
    'GetUniqueVisitedCitiesController',
    'GetMaxQtyUniqueVisitedCitiesController',
    'GetMaxQtyVisitedCitiesController',
    'GetAverageQtyVisitedCitiesController',
    'GetAverageQtyUniqueVisitedCitiesController',
    'GetVisitedCitiesByUserChartController',
    'GetUniqueVisitedCitiesByUserChartController',
    # Visited countries
    'GetTotalVisitedCountriesController',
    'GetUsersWithVisitedCountriesController',
    'GetAverageQtyVisitedCountriesController',
    'GetMaxQtyVisitedCountriesController',
    'GetAddedVisitedCountryController',
    'GetAddedVisitedCountriesByRangeController',
    'GetAddedVisitedCountriesComparisonController',
    'GetAddedVisitedCountriesChartController',
]
