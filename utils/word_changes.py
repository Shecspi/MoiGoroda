def change(word: str, num: int) -> str:
    match word:
        case 'город':
            return change__city(num)
        case 'посещено':
            return change__visited(num)
        case _:
            return word


def change__city(num: int) -> str:
    """
    Возвращает правильную форму слова 'город' в зависимости от количества 'num'.
    """
    if num == 1:
        return 'город'
    elif 5 <= num <= 20:
        return 'городов'
    elif len(str(num)) >= 2 and 10 <= int(str(num)[-2:]) <= 20\
            or str(num)[-1] in ['5', '6', '7', '8', '9', '0']:
        return 'городов'
    elif str(num)[-1] in ['2', '3', '4']:
        return 'города'
    else:
        return 'город'


def change__visited(num: int) -> str:
    """
    Возвращает правильную форму слова 'посещено' в зависимости от количества 'num'.
    """
    if len(str(num)) > 1 and str(num)[-2:] == '11':
        return 'Посещено'
    elif str(num)[-1] == '1':
        return 'Посещён'
    else:
        return 'Посещено'
