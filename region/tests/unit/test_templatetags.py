"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest

from region.templatetags.morphology import (
    nominative,
    genitive,
    dative,
    accusative,
    instrumental,
    prepositional,
    plural_by_num,
)


@pytest.mark.unit
class TestMorphologyFilters:
    """Тесты для фильтров морфологии"""

    def test_nominative_returns_string(self) -> None:
        """Тест что nominative возвращает строку"""
        result = nominative('Москва')
        assert isinstance(result, str)

    def test_genitive_returns_string(self) -> None:
        """Тест что genitive возвращает строку"""
        result = genitive('Москва')
        assert isinstance(result, str)

    def test_dative_returns_string(self) -> None:
        """Тест что dative возвращает строку"""
        result = dative('Москва')
        assert isinstance(result, str)

    def test_accusative_returns_string(self) -> None:
        """Тест что accusative возвращает строку"""
        result = accusative('Москва')
        assert isinstance(result, str)

    def test_instrumental_returns_string(self) -> None:
        """Тест что instrumental возвращает строку"""
        result = instrumental('Москва')
        assert isinstance(result, str)

    def test_prepositional_returns_string(self) -> None:
        """Тест что prepositional возвращает строку"""
        result = prepositional('Москва')
        assert isinstance(result, str)

    def test_plural_by_num_returns_string(self) -> None:
        """Тест что plural_by_num возвращает строку"""
        result = plural_by_num('город', 5)
        assert isinstance(result, str)

    def test_filters_work_with_russian_words(self) -> None:
        """Тест что фильтры работают с русскими словами"""
        word = 'Московская область'

        result_nom = nominative(word)
        result_gen = genitive(word)
        result_dat = dative(word)
        result_acc = accusative(word)
        result_inst = instrumental(word)
        result_prep = prepositional(word)

        # Все результаты должны быть строками
        for result in [result_nom, result_gen, result_dat, result_acc, result_inst, result_prep]:
            assert isinstance(result, str)
            assert len(result) > 0
