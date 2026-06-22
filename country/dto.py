# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

"""DTO для внутренних результатов country-репозиториев."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CountryVisitedCityCounts:
    """Количество посещённых и доступных городов в стране."""

    pk: int
    name: str
    visited_cities: int
    total_cities: int
