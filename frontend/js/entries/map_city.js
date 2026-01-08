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
import {City, MarkerStyle} from "../components/schemas.js";
import {showDangerToast} from "../components/toast.js";

let actions;
let map;

const urlParams = new URLSearchParams(window.location.search);
const selectedCountryCode = urlParams.get('country');

window.onload = async () => {
    map = create_map();
    window.MG_MAIN_MAP = map;
    addExternalBorderControl(map, selectedCountryCode);
    addInternalBorderControl(map, selectedCountryCode);

    try {
        const own_cities = await getVisitedCities();
        actions = new ToolbarActions(map, own_cities);

        if (own_cities.length === 0) {
            map.setView([55.7522, 37.6156], 6);

            const btn = document.getElementById('btn_show-not-visited-cities');
            if (!btn) {
                console.error('Кнопка не найдена!');
            } else {
                btn.click();
                let attempts = 0;
                const maxAttempts = 50; // Максимум 10 секунд (50 * 200мс)
                const checkInterval = setInterval(() => {
                    attempts++;
                    if (actions.stateNotVisitedCities.size > 0) {
                        const group = new L.featureGroup(Array.from(actions.stateNotVisitedCities.values()));
                        map.fitBounds(group.getBounds());
                        clearInterval(checkInterval);
                    } else if (attempts >= maxAttempts) {
                        clearInterval(checkInterval);
                        console.warn('Таймаут ожидания загрузки непосещённых городов');
                    }
                }, 200); // проверяем каждые 200 мс
            }
        } else {
            const allMarkers = actions.addOwnCitiesOnMap();
            const group = new L.featureGroup([...allMarkers]);
            map.fitBounds(group.getBounds());
        }

        initAddCityForm(actions);
    } catch (error) {
        console.error('Ошибка при загрузке посещённых городов:', error);
    }

    await initCountrySelect();
    await initYearFilter();

    // Делаем функции доступными глобально для вызова из других модулей
    window.filterCitiesByYear = filterCitiesByYear;
    window.updateNotVisitedCitiesButtonState = updateNotVisitedCitiesButtonState;
    
    // Обновляем состояние кнопки "Показать непосещённые города" при загрузке
    updateNotVisitedCitiesButtonState();
}

/**
 * Делает запрос на сервер и возвращает список городов, посещённых пользователем.
 */
async function getVisitedCities() {
    const baseUrl = window.URL_GET_VISITED_CITIES;
    const queryParams = window.location.search;

    const url = baseUrl + queryParams;

    const response = await fetch(url, {
        method: 'GET'
    });
    
    if (!response.ok) {
        throw new Error(`Ошибка загрузки городов: ${response.status} ${response.statusText}`);
    }
    
    return response.json();
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
    const countryCode = selectedCountryCode;

    try {
        // Формируем URL для запроса годов
        let url = '/api/city/visit_years';
        if (countryCode) {
            url += `?country=${countryCode}`;
        }

        // Загружаем список годов через API
        const response = await fetch(url);
        if (!response.ok) {
            // Пытаемся получить детали ошибки из ответа
            let errorMessage = 'Ошибка загрузки списка годов';
            try {
                const errorData = await response.json();
                if (errorData.detail) {
                    errorMessage = errorData.detail;
                } else if (errorData.message) {
                    errorMessage = errorData.message;
                }
            } catch (e) {
                // Если не удалось распарсить JSON, используем стандартное сообщение
                if (response.status === 401) {
                    errorMessage = 'Требуется авторизация';
                } else if (response.status === 404) {
                    errorMessage = 'Страна не найдена';
                } else if (response.status >= 500) {
                    errorMessage = 'Ошибка сервера. Попробуйте позже';
                }
            }
            throw new Error(errorMessage);
        }
        const data = await response.json();
        const years = data.years || [];

        // Очищаем существующие опции и добавляем "Все годы"
        yearSelect.textContent = '';
        const allYearsOption = document.createElement('option');
        allYearsOption.value = 'all';
        allYearsOption.textContent = 'Все годы';
        yearSelect.appendChild(allYearsOption);

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

        // Удаляем старый обработчик, если он был добавлен ранее
        yearSelect.removeEventListener('change', handleChange);
        // Слушаем изменения напрямую на select элементе
        yearSelect.addEventListener('change', handleChange);
    } catch (error) {
        console.error('Ошибка при загрузке списка годов:', error);
        
        // Показываем сообщение об ошибке пользователю
        const errorMessage = error.message || 'Не удалось загрузить список годов посещений';
        showDangerToast('Ошибка загрузки', errorMessage);
        
        // Обновляем placeholder для отображения ошибки
        const dataHsSelect = yearSelect.getAttribute('data-hs-select');
        if (dataHsSelect) {
            try {
                const config = JSON.parse(dataHsSelect);
                config.placeholder = 'Ошибка загрузки';
                yearSelect.setAttribute('data-hs-select', JSON.stringify(config));
            } catch (e) {
                console.error('Ошибка при обновлении конфигурации Preline UI:', e);
            }
        }
        
        // Переинициализируем компонент с обновлённым placeholder
        const hsSelectInstance = window.HSSelect && window.HSSelect.getInstance ? window.HSSelect.getInstance('#id_year_filter') : null;
        if (hsSelectInstance && typeof hsSelectInstance.destroy === 'function') {
            hsSelectInstance.destroy();
        }
        
        requestAnimationFrame(() => {
            if (window.HSSelect) {
                try {
                    new window.HSSelect('#id_year_filter');
                } catch (e) {
                    if (window.HSStaticMethods && typeof window.HSStaticMethods.autoInit === 'function') {
                        window.HSStaticMethods.autoInit();
                    }
                }
            }
        });
        
        // Компонент остаётся в disabled состоянии
    }
}

/**
 * Обновляет состояние кнопки "Показать непосещённые города".
 * Кнопка активна только если:
 * - Выбрана конкретная страна (не "все страны")
 * - Не показаны города подписчиков
 * - Не применена фильтрация по годам
 */
function updateNotVisitedCitiesButtonState() {
    if (!actions) {
        return;
    }

    const btn = document.getElementById('btn_show-not-visited-cities');
    if (!btn) {
        return;
    }

    // Проверяем, выбрана ли конкретная страна
    const countrySelect = document.getElementById('id_country');
    const hasCountrySelected = countrySelect && countrySelect.value && countrySelect.value !== '' && countrySelect.value !== 'all';

    // Проверяем, показаны ли города подписок (есть ли маркеры на карте)
    const hasSubscriptionCitiesShown = actions.stateSubscriptionCities && 
        actions.stateSubscriptionCities.size > 0 &&
        Array.from(actions.stateSubscriptionCities.values()).some(marker => map.hasLayer(marker));

    // Проверяем, применена ли фильтрация по годам
    const yearSelect = document.getElementById('id_year_filter');
    const hasYearFilter = yearSelect && yearSelect.value && yearSelect.value !== '' && yearSelect.value !== 'all';

    // Кнопка активна только если все условия выполнены
    const shouldBeEnabled = hasCountrySelected && !hasSubscriptionCitiesShown && !hasYearFilter;

    btn.disabled = !shouldBeEnabled;
}

/**
 * Фильтрует города на карте по выбранному году.
 * @param {string} selectedYear - Выбранный год (пустая строка для показа всех городов)
 */
function filterCitiesByYear(selectedYear) {
    if (!actions || !actions.stateOwnCities) {
        return;
    }

    // Если год не выбран или выбрано "Все годы", пересоздаём все маркеры без фильтрации
    if (!selectedYear || selectedYear === 'all') {
        // Удаляем все существующие маркеры своих городов и городов подписок с карты
        actions.stateOwnCities.forEach((marker) => {
            if (map.hasLayer(marker)) {
                map.removeLayer(marker);
            }
        });
        if (actions.stateSubscriptionCities) {
            actions.stateSubscriptionCities.forEach((marker) => {
                if (map.hasLayer(marker)) {
                    map.removeLayer(marker);
                }
            });
        }

        // Очищаем словари маркеров
        actions.stateOwnCities.clear();
        actions.stateSubscriptionCities.clear();

        // Пересоздаём все маркеры без фильтрации по годам
        const allMarkers = [];
        
        // Добавляем свои города
        if (actions.ownCities) {
            actions.ownCities.forEach((cityData) => {
                const city = new City();
                city.id = cityData.id;
                city.name = cityData.title;
                city.region = cityData.region_title;
                city.country = cityData.country;
                city.lat = cityData.lat;
                city.lon = cityData.lon;
                city.visit_years = cityData.visit_years;
                city.first_visit_date = cityData.first_visit_date;
                city.last_visit_date = cityData.last_visit_date;
                city.number_of_visits = cityData.number_of_visits;

                const marker = actions.addMarkerToMap(city, MarkerStyle.OWN);
                actions.stateOwnCities.set(city.id, marker);
                allMarkers.push(marker);
            });
        }

        // Добавляем города подписок (они могут включать города, посещённые и мной, и подписчиками)
        if (actions.subscriptionCities && actions.subscriptionCities.length > 0) {
            // Получаем информацию о пользователях без фильтрации по годам
            const usersWhoVisitedCity = actions.getUsersWhoVisitedCity();
            const processedCityIds = new Set(Array.from(actions.stateOwnCities.keys()));

            actions.subscriptionCities.forEach((cityData) => {
                const cityId = cityData.id;
                
                // Пропускаем города, которые уже добавлены как свои
                if (processedCityIds.has(cityId)) {
                    return;
                }

                const city = new City();
                city.id = cityId;
                city.name = cityData.title;
                city.region = cityData.region_title;
                city.country = cityData.country;
                city.lat = cityData.lat;
                city.lon = cityData.lon;
                
                // Для городов подписок visit_years берём из ownCities по названию, если город есть там
                const ownCityData = actions.ownCities?.find(c => c.id === cityId);
                if (ownCityData) {
                    city.visit_years = ownCityData.visit_years;
                    city.first_visit_date = ownCityData.first_visit_date;
                    city.last_visit_date = ownCityData.last_visit_date;
                    city.number_of_visits = ownCityData.number_of_visits;
                }

                const users = usersWhoVisitedCity.get(cityId) || [];
                const markerStyle = ownCityData ? MarkerStyle.TOGETHER : MarkerStyle.SUBSCRIPTION;
                const marker = actions.addMarkerToMap(city, markerStyle, users);
                actions.stateSubscriptionCities.set(cityId, marker);
                allMarkers.push(marker);
                processedCityIds.add(cityId);
            });
        }

        // Перецентрируем карту по всем городам
        if (allMarkers.length > 0) {
            const group = new L.featureGroup(allMarkers);
            map.fitBounds(group.getBounds());
        }
        
        // Обновляем состояние кнопки "Показать непосещённые города"
        updateNotVisitedCitiesButtonState();
        return;
    }

    const year = parseInt(selectedYear, 10);
    if (isNaN(year)) {
        return;
    }

    // Создаём Map для быстрого доступа к данным своих городов по ID
    // Одновременно создаём объект ownCities по названию для получения данных о посещениях пользователя
    const ownCitiesMap = new Map();
    const ownCitiesByName = {};
    if (actions.ownCities) {
        actions.ownCities.forEach((city) => {
            ownCitiesMap.set(city.id, city);
            // Сохраняем данные по названию для городов подписок
            if (!ownCitiesByName[city.title]) {
                ownCitiesByName[city.title] = {
                    visit_years: city.visit_years,
                    first_visit_date: city.first_visit_date,
                    last_visit_date: city.last_visit_date
                };
            }
        });
    }

    // Создаём Map для быстрого доступа к данным городов подписок по ID
    // Важно: один город может быть посещён несколькими подписчиками, поэтому собираем все годы посещений
    const subscriptionCitiesMap = new Map();
    const subscriptionCitiesDataMap = new Map(); // Полные данные о городах подписок (первый объект для каждого города)
    if (actions.subscriptionCities) {
        actions.subscriptionCities.forEach((city) => {
            if (!subscriptionCitiesMap.has(city.id)) {
                subscriptionCitiesMap.set(city.id, {
                    id: city.id,
                    visit_years: []
                });
                // Сохраняем первый объект города для получения полных данных
                subscriptionCitiesDataMap.set(city.id, city);
            }
            // Добавляем годы посещений из текущего объекта
            if (city.visit_years && Array.isArray(city.visit_years)) {
                city.visit_years.forEach((visitYear) => {
                    const cityData = subscriptionCitiesMap.get(city.id);
                    if (cityData && !cityData.visit_years.includes(visitYear)) {
                        cityData.visit_years.push(visitYear);
                    }
                });
            }
        });
    }

    // Получаем информацию о пользователях, которые посещали города в выбранном году (один раз перед циклом)
    const usersWhoVisitedCity = actions.getUsersWhoVisitedCity(year);

    // Собираем все уникальные ID городов, которые нужно обработать
    // Собираем из ownCities и subscriptionCities, а не из существующих маркеров
    const allCityIds = new Set();
    if (actions.ownCities) {
        actions.ownCities.forEach((city) => {
            allCityIds.add(city.id);
        });
    }
    if (actions.subscriptionCities) {
        actions.subscriptionCities.forEach((city) => {
            allCityIds.add(city.id);
        });
    }

    // Удаляем все существующие маркеры своих городов и городов подписок с карты
    actions.stateOwnCities.forEach((marker, cityId) => {
        if (map.hasLayer(marker)) {
            map.removeLayer(marker);
        }
    });
    if (actions.stateSubscriptionCities) {
        actions.stateSubscriptionCities.forEach((marker, cityId) => {
            if (map.hasLayer(marker)) {
                map.removeLayer(marker);
            }
        });
    }

    // Очищаем словари маркеров
    actions.stateOwnCities.clear();
    actions.stateSubscriptionCities.clear();

    // Пересоздаём маркеры с правильным типом в зависимости от того, кто посещал город в выбранном году
    const visibleMarkers = [];

    for (const cityId of allCityIds) {
        const ownCityData = ownCitiesMap.get(cityId);
        const subscriptionCityData = subscriptionCitiesMap.get(cityId);
        const subscriptionCityFullData = subscriptionCitiesDataMap.get(cityId);

        // Определяем, кто посещал город в выбранном году
        const iVisitedInYear = ownCityData && ownCityData.visit_years && ownCityData.visit_years.includes(year);
        const subscriptionVisitedInYear = subscriptionCityData && subscriptionCityData.visit_years && subscriptionCityData.visit_years.includes(year);

        // Если никто не посещал город в выбранном году, пропускаем его
        if (!iVisitedInYear && !subscriptionVisitedInYear) {
            continue;
        }

        let marker;
        let city;

        if (iVisitedInYear && subscriptionVisitedInYear) {
            // Город посещён и мной, и подписчиком → маркер TOGETHER
            city = new City();
            city.id = cityId;
            city.name = ownCityData.title;
            city.region = ownCityData.region_title;
            city.country = ownCityData.country;
            city.lat = ownCityData.lat;
            city.lon = ownCityData.lon;
            city.visit_years = ownCityData.visit_years;
            city.first_visit_date = ownCityData.first_visit_date;
            city.last_visit_date = ownCityData.last_visit_date;
            city.number_of_visits = ownCityData.number_of_visits;

            // Получаем список пользователей с учётом выбранного года (используем предварительно полученный Map)
            const users = usersWhoVisitedCity.get(cityId) || [];
            marker = actions.addMarkerToMap(city, MarkerStyle.TOGETHER, users);
            actions.stateSubscriptionCities.set(cityId, marker);
        } else if (subscriptionVisitedInYear) {
            // Город посещён только подписчиком → маркер SUBSCRIPTION
            if (!subscriptionCityFullData) {
                continue; // Пропускаем, если нет данных о городе подписок
            }
            city = new City();
            city.id = cityId;
            city.name = subscriptionCityFullData.title;
            city.region = subscriptionCityFullData.region_title;
            city.country = subscriptionCityFullData.country;
            city.lat = subscriptionCityFullData.lat;
            city.lon = subscriptionCityFullData.lon;
            // Для городов подписок visit_years берём из ownCities по названию, если город есть там
            const ownCityForSubscription = ownCitiesByName[city.name];
            city.visit_years = ownCityForSubscription ? ownCityForSubscription.visit_years : undefined;
            city.first_visit_date = ownCityForSubscription ? ownCityForSubscription.first_visit_date : undefined;
            city.last_visit_date = ownCityForSubscription ? ownCityForSubscription.last_visit_date : undefined;
            // Получаем number_of_visits из ownCityData, если город есть там
            if (ownCityData) {
                city.number_of_visits = ownCityData.number_of_visits;
            }

            // Получаем список пользователей с учётом выбранного года (используем предварительно полученный Map)
            const users = usersWhoVisitedCity.get(cityId) || [];
            marker = actions.addMarkerToMap(city, MarkerStyle.SUBSCRIPTION, users);
            actions.stateSubscriptionCities.set(cityId, marker);
        } else if (iVisitedInYear) {
            // Город посещён только мной → маркер OWN
            city = new City();
            city.id = cityId;
            city.name = ownCityData.title;
            city.region = ownCityData.region_title;
            city.country = ownCityData.country;
            city.lat = ownCityData.lat;
            city.lon = ownCityData.lon;
            city.visit_years = ownCityData.visit_years;
            city.first_visit_date = ownCityData.first_visit_date;
            city.last_visit_date = ownCityData.last_visit_date;
            city.number_of_visits = ownCityData.number_of_visits;

            marker = actions.addMarkerToMap(city, MarkerStyle.OWN);
            actions.stateOwnCities.set(cityId, marker);
        }

        if (marker) {
            visibleMarkers.push(marker);
        }
    }

    // Перецентрируем карту по видимым городам
    if (visibleMarkers.length > 0) {
        const group = new L.featureGroup(visibleMarkers);
        map.fitBounds(group.getBounds());
    }
    
    // Обновляем состояние кнопки "Показать непосещённые города"
    updateNotVisitedCitiesButtonState();
}
