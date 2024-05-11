import pytest

from utils.RegionListMixin import RegionListMixin
from utils.VisitedCityMixin import VisitedCityMixin


@pytest.mark.parametrize(
    'quantity, word',
    (
        (1, 'регион'),
        (2, 'региона'),
        (3, 'региона'),
        (4, 'региона'),
        (5, 'регионов'),
        (6, 'регионов'),
        (7, 'регионов'),
        (8, 'регионов'),
        (9, 'регионов'),
        (10, 'регионов'),
        (11, 'регионов'),
        (12, 'регионов'),
        (13, 'регионов'),
        (14, 'регионов'),
        (15, 'регионов'),
        (16, 'регионов'),
        (17, 'регионов'),
        (18, 'регионов'),
        (19, 'регионов'),
        (20, 'регионов'),
        (21, 'регион'),
        (22, 'региона'),
        (31, 'регион'),
        (33, 'региона'),
        (44, 'региона'),
        (55, 'регионов'),
        (66, 'регионов'),
        (77, 'регионов'),
        (88, 'регионов'),
        (99, 'регионов'),
        (100, 'регионов'),
    ),
)
def test__declension_of_city(quantity, word):
    mixin = RegionListMixin()

    assert mixin.declension_of_region(quantity) == word
