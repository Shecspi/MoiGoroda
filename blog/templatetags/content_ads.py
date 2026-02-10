"""
Тег для вывода HTML-контента с подстановкой рекламных блоков в места маркеров.

Поддерживаются два варианта маркера (TinyMCE при сохранении вырезает комментарии):
  - <!-- rtb_banner --> (если вставлен вручную в исходном коде)
  - <div class="ad-placeholder-rtb-banner" data-ad="rtb_banner"></div> (кнопка в редакторе)

При рендере каждый маркер заменяется на вывод указанного шаблона.
"""

import re

from django import template
from django.template import loader
from django.utils.safestring import mark_safe

register = template.Library()

# Комментарий (для ручной вставки в исходном коде)
PLACEHOLDER_COMMENT = '<!-- rtb_banner -->'
# Регулярка для div, вставляемого кнопкой (атрибуты и пробелы могут отличаться)
PLACEHOLDER_DIV_PATTERN = re.compile(
    r'<div\s+[^>]*class="[^"]*ad-placeholder-rtb-banner[^"]*"[^>]*data-ad="rtb_banner"[^>]*>\s*</div>'
    r'|<div\s+[^>]*data-ad="rtb_banner"[^>]*class="[^"]*ad-placeholder-rtb-banner[^"]*"[^>]*>\s*</div>',
    re.IGNORECASE,
)


def _normalize_placeholders(html_content: str) -> str:
    """Заменяет div-маркеры на комментарий, чтобы дальше обрабатывать единообразно."""
    return PLACEHOLDER_DIV_PATTERN.sub(PLACEHOLDER_COMMENT, html_content)


@register.simple_tag(takes_context=True)
def content_with_ads(context: template.Context, html_content: str, ad_template_name: str) -> str:
    """
    Разбивает html_content по маркерам рекламы и между частями вставляет
    рендер шаблона ad_template_name. Поддерживаются комментарий и div с data-ad.
    """
    if not html_content:
        return mark_safe(html_content)

    normalized = _normalize_placeholders(html_content)
    if PLACEHOLDER_COMMENT not in normalized:
        return mark_safe(html_content)

    parts = normalized.split(PLACEHOLDER_COMMENT)
    ad_html = loader.get_template(ad_template_name).render(context.flatten())
    # Обёртка с вертикальными отступами, чтобы сверху и снизу от рекламы был одинаковый зазор
    ad_wrapped = f'<div class="ad-insert-in-content" style="margin: 1rem 0;">{ad_html}</div>'

    result = parts[0]
    for part in parts[1:]:
        result += ad_wrapped + part

    return mark_safe(result)
