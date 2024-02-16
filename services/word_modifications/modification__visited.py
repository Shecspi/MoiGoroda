def modification__visited(num: int) -> str:
    """
    Возвращает правильную форму слова 'посещено' в зависимости от количества 'num'.
    """
    if len(str(num)) > 1 and str(num)[-2:] == '11':
        return 'посещено'
    elif str(num)[-1] == '1':
        return 'посещён'
    else:
        return 'посещено'
