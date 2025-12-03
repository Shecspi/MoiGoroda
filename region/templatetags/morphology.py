from django import template
from services.morphology import (
    to_nominative,
    to_genitive,
    to_dative,
    to_accusative,
    to_instrumental,
    to_prepositional,
    plural_by_number,
    modify_by_number,
)

register = template.Library()


@register.filter
def nominative(value: str) -> str:
    return to_nominative(value)


@register.filter
def genitive(value: str) -> str:
    return to_genitive(value)


@register.filter
def dative(value: str) -> str:
    return to_dative(value)


@register.filter
def accusative(value: str) -> str:
    return to_accusative(value)


@register.filter
def instrumental(value: str) -> str:
    return to_instrumental(value)


@register.filter
def prepositional(value: str) -> str:
    return to_prepositional(value)


@register.filter
def plural_by_num(word: str, number: int) -> str:
    """
    Склоняет слово в зависимости от числительного.
    Пример: {{ "страна"|plural_by_num:5 }} → "стран"
    """
    return plural_by_number(word, number)


@register.filter
def modify_by_num(forms: str, number: int) -> str:
    """
    Универсальная функция для выбора формы слова в зависимости от числа.
    Принимает строку с двумя формами, разделёнными запятой: "одна_форма,другая_форма".
    Возвращает первую форму для 1, 21, 31... (но не 11), иначе вторую форму.

    Примеры:
    {{ "посещён,посещено"|modify_by_num:1 }} → "посещён"
    {{ "посещён,посещено"|modify_by_num:2 }} → "посещено"
    {{ "посещён,посещено"|modify_by_num:11 }} → "посещено"
    {{ "посещён,посещено"|modify_by_num:21 }} → "посещён"
    """
    try:
        one_form, other_form = forms.split(',', 1)
        return modify_by_number(one_form.strip(), other_form.strip(), number)
    except ValueError:
        # Если формат неправильный, возвращаем исходную строку
        return forms
