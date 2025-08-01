from django import template
from services.morphology import (
    to_nominative,
    to_genitive,
    to_dative,
    to_accusative,
    to_instrumental,
    to_prepositional,
    plural_by_number,
)

register = template.Library()


@register.filter
def nominative(value):
    return to_nominative(value)


@register.filter
def genitive(value):
    return to_genitive(value)


@register.filter
def dative(value):
    return to_dative(value)


@register.filter
def accusative(value):
    return to_accusative(value)


@register.filter
def instrumental(value):
    return to_instrumental(value)


@register.filter
def prepositional(value):
    return to_prepositional(value)


@register.filter
def plural_by_num(word, number):
    """
    Склоняет слово в зависимости от числительного.
    Пример: {{ "страна"|plural_by_num:5 }} → "стран"
    """
    return plural_by_number(word, number)
