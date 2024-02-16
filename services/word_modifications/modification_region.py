def modification__region__accusative_case(num: int) -> str:
    """
    Производит модификацию слова "регион" в зависимости от количества, которое употребляется с этим словом.
    Модиифцирует слово в винительном падеже: посетил 40 регионов.
    """
    if num == 1:
        return 'регион'
    elif 5 <= num <= 20:
        return 'регионов'
    elif len(str(num)) >= 2 and 10 <= int(str(num)[-2:]) <= 20 \
            or str(num)[-1] in ['5', '6', '7', '8', '9', '0']:
        return 'регионов'
    elif str(num)[-1] in ['2', '3', '4']:
        return 'региона'
    else:
        return 'регион'


def modification__region__prepositional_case(num: int) -> str:
    """
    Производит модификацию слова "регион" в зависимости от количества, которое употребляется с этим словом.
    Модиифцирует слово в предложном падеже: был в 40 регионах.
    """
    if str(num)[-1] == '1' and num != 11:
        return 'регионе'
    else:
        return 'регионах'
