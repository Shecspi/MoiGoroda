"""
Тег для вывода HTML-контента с подстановкой рекламных блоков в места маркеров.

Поддерживаются:
  - <!-- rtb_banner --> (ручная вставка в исходном коде)
  - <div class="ad-placeholder-rtb-banner" data-ad="..."></div> (кнопки в редакторе)

Каждый маркер заменяется на вывод соответствующего шаблона (см. AD_TEMPLATE_MAP).
"""

import re
from typing import Any, cast

from django import template
from django.template import loader
from django.utils.safestring import mark_safe

register = template.Library()

# data-ad -> шаблон (None = использовать default_template из вызова тега)
AD_TEMPLATE_MAP: dict[str, str | None] = {
    'rtb_banner': None,  # default
    'rtb_banner_inside_article_1': 'advertisement/rtb_banner inside_article_1.html',
    'rtb_banner_inside_article_2': 'advertisement/rtb_banner inside_article_2.html',
    'rtb_banner_inside_article_3': 'advertisement/rtb_banner inside_article_3.html',
}

# Регулярка: комментарий или div с data-ad (захватываем значение data-ad)
PLACEHOLDER_PATTERN = re.compile(
    r'<!--\s*rtb_banner\s*-->'
    r'|'
    r'<div\s+[^>]*class="[^"]*ad-placeholder-rtb-banner[^"]*"[^>]*data-ad="([^"]+)"[^>]*>\s*</div>'
    r'|'
    r'<div\s+[^>]*data-ad="([^"]+)"[^>]*class="[^"]*ad-placeholder-rtb-banner[^"]*"[^>]*>\s*</div>',
    re.IGNORECASE,
)


def _get_template_name(ad_type: str, default_template: str) -> str:
    """Возвращает имя шаблона для типа рекламы."""
    tpl = AD_TEMPLATE_MAP.get(ad_type, None)
    return default_template if tpl is None else tpl


@register.simple_tag(takes_context=True)
def content_with_ads(context: template.Context, html_content: str, ad_template_name: str) -> str:
    """
    Разбивает html_content по маркерам рекламы и вставляет рендер соответствующего
    шаблона. ad_template_name — шаблон по умолчанию для rtb_banner.
    """
    if not html_content:
        return mark_safe(html_content)

    flat_context = cast(dict[str, Any] | None, context.flatten())

    def replace_placeholder(match: re.Match[str]) -> str:
        # Комментарий <!-- rtb_banner -->: группа 0 — вся строка, групп 1 и 2 нет
        if match.group(0).strip().startswith('<!--'):
            ad_type = 'rtb_banner'
        else:
            ad_type = (match.group(1) or match.group(2) or 'rtb_banner').strip()

        tpl_name = _get_template_name(ad_type, ad_template_name)
        ad_html = loader.get_template(tpl_name).render(flat_context)
        return f'<div class="ad-insert-in-content" style="margin: 1rem 0;">{ad_html}</div>'

    if not PLACEHOLDER_PATTERN.search(html_content):
        return mark_safe(html_content)

    result = PLACEHOLDER_PATTERN.sub(replace_placeholder, html_content)
    return mark_safe(result)
