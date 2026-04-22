"""
Конфигурация Preline HSSelect для переиспользования в шаблонах и формах.

Использование в форме:
    self.fields["my_field"].widget.attrs["data-hs-select"] = json.dumps(
        hs_select_search_single_config(placeholder="..."),
        ensure_ascii=False,
    )
"""

from __future__ import annotations

from typing import Any


def hs_select_search_single_config(
    *,
    placeholder: str = 'Выберите...',
    search_placeholder: str = 'Поиск...',
) -> dict[str, Any]:
    """
    Одиночный select с полем поиска в выпадающем списке (Preline data-hs-select).

    Стили согласованы с остальными hs-select в проекте (tailwind.css, страницы с картой).
    z-index панели списка умеренный (z-20), чтобы не перекрывать навбар и модалки.
    """
    return {
        'hasSearch': True,
        'searchPlaceholder': search_placeholder,
        'searchClasses': 'mg-select-search',
        'searchWrapperClasses': 'mg-select-search-wrap',
        'placeholder': placeholder,
        'toggleTag': (
            '<button type="button" aria-expanded="false">'
            '<span class="text-gray-800 dark:text-neutral-200 truncate" data-title></span>'
            '</button>'
        ),
        'toggleClasses': 'mg-select-toggle',
        'dropdownClasses': 'mg-select-dropdown z-20',
        'optionClasses': 'mg-select-option',
        'optionTemplate': (
            '<div class="flex items-center">'
            '<div class="me-2" data-icon></div>'
            '<div>'
            '<div class="text-sm text-gray-800 dark:text-neutral-200" data-title></div>'
            '</div>'
            '<div class="ms-auto">'
            '<span class="hidden">'
            '<svg class="shrink-0 size-4 text-blue-600 dark:text-blue-500" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">'
            '<path d="M12.736 3.97a.733.733 0 0 1 1.047 0c.286.289.29.756.01 1.05L7.88 12.01a.733.733 0 0 1-1.065.02L3.217 8.384a.757.757 0 0 1 0-1.06.733.733 0 0 1 1.047 0l3.052 3.093 5.4-6.425a.247.247 0 0 1 .02-.022Z"/>'
            '</svg>'
            '</span>'
            '</div>'
            '</div>'
        ),
        'extraMarkup': (
            '<div class="absolute top-1/2 end-3 -translate-y-1/2">'
            '<svg class="shrink-0 size-3.5 text-gray-500 dark:text-neutral-500" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="m7 15 5 5 5-5"/>'
            '<path d="m7 9 5-5 5 5"/>'
            '</svg>'
            '</div>'
        ),
    }
