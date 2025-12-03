/**
 * Компонент для создания popup окон с информацией о городе на картах.
 * Переиспользуемый модуль для различных страниц с картами.
 *
 * ----------------------------------------------
 *
 * Copyright © Egor Vavilov (Shecspi)
 * Licensed under the Apache License, Version 2.0
 *
 * ----------------------------------------------
 */

import L from 'leaflet';

/**
 * Форматирует дату из формата YYYY-MM-DD в формат ДД.ММ.ГГГГ
 */
export const formatDate = (value) => {
    if (!value) {
        return 'Не указана';
    }

    const parts = value.split('-');
    if (parts.length !== 3) {
        return value;
    }

    const [year, month, day] = parts;
    if (!year || !month || !day) {
        return value;
    }

    const dd = day.padStart(2, '0');
    const mm = month.padStart(2, '0');

    return `${dd}.${mm}.${year}`;
};

/**
 * Строит блок с информацией о посещениях города
 * @param {Object} cityData - Данные о городе
 * @param {boolean} cityData.isVisited - Посещён ли город
 * @param {string} cityData.firstVisitDate - Дата первого посещения (YYYY-MM-DD)
 * @param {string} cityData.lastVisitDate - Дата последнего посещения (YYYY-MM-DD)
 * @param {number} cityData.numberOfVisits - Количество посещений
 * @param {number|null} cityData.numberOfUsersWhoVisitCity - Количество пользователей, посетивших город
 * @param {number|null} cityData.numberOfVisitsAllUsers - Общее количество посещений всеми пользователями
 * @returns {string} HTML-код блока информации
 */
export const buildVisitInfoBlock = (cityData) => {
    let info = '';
    if (cityData.isVisited) {
        if (cityData.firstVisitDate && cityData.lastVisitDate && cityData.firstVisitDate === cityData.lastVisitDate) {
            info += `<div class="flex items-center justify-between gap-2 text-sm">`;
            info += `<div class="flex items-center gap-2">`;
            info += `<svg class="size-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>`;
            info += `<span class="text-gray-500 dark:text-neutral-400">Дата посещения:</span>`;
            info += `</div>`;
            info += `<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-500/10 dark:text-blue-400">${formatDate(cityData.firstVisitDate)}</span>`;
            info += `</div>`;
        } else if (cityData.firstVisitDate && cityData.lastVisitDate && cityData.firstVisitDate !== cityData.lastVisitDate) {
            info += `<div class="flex items-center justify-between gap-2 text-sm">`;
            info += `<div class="flex items-center gap-2">`;
            info += `<svg class="size-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>`;
            info += `<span class="text-gray-500 dark:text-neutral-400">Первое посещение:</span>`;
            info += `</div>`;
            info += `<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-500/10 dark:text-blue-400">${formatDate(cityData.firstVisitDate)}</span>`;
            info += `</div>`;
            info += `<div class="flex items-center justify-between gap-2 text-sm">`;
            info += `<div class="flex items-center gap-2">`;
            info += `<svg class="size-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>`;
            info += `<span class="text-gray-500 dark:text-neutral-400">Последнее посещение:</span>`;
            info += `</div>`;
            info += `<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-100 text-emerald-800 dark:bg-emerald-500/10 dark:text-emerald-400">${formatDate(cityData.lastVisitDate)}</span>`;
            info += `</div>`;
        }

        info += `<div class="flex items-center justify-between gap-2 text-sm">`;
        info += `<div class="flex items-center gap-2">`;
        info += `<svg class="size-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg>`;
        info += `<span class="text-gray-500 dark:text-neutral-400">Всего посещений:</span>`;
        info += `</div>`;
        info += `<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-500/10 dark:text-purple-400">${cityData.numberOfVisits || 1}</span>`;
        info += `</div>`;
    } else {
        info += `<div class="flex items-center justify-between gap-2 text-sm">`;
        info += `<div class="flex items-center gap-2">`;
        info += `<svg class="size-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>`;
        info += `<span class="text-gray-500 dark:text-neutral-400">Статус:</span>`;
        info += `</div>`;
        info += `<span class="text-gray-900 dark:text-white">Вы не были в этом городе</span>`;
        info += `</div>`;
    }

    if (cityData.numberOfUsersWhoVisitCity !== null || cityData.numberOfVisitsAllUsers !== null) {
        info += `<div class="mt-2 pt-2 border-t border-gray-200 dark:border-neutral-700"></div>`;

        info += `<div class="flex items-center justify-between gap-2 text-sm">`;
        info += `<div class="flex items-center gap-2">`;
        info += `<svg class="h-4 w-4 shrink-0 text-gray-400 dark:text-neutral-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M22 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>`;
        info += `<span class="text-gray-500 dark:text-neutral-400">Пользователей посетило:</span>`;
        info += `</div>`;
        info += `<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-orange-100 text-orange-800 dark:bg-orange-500/10 dark:text-orange-400">${cityData.numberOfUsersWhoVisitCity ?? 0}</span>`;
        info += `</div>`;

        info += `<div class="flex items-center justify-between gap-2 text-sm">`;
        info += `<div class="flex items-center gap-2">`;
        info += `<svg class="h-4 w-4 shrink-0 text-gray-400 dark:text-neutral-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"></path><path d="m9 12 2 2 4-4"></path></svg>`;
        info += `<span class="text-gray-500 dark:text-neutral-400">Посещений всеми пользователями:</span>`;
        info += `</div>`;
        info += `<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-teal-100 text-teal-800 dark:bg-teal-500/10 dark:text-teal-400">${cityData.numberOfVisitsAllUsers ?? 0}</span>`;
        info += `</div>`;
    }

    return info;
};

/**
 * Строит полное содержимое popup окна для города
 * @param {Object} cityData - Данные о городе
 * @param {number} cityData.id - ID города
 * @param {string} cityData.name - Название города
 * @param {Object} options - Опции для кастомизации popup
 * @param {string} [options.regionName] - Название региона
 * @param {string} [options.countryName] - Название страны
 * @param {string} [options.regionLink] - Ссылка на список городов региона
 * @param {string} [options.countryLink] - Ссылка на список городов страны
 * @param {boolean} [options.showAddButton] - Показывать ли кнопку "Отметить как посещённый"
 * @returns {string} HTML-код popup окна
 */
export const buildPopupContent = (cityData, options = {}) => {
    const {
        regionName = '',
        countryName = '',
        regionLink = '',
        countryLink = '',
        showAddButton = false
    } = options;

    let content = '<div class="px-1.5 py-1.5 min-w-[280px] max-w-[400px]">';

    content += `<div class="mb-2 pb-1 border-b border-gray-200 dark:border-neutral-700">`;
    content += `<h3 class="text-base font-semibold text-gray-900 dark:text-white mb-0">`;
    content += `<a href="/city/${cityData.id}" target="_blank" rel="noopener noreferrer" class="text-gray-900 hover:text-blue-600 dark:text-white dark:hover:text-blue-400 transition-colors">${cityData.name}</a>`;
    content += `</h3>`;

    content += `<div class="mt-2 flex items-center text-xs text-gray-600 dark:text-neutral-400">`;
    if (regionLink && regionName) {
        content += `<a href="${regionLink}" target="_blank" rel="noopener noreferrer" class="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">${regionName}</a>`;
    } else if (regionName) {
        content += `<span>${regionName}</span>`;
    }

    if (countryLink && countryName) {
        if (regionName) {
            content += `,`;
        }
        content += `<a href="${countryLink}" target="_blank" rel="noopener noreferrer" class="ps-1 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">${countryName}</a>`;
    } else if (countryName) {
        if (regionName) {
            content += `<span>,</span>`;
        }
        content += `<span>${countryName}</span>`;
    }
    content += `</div>`;
    content += `</div>`;

    content += '<div class="space-y-1.5 text-sm">';
    content += buildVisitInfoBlock(cityData);
    content += '</div>';

    if (showAddButton) {
        content += '<div class="mt-2 pt-2 border-t border-gray-200 dark:border-neutral-700">';
        if (!cityData.isVisited) {
            content += `<a href="#" 
                class="text-sm text-emerald-600 hover:text-emerald-700 dark:text-emerald-400 dark:hover:text-emerald-300 transition-colors"
                data-hs-overlay="#addCityModal" 
                data-city-name="${cityData.name}" 
                data-city-id="${cityData.id}" 
                data-city-region="${regionName}">Отметить как посещённый</a>`;
        } else {
            content += `<a href="#" 
                class="text-sm text-emerald-600 hover:text-emerald-700 dark:text-emerald-400 dark:hover:text-emerald-300 transition-colors"
                data-hs-overlay="#addCityModal" 
                data-city-name="${cityData.name}" 
                data-city-id="${cityData.id}" 
                data-city-region="${regionName}">Добавить ещё одно посещение</a>`;
        }
        content += '</div>';
    }

    content += '</div>';
    return content;
};

/**
 * Привязывает popup к маркеру Leaflet
 * @param {L.Marker} marker - Маркер Leaflet
 * @param {Object} cityData - Данные о городе
 * @param {Object} options - Опции для popup (см. buildPopupContent)
 */
export const bindPopupToMarker = (marker, cityData, options = {}) => {
    marker.bindPopup(buildPopupContent(cityData, options), {maxWidth: 400, minWidth: 280});
    marker.on('popupopen', () => {
        if (window.HSStaticMethods && typeof window.HSStaticMethods.autoInit === 'function') {
            window.HSStaticMethods.autoInit();
        }
    });
    marker.bindTooltip(cityData.name, {direction: 'top'});
    marker.on('mouseover', function () {
        const tooltip = this.getTooltip();
        if (this.isPopupOpen()) {
            tooltip.setOpacity(0.0);
        } else {
            tooltip.setOpacity(0.9);
        }
    });
    marker.on('click', function () {
        this.getTooltip().setOpacity(0.0);
    });
};

