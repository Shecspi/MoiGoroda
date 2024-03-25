"""
Реализует функции, производящие какие-либо рассчёты, не связанные с обращением в БД.
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""


def calculate_ratio(divisible: int, divisor: int) -> int:
    """
    Рассчитывает процентное соотношение divisible к divisor и возвращает его в округлённом до целого числа значении.
    В случае, если в качестве divisor передаётся 0, то возвращается 0.
    """
    try:
        return int((divisible / divisor) * 100)
    except ZeroDivisionError:
        return 0
