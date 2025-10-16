from typing import Any

from django import template

register = template.Library()


@register.filter
def in_list(value: Any, arg: str) -> bool:
    return value in arg.split(',')
