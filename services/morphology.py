from typing import Literal

from pymorphy3 import MorphAnalyzer  # type: ignore[import-untyped]

morph = MorphAnalyzer()


Case = Literal['nomn', 'gent', 'datv', 'accs', 'ablt', 'loct']


def match_case(original: str, new: str) -> str:
    if original.isupper():
        return new.upper()
    elif original.istitle():
        return new.capitalize()
    else:
        return new


def inflect_word(word: str, case: Case) -> str:
    parsed = morph.parse(word)[0]
    form = parsed.inflect({case})
    inflected = form.word if form else word
    return match_case(word, inflected)


def inflect_phrase(phrase: str, case: Case) -> str:
    """
    Склоняет фразу (с дефисами и пробелами) в нужный падеж, сохраняя регистр каждой части.
    """
    result_words = []

    for word in phrase.split():
        # Обработка дефисных слов: Абу-Даби → [Абу, Даби]
        parts = word.split('-')
        inflected_parts = [inflect_word(part, case) for part in parts]
        result_words.append('-'.join(inflected_parts))

    return ' '.join(result_words)


def to_nominative(word: str) -> str:
    """
    Именительный падеж — кто? что?
    Используется для подлежащего.
    Пример: Россия, Франция, Китай
    """
    return inflect_phrase(word, 'nomn')


def to_genitive(word: str) -> str:
    """
    Родительный падеж — кого? чего?
    Используется для выражения принадлежности, количества, отсутствия.
    Пример: города России, регионы Китая, столица Франции
    """
    return inflect_phrase(word, 'gent')


def to_dative(word: str) -> str:
    """
    Дательный падеж — кому? чему?
    Используется для указания получателя действия.
    Пример: по России, подарить Франции, написать Китаю
    """
    return inflect_phrase(word, 'datv')


def to_accusative(word: str) -> str:
    """
    Винительный падеж — кого? что?
    Объект действия, часто используется с глаголами.
    Пример: видеть Россию, посетить Францию, исследовать Китай
    """
    return inflect_phrase(word, 'accs')


def to_instrumental(word: str) -> str:
    """
    Творительный падеж — кем? чем?
    Средство действия, совместность.
    Пример: с Россией, управлять Китаем, дружить с Францией
    """
    return inflect_phrase(word, 'ablt')


def to_prepositional(word: str) -> str:
    """
    Предложный падеж — о ком? о чём?
    Употребляется только с предлогами: о, в, на и т.п.
    Пример: о России, в Китае, на Франции (реже)
    """
    return inflect_phrase(word, 'loct')


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


def modify_by_number(one_form: str, other_form: str, number: int) -> str:
    """
    Универсальная функция для выбора формы слова в зависимости от числа.
    Возвращает one_form для 1, 21, 31... (но не 11), иначе other_form.

    Примеры:
    modify_by_number("посещён", "посещено", 1) → "посещён"
    modify_by_number("посещён", "посещено", 2) → "посещено"
    modify_by_number("посещён", "посещено", 11) → "посещено"
    modify_by_number("посещён", "посещено", 21) → "посещён"
    """
    n = abs(number) % 100
    n1 = n % 10
    # Особый случай: 11-14 всегда other_form
    if 10 < n < 20:
        return other_form
    # 1, 21, 31, 41... → one_form
    if n1 == 1:
        return one_form
    # Остальные → other_form
    return other_form
