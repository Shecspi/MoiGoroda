"""
Реализует методы для работы со списком регионов.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""


class RegionListMixin:
    @staticmethod
    def declension_of_visited(quantity: int) -> str:
        """
        Возвращает правильное склонение слова 'Посещено' в зависимости от количества 'num'.
        """
        if len(str(quantity)) > 1 and str(quantity)[-2:] == '11':
            return 'Посещено'
        elif str(quantity)[-1] == '1':
            return 'Посещён'
        else:
            return 'Посещено'

    @staticmethod
    def declension_of_region(quantity: int) -> str:
        """
        Возвращает правильное склонение слова 'регион' в зависимости от количества 'num'.
        """
        if quantity == 1:
            return 'регион'
        elif 5 <= quantity <= 20:
            return 'регионов'
        elif (
            len(str(quantity)) >= 2
            and 10 <= int(str(quantity)[-2:]) <= 20
            or str(quantity)[-1] in ['5', '6', '7', '8', '9', '0']
        ):
            return 'регионов'
        elif str(quantity)[-1] in ['2', '3', '4']:
            return 'региона'
        else:
            return 'регион'
