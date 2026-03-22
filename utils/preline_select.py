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
        'searchClasses': (
            'block w-full text-sm bg-transparent border border-gray-200 dark:border-neutral-600 '
            'rounded-lg text-gray-900 dark:text-neutral-100 placeholder:text-gray-400 '
            'placeholder:text-sm dark:placeholder:text-neutral-500 focus:border-blue-500 focus:outline-none '
            'focus:ring-1 focus:ring-blue-500 focus:ring-offset-0 dark:focus:ring-1 dark:focus:ring-blue-500 '
            'py-2 px-3 [-webkit-tap-highlight-color:transparent]'
        ),
        'searchWrapperClasses': (
            'bg-white dark:bg-neutral-900 p-2 -mx-1 sticky top-0 '
            'border-b border-gray-200 dark:border-neutral-700 z-10'
        ),
        'placeholder': placeholder,
        'toggleTag': (
            '<button type="button" aria-expanded="false">'
            '<span class="text-gray-800 dark:text-neutral-200 truncate" data-title></span>'
            '</button>'
        ),
        'toggleClasses': (
            'hs-select-disabled:pointer-events-none hs-select-disabled:opacity-50 relative py-3 ps-4 pe-9 '
            'flex gap-x-2 text-nowrap w-full cursor-pointer bg-white border border-gray-200 rounded-lg '
            'text-start text-sm focus:outline-hidden focus:ring-2 focus:ring-blue-500 dark:bg-neutral-900 '
            'dark:border-neutral-700 dark:text-neutral-200 dark:focus:outline-hidden dark:focus:ring-1 '
            'dark:focus:ring-neutral-600'
        ),
        'dropdownClasses': (
            'mt-2 max-h-72 pb-1 px-1 space-y-0.5 z-20 w-full bg-white dark:bg-neutral-900 '
            'border border-gray-200 dark:border-neutral-700 rounded-lg shadow-lg overflow-hidden '
            'overflow-y-auto [&::-webkit-scrollbar]:w-2 [&::-webkit-scrollbar-thumb]:rounded-full '
            '[&::-webkit-scrollbar-track]:bg-gray-100 [&::-webkit-scrollbar-thumb]:bg-gray-300 '
            'dark:[&::-webkit-scrollbar-track]:bg-neutral-700 dark:[&::-webkit-scrollbar-thumb]:bg-neutral-500'
        ),
        'optionClasses': (
            'py-2 px-4 w-full text-sm text-gray-800 cursor-pointer hover:bg-gray-100 rounded-lg '
            'focus:outline-hidden focus:bg-gray-100 dark:bg-neutral-900 dark:hover:bg-neutral-800 '
            'dark:text-neutral-200 dark:focus:bg-neutral-800'
        ),
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
