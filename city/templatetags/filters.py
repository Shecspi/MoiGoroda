"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import Any

from django import template

register = template.Library()


@register.filter
def in_list(value: Any, arg: str) -> bool:
    return value in arg.split(',')


@register.filter
def startswith(value: str | None, arg: str) -> bool:
    """
    Проверяет, начинается ли строка с указанного префикса.

    :param value: Строка для проверки
    :param arg: Префикс для проверки
    :return: True, если строка начинается с префикса, иначе False
    """
    if value is None:
        return False
    return str(value).startswith(str(arg))
