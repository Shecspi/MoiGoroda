from typing import Any

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def update_query(context: dict[str, Any], **kwargs: Any) -> str:
    """
    Возвращает текущий GET-запрос с обновлёнными параметрами.
    Пример использования: {% update_query page=3 %}
    """
    request = context['request']
    query = request.GET.copy()

    # Удалить page, если она в query и не является целым числом
    page_value = query.get('page')
    if page_value and not page_value.isdigit():
        query.pop('page', None)

    for k, v in kwargs.items():
        if v is None:
            query.pop(k, None)
        else:
            query[k] = v

    return str(query.urlencode())
