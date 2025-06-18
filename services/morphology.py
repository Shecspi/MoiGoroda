from typing import Literal

from pymorphy3 import MorphAnalyzer

morph = MorphAnalyzer()


def inflect_word(word: str, case: Literal['nomn', 'gent', 'datv', 'accs', 'ablt', 'loct']) -> str:
    """
    Склоняет слово в указанный падеж.
    """
    parsed = morph.parse(word)[0]
    form = parsed.inflect({case})
    return form.word if form else word


def to_nominative(word: str) -> str:
    """
    Именительный падеж — кто? что?
    Используется для подлежащего.
    Пример: Россия, Франция, Китай
    """
    return inflect_word(word, 'nomn')


def to_genitive(word: str) -> str:
    """
    Родительный падеж — кого? чего?
    Используется для выражения принадлежности, количества, отсутствия.
    Пример: города России, регионы Китая, столица Франции
    """
    return inflect_word(word, 'gent')


def to_dative(word: str) -> str:
    """
    Дательный падеж — кому? чему?
    Используется для указания получателя действия.
    Пример: по России, подарить Франции, написать Китаю
    """
    return inflect_word(word, 'datv')


def to_accusative(word: str) -> str:
    """
    Винительный падеж — кого? что?
    Объект действия, часто используется с глаголами.
    Пример: видеть Россию, посетить Францию, исследовать Китай
    """
    return inflect_word(word, 'accs')


def to_instrumental(word: str) -> str:
    """
    Творительный падеж — кем? чем?
    Средство действия, совместность.
    Пример: с Россией, управлять Китаем, дружить с Францией
    """
    return inflect_word(word, 'ablt')


def to_prepositional(word: str) -> str:
    """
    Предложный падеж — о ком? о чём?
    Употребляется только с предлогами: о, в, на и т.п.
    Пример: о России, в Китае, на Франции (реже)
    """
    return inflect_word(word, 'loct')


def plural_by_number(word: str, number: int) -> str:
    """
    Возвращает существительное в нужной форме в зависимости от числительного.

    Примеры:
    1 страна, 2 страны, 5 стран, 21 страна, 104 страны
    """
    parsed = morph.parse(word)[0]
    n = abs(number) % 100
    if 11 <= n <= 14:
        form = parsed.inflect({'plur', 'gent'})
    else:
        n = n % 10
        if n == 1:
            form = parsed.inflect({'sing', 'nomn'})
        elif 2 <= n <= 4:
            form = parsed.inflect({'sing', 'gent'})
        else:
            form = parsed.inflect({'plur', 'gent'})
    return form.word if form else word
