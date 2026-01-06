/**
 * Реализует отображение карты и меток на ней, запрос посещённых
 * и не посещённых городов с сервера и обновление меток на карте.
 *
 * ----------------------------------------------
 *
 * Copyright © Egor Vavilov (Shecspi)
 * Licensed under the Apache License, Version 2.0
 *
 * ----------------------------------------------
 */
import L from 'leaflet';

import {addExternalBorderControl, addInternalBorderControl, create_map} from "../components/map.js";
import {ToolbarActions} from "../components/toolbar_actions.js";
import {initCountrySelect} from "../components/initCountrySelect";
import {initAddCityForm} from "../components/add_city_modal.js";

let actions;
let map;

const urlParams = new URLSearchParams(window.location.search);
const selectedCountryCode = urlParams.get('country');

window.onload = async () => {
    map = create_map();
    window.MG_MAIN_MAP = map;
    addExternalBorderControl(map, selectedCountryCode);
    addInternalBorderControl(map, selectedCountryCode);

    getVisitedCities()
        .then(own_cities => {
            actions = new ToolbarActions(map, own_cities);

            if (own_cities.length === 0) {
                map.setView([55.7522, 37.6156], 6);

                const btn = document.getElementById('btn_show-not-visited-cities');
                if (!btn) {
                    console.error('Кнопка не найдена!');
                } else if (own_cities.length === 0) {
                    btn.click();
                    const checkInterval = setInterval(() => {
                        if (actions.stateNotVisitedCities.size > 0) {
                            const group = new L.featureGroup(Array.from(actions.stateNotVisitedCities.values()));
                            map.fitBounds(group.getBounds());
                            clearInterval(checkInterval);
                        }
                    }, 200); // проверяем каждые 200 мс
                }
            } else {
                const allMarkers = actions.addOwnCitiesOnMap();
                const group = new L.featureGroup([...allMarkers]);
                map.fitBounds(group.getBounds());
            }
        })
        .then(() => {
            initAddCityForm(actions);
        });

    await initCountrySelect();
    await initYearFilter();
}

/**
 * Делает запрос на сервер и возвращает список городов, посещённых пользователем.
 */
async function getVisitedCities() {
    const baseUrl = window.URL_GET_VISITED_CITIES;
    const queryParams = window.location.search;

    const url = baseUrl + queryParams;

    return fetch(url, {
        method: 'GET'
    })
        .then(response => response.json());
}

/**
 * Инициализирует выпадающий список годов и загружает годы через API.
 * Preline UI автоматически инициализирует компонент через autoInit().
 */
async function initYearFilter() {
    const yearSelect = document.getElementById('id_year_filter');

    if (!yearSelect) {
        return;
    }

    // Инициализируем компонент сразу с disabled и placeholder "Загрузка..."
    // Убираем класс hidden перед инициализацией
    if (yearSelect.classList.contains('hidden')) {
        yearSelect.classList.remove('hidden');
    }

    // Инициализируем Preline UI компонент с disabled состоянием
    requestAnimationFrame(() => {
        if (window.HSStaticMethods && typeof window.HSStaticMethods.autoInit === 'function') {
            window.HSStaticMethods.autoInit();
        }
    });

    // Получаем текущий выбранный код страны из URL для фильтрации
    const urlParams = new URLSearchParams(window.location.search);
    const countryCode = urlParams.get('country');

    try {
        // Формируем URL для запроса годов
        let url = '/api/city/visit_years';
        if (countryCode) {
            url += `?country=${countryCode}`;
        }

        // Загружаем список годов через API
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Ошибка загрузки списка годов');
        }
        const data = await response.json();
        const years = data.years || [];

        // Очищаем существующие опции
        yearSelect.innerHTML = '<option value="all">Все годы</option>';

        // Добавляем опции годов
        years.forEach((year) => {
            const option = document.createElement('option');
            option.value = year;
            option.textContent = year;
            yearSelect.appendChild(option);
        });

        // Убираем disabled и обновляем placeholder
        yearSelect.removeAttribute('disabled');
        
        // Обновляем data-hs-select для изменения placeholder
        const dataHsSelect = yearSelect.getAttribute('data-hs-select');
        if (dataHsSelect) {
            try {
                const config = JSON.parse(dataHsSelect);
                config.placeholder = 'Все годы';
                yearSelect.setAttribute('data-hs-select', JSON.stringify(config));
            } catch (e) {
                console.error('Ошибка при обновлении конфигурации Preline UI:', e);
            }
        }

        // Если компонент уже был инициализирован, переинициализируем его
        const hsSelectInstance = window.HSSelect && window.HSSelect.getInstance ? window.HSSelect.getInstance('#id_year_filter') : null;
        if (hsSelectInstance && typeof hsSelectInstance.destroy === 'function') {
            hsSelectInstance.destroy();
        }
        
        // Переинициализируем компонент с новыми опциями
        // Используем requestAnimationFrame для гарантии, что DOM обновлен
        requestAnimationFrame(() => {
            if (window.HSSelect) {
                try {
                    new window.HSSelect('#id_year_filter');
                } catch (e) {
                    // Если не получилось, используем autoInit
                    if (window.HSStaticMethods && typeof window.HSStaticMethods.autoInit === 'function') {
                        window.HSStaticMethods.autoInit();
                    }
                }
            }
        });

        // Обработчик изменений значения
        const handleChange = () => {
            const selectedValue = yearSelect.value || '';
            // Если выбрано "all", передаем пустую строку для сброса фильтра
            const filterValue = selectedValue === 'all' ? '' : selectedValue;
            filterCitiesByYear(filterValue);
        };

        // Слушаем изменения напрямую на select элементе
        yearSelect.addEventListener('change', handleChange);
    } catch (error) {
        console.error('Ошибка при загрузке списка годов:', error);
        // В случае ошибки оставляем компонент disabled
    }
}

/**
 * Фильтрует города на карте по выбранному году.
 * @param {string} selectedYear - Выбранный год (пустая строка для показа всех городов)
 */
function filterCitiesByYear(selectedYear) {
    if (!actions || !actions.stateOwnCities) {
        return;
    }

    // Если год не выбран или выбрано "Все годы", показываем все города
    if (!selectedYear || selectedYear === 'all') {
        actions.stateOwnCities.forEach((marker) => {
            if (!map.hasLayer(marker)) {
                marker.addTo(map);
            }
        });

        // Перецентрируем карту по всем городам
        const allMarkers = Array.from(actions.stateOwnCities.values());
        if (allMarkers.length > 0) {
            const group = new L.featureGroup(allMarkers);
            map.fitBounds(group.getBounds());
        }
        return;
    }

    const year = parseInt(selectedYear, 10);
    if (isNaN(year)) {
        return;
    }

    // Создаём Map для быстрого доступа к данным города по ID
    const citiesMap = new Map();
    if (actions.ownCities) {
        actions.ownCities.forEach((city) => {
            citiesMap.set(city.id, city);
        });
    }

    // Фильтруем города по году посещения
    const visibleMarkers = [];
    actions.stateOwnCities.forEach((marker, cityId) => {
        const cityData = citiesMap.get(cityId);
        if (!cityData) {
            return;
        }

        // Проверяем, есть ли у города посещения в выбранном году
        const visitYears = cityData.visit_years || [];
        const hasVisitInYear = visitYears.includes(year);

        if (hasVisitInYear) {
            // Показываем город
            if (!map.hasLayer(marker)) {
                marker.addTo(map);
            }
            visibleMarkers.push(marker);
        } else {
            // Скрываем город
            if (map.hasLayer(marker)) {
                map.removeLayer(marker);
            }
        }
    });

    // Перецентрируем карту по видимым городам
    if (visibleMarkers.length > 0) {
        const group = new L.featureGroup(visibleMarkers);
        map.fitBounds(group.getBounds());
    }
}
