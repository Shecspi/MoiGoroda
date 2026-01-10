/**
 * Реализует отображение карты районов города с полигонами из GeoJSON.
 *
 * ----------------------------------------------
 *
 * Copyright © Egor Vavilov (Shecspi)
 * Licensed under the Apache License, Version 2.0
 *
 * ----------------------------------------------
 */
import L from 'leaflet';
import {create_map, addLoadControl, addErrorControl} from '../components/map.js';
import {showDangerToast, showSuccessToast} from '../components/toast.js';

let map;
let districtsData = new Map(); // district_name -> {id, is_visited, area, population}
let geoJsonLayers = [];
let currentCityId = null;
let cachedGeoJson = null;

// Стили для полигонов
const visitedStyle = {
    fillColor: '#22c55e', // зелёный
    fillOpacity: 0.3,
    color: '#16a34a',
    weight: 2,
    opacity: 0.8,
};

const notVisitedStyle = {
    fillColor: '#9ca3af', // серый
    fillOpacity: 0.3,
    color: '#6b7280',
    weight: 2,
    opacity: 0.8,
};

const defaultStyle = {
    fillColor: '#9ca3af',
    fillOpacity: 0.2,
    color: '#6b7280',
    weight: 1,
    opacity: 0.5,
};

/**
 * Загружает список городов с районами для селектора.
 */
async function loadCitiesForSelect() {
    try {
        const response = await fetch(window.API_CITIES_URL);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const cities = await response.json();
        
        const select = document.getElementById('city-select');
        if (!select) return;
        
        // Очищаем селектор
        select.innerHTML = '';
        
        // Добавляем опцию по умолчанию
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = 'Выберите город...';
        select.appendChild(defaultOption);
        
        // Добавляем города
        cities.forEach(city => {
            const option = document.createElement('option');
            option.value = city.id;
            option.textContent = city.title;
            if (city.id === window.CITY_ID) {
                option.selected = true;
            }
            select.appendChild(option);
        });
        
        // Обработчик изменения города
        select.addEventListener('change', (e) => {
            const cityId = parseInt(e.target.value);
            if (cityId) {
                window.location.href = `/city/districts/${cityId}/map`;
            }
        });
    } catch (error) {
        console.error('Ошибка загрузки списка городов:', error);
    }
}

/**
 * Загружает данные о районах и GeoJSON полигоны параллельно.
 */
async function loadDistrictsData(cityId, countryCode, cityName, regionCode) {
    const loadControl = addLoadControl(map, 'Загружаю данные о районах...');
    
    try {
        // Формируем тело запроса для GeoJSON
        const geoJsonBody = {
            country_code: countryCode,
            city_name: cityName,
            region_code: regionCode,
        };
        
        // Параллельная загрузка данных о районах и GeoJSON
        const [districtsResponse, geoJsonResponse] = await Promise.all([
            fetch(`${window.API_DISTRICTS_URL}`),
            fetch(`${window.URL_GEO_POLYGONS}/city-district/hq`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(geoJsonBody),
            }),
        ]);
        
        map.removeControl(loadControl);
        
        // Обработка ответа с данными о районах
        if (!districtsResponse.ok) {
            if (districtsResponse.status === 404) {
                addErrorControl(map, 'Для этого города нет районов в базе данных');
                return;
            }
            throw new Error(`HTTP error! status: ${districtsResponse.status}`);
        }
        
        const districts = await districtsResponse.json();
        
        // Создаём Map для быстрого поиска по названию
        districtsData.clear();
        districts.forEach(district => {
            districtsData.set(district.title, {
                id: district.id,
                is_visited: district.is_visited || false,
                area: district.area,
                population: district.population,
            });
        });
        
        // Обработка ответа с GeoJSON
        if (!geoJsonResponse.ok) {
            if (geoJsonResponse.status === 404) {
                addErrorControl(map, 'Для этого города нет полигонов районов');
                return;
            }
            throw new Error(`HTTP error! status: ${geoJsonResponse.status}`);
        }
        
        const geoJsonData = await geoJsonResponse.json();
        cachedGeoJson = geoJsonData;
        
        // Отображаем полигоны на карте
        displayDistrictsOnMap(geoJsonData, districtsData);
        
        // Центрируем карту по полигонам
        if (geoJsonLayers.length > 0) {
            const group = new L.featureGroup(geoJsonLayers);
            map.fitBounds(group.getBounds());
        }
        
    } catch (error) {
        map.removeControl(loadControl);
        console.error('Ошибка загрузки данных:', error);
        addErrorControl(map, 'Произошла ошибка при загрузке данных о районах');
        showDangerToast('Ошибка соединения с сервером', 'Не получилось загрузить данные о районах.');
    }
}

/**
 * Отображает полигоны районов на карте.
 */
function displayDistrictsOnMap(geoJsonData, districtsDataMap) {
    // Очищаем предыдущие слои
    geoJsonLayers.forEach(layer => {
        map.removeLayer(layer);
    });
    geoJsonLayers = [];
    
    // Проверяем, что пришло: массив FeatureCollection или один FeatureCollection
    const featureCollections = Array.isArray(geoJsonData) ? geoJsonData : [geoJsonData];
    
    featureCollections.forEach(featureCollection => {
        // Проверяем, что это FeatureCollection
        if (featureCollection.type !== 'FeatureCollection' || !featureCollection.features) {
            console.warn('Неверный формат GeoJSON:', featureCollection);
            return;
        }
        
        // Обрабатываем каждый feature в FeatureCollection
        featureCollection.features.forEach(feature => {
            // Получаем название района из properties.feature
            const districtName = feature.properties?.name || feature.properties?.title || '';
            const districtInfo = districtsDataMap.get(districtName);
            
            // Отладочная информация (можно удалить после проверки)
            if (!districtInfo && districtName) {
                console.log(`Район "${districtName}" не найден в данных БД. Доступные районы:`, Array.from(districtsDataMap.keys()));
            }
            
            // Определяем стиль в зависимости от того, посещён ли район
            const style = districtInfo?.is_visited ? visitedStyle : (districtInfo ? notVisitedStyle : defaultStyle);
            
            // Создаём слой GeoJSON для отдельного feature
            const layer = L.geoJSON(feature, {
                style: style,
            });
            
            // Добавляем popup при клике
            layer.bindPopup(() => {
                return createPopupContent(districtName, districtInfo);
            });
            
            // Добавляем tooltip при наведении
            const tooltip = layer.bindTooltip(districtName, {
                direction: 'top',
                sticky: true
            });
            
            // Предотвращаем перемещение tooltip в центр при клике
            const originalUpdatePosition = tooltip.updatePosition;
            let isClickInProgress = false;
            
            tooltip.updatePosition = function(e) {
                if (isClickInProgress) return;
                return originalUpdatePosition.call(this, e);
            };
            
            // Скрываем tooltip при нажатии мыши
            layer.on('mousedown', function () {
                isClickInProgress = true;
                const tooltip = this.getTooltip();
                if (tooltip) {
                    tooltip.setOpacity(0.0);
                    if (tooltip._container) tooltip._container.style.display = 'none';
                }
            });
            
            layer.on('mouseup', function () {
                setTimeout(() => { isClickInProgress = false; }, 100);
            });
            
            // Показываем tooltip при наведении
            layer.on('mouseover', function () {
                const tooltip = this.getTooltip();
                if (tooltip && !this.isPopupOpen()) {
                    if (tooltip._container) tooltip._container.style.display = '';
                    tooltip.setOpacity(0.9);
                }
            });
            
            // Скрываем tooltip при уходе курсора или открытии/закрытии popup
            layer.on('mouseout popupopen popupclose', function (e) {
                const tooltip = this.getTooltip();
                if (tooltip) {
                    tooltip.setOpacity(0.0);
                    // Для popup всегда скрываем container, для mouseout - только если popup не открыт
                    if (tooltip._container && (e.type === 'popupopen' || e.type === 'popupclose' || !this.isPopupOpen())) {
                        tooltip._container.style.display = 'none';
                    }
                }
            });
            
            layer.addTo(map);
            geoJsonLayers.push(layer);
        });
    });
}

/**
 * Создаёт содержимое popup для района.
 */
function createPopupContent(districtName, districtInfo) {
    let content = `<div class="p-2">`;
    content += `<h3 class="font-semibold text-lg mb-2">${districtName}</h3>`;
    
    if (districtInfo) {
        if (districtInfo.area) {
            content += `<p class="text-sm text-gray-600 dark:text-neutral-400 mb-1">Площадь: ${districtInfo.area} км²</p>`;
        }
        if (districtInfo.population) {
            content += `<p class="text-sm text-gray-600 dark:text-neutral-400 mb-1">Население: ${districtInfo.population.toLocaleString()}</p>`;
        }
        
        // Для авторизованных пользователей добавляем форму отметки посещения
        if (window.IS_AUTHENTICATED) {
            content += `<hr class="my-3 border-gray-200 dark:border-neutral-700">`;
            content += `<form id="visit-district-form-${districtInfo.id}" class="mt-2">`;
            content += `<input type="hidden" name="city_district_id" value="${districtInfo.id}">`;
            content += `<label class="block text-sm font-medium text-gray-700 dark:text-neutral-300 mb-1">`;
            content += `Дата посещения (необязательно):`;
            content += `</label>`;
            content += `<input type="date" name="date_of_visit" class="block w-full rounded-lg border-gray-300 dark:border-neutral-700 dark:bg-neutral-800 dark:text-white mb-2">`;
            content += `<button type="submit" class="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">`;
            content += districtInfo.is_visited ? 'Обновить посещение' : 'Отметить как посещённый';
            content += `</button>`;
            content += `</form>`;
        }
    } else {
        content += `<p class="text-sm text-gray-500 dark:text-neutral-500">Информация о районе отсутствует</p>`;
    }
    
    content += `</div>`;
    return content;
}

/**
 * Обрабатывает отправку формы отметки посещения.
 */
function handleVisitFormSubmit(event, districtId, districtName) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const data = {
        city_district_id: parseInt(formData.get('city_district_id')),
        date_of_visit: formData.get('date_of_visit') || null,
    };
    
    fetch(window.API_VISIT_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    const errorMessage = err.detail || err.city_district_id?.[0] || err.date_of_visit?.[0] || 'Ошибка при сохранении';
                    throw new Error(errorMessage);
                });
            }
            return response.json();
        })
        .then(async result => {
            // Перезагружаем данные о районах для обновления статуса is_visited
            if (window.CITY_ID && window.COUNTRY_CODE && window.CITY_NAME) {
                const districtsResponse = await fetch(`${window.API_DISTRICTS_URL}`);
                if (districtsResponse.ok) {
                    const districts = await districtsResponse.json();
                    districtsData.clear();
                    districts.forEach(district => {
                        districtsData.set(district.title, {
                            id: district.id,
                            is_visited: district.is_visited || false,
                            area: district.area,
                            population: district.population,
                        });
                    });
                    
                    // Перерисовываем полигоны с обновлёнными стилями
                    if (cachedGeoJson) {
                        displayDistrictsOnMap(cachedGeoJson, districtsData);
                    }
                }
            }
            
            // Показываем уведомление об успехе
            const message = `Район <span class="font-semibold">${districtName}</span> успешно отмечен как посещённый`;
            showSuccessToast('Успешно', message);
            
            // Закрываем popup
            map.closePopup();
        })
        .catch(error => {
            console.error('Ошибка при сохранении посещения:', error);
            alert('Ошибка при сохранении: ' + error.message);
        });
}

/**
 * Инициализация карты при загрузке страницы.
 */
async function initDistrictsMap() {
    map = create_map();
    window.MG_MAIN_MAP = map;
    
    // Загружаем список городов для селектора
    await loadCitiesForSelect();
    
    // Загружаем данные о районах текущего города
    if (window.CITY_ID && window.COUNTRY_CODE && window.CITY_NAME) {
        currentCityId = window.CITY_ID;
        await loadDistrictsData(window.CITY_ID, window.COUNTRY_CODE, window.CITY_NAME, window.REGION_CODE);
    }
    
    // Обработчик отправки форм посещения (делегирование событий)
    document.addEventListener('submit', (event) => {
        const form = event.target;
        if (form.id && form.id.startsWith('visit-district-form-')) {
            const districtId = parseInt(form.querySelector('input[name="city_district_id"]').value);
            const districtName = Array.from(districtsData.keys()).find(name => {
                const info = districtsData.get(name);
                return info && info.id === districtId;
            });
            if (districtName) {
                handleVisitFormSubmit(event, districtId, districtName);
            }
        }
    });
}

// Инициализация при загрузке DOM
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDistrictsMap);
} else {
    initDistrictsMap();
}
