from services.word_modifications.modification__city import change__city
from services.word_modifications.modification__visited import change__visited


def change(word: str, num: int) -> str:
    match word:
        case 'город':
            return change__city(num)
        case 'посещено':
            return change__visited(num)
        case _:
            return word
