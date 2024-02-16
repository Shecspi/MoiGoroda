def modification__city(num: int) -> str:
    """
    Производит модификацию слова "город" в зависимости от количества, которое употребляется с этим словом.
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
