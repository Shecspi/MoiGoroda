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
import {getCookie} from '../components/get_cookie.js';
import {pluralize} from '../components/search_services.js';

let map;
let districtsData = new Map(); // district_name -> {id, is_visited, area, population}
let geoJsonLayers = [];
let currentCityId = null;
let cachedGeoJson = null;

// Стили для полигонов (используются те же параметры, что и на карте регионов)
const visitedStyle = {
    fillColor: '#4fbf4f', // зелёный для 41-60% посещённости - более светлый оттенок
    fillOpacity: 0.7,
    color: '#444444', // тёмно-серый цвет границы
    weight: 1,
    opacity: 0.6,
};

const notVisitedStyle = {
    fillColor: '#bbbbbb', // серый - цвет для непосещённого региона
    fillOpacity: 0.85,
    color: '#444444', // тёмно-серый цвет границы
    weight: 1,
    opacity: 0.6,
};

const defaultStyle = {
    fillColor: 'red',
    fillOpacity: 0.6,
    color: '#444444', // тёмно-серый цвет границы
    weight: 1,
    opacity: 0.6,
};

/**
 * Загружает список городов с районами для селектора.
 * Инициализирует Preline UI компонент HSSelect с поиском.
 */
async function loadCitiesForSelect() {
    const select = document.getElementById('city-select');
    if (!select) return;

    try {
        const response = await fetch(window.API_CITIES_URL);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const cities = await response.json();
        
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
            if (parseInt(city.id) === parseInt(window.CITY_ID)) {
                option.selected = true;
            }
            select.appendChild(option);
        });

        // Preline UI автоматически обновит компонент при изменении опций в DOM
        // Если компонент уже был инициализирован, переинициализируем его
        const hsSelectInstance = window.HSSelect && window.HSSelect.getInstance ? window.HSSelect.getInstance('#city-select') : null;
        if (hsSelectInstance && typeof hsSelectInstance.destroy === 'function') {
            hsSelectInstance.destroy();
        }
        
        // Переинициализируем компонент с новыми опциями
        if (window.HSSelect) {
            try {
                new window.HSSelect('#city-select');
            } catch (e) {
                // Если не получилось, используем autoInit
                if (window.HSStaticMethods && typeof window.HSStaticMethods.autoInit === 'function') {
                    window.HSStaticMethods.autoInit();
                }
            }
        }
        
        // Обработчик изменения города (используем делегирование событий, чтобы избежать множественных обработчиков)
        // Удаляем старый обработчик, если он был добавлен ранее
        const oldHandler = select._changeHandler;
        if (oldHandler) {
            select.removeEventListener('change', oldHandler);
        }
        
        // Создаём новый обработчик
        const changeHandler = (e) => {
            const cityId = parseInt(e.target.value);
            if (cityId) {
                window.location.href = `/city/districts/${cityId}/map`;
            }
        };
        
        // Сохраняем ссылку на обработчик для возможности удаления в будущем
        select._changeHandler = changeHandler;
        select.addEventListener('change', changeHandler);
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
        
        // Обновляем бейджик со статистикой
        updateStatsBadge();
        
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
            }, {maxWidth: 400, minWidth: 280});
            
            // Инициализируем Preline UI для элементов в popup после его открытия
            layer.on('popupopen', function() {
                if (window.HSStaticMethods && typeof window.HSStaticMethods.autoInit === 'function') {
                    window.HSStaticMethods.autoInit();
                }
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
    let content = '<div class="px-1.5 py-1.5 min-w-[280px] max-w-[400px]">';
    
    // Заголовок (стиль аналогичный popup для городов)
    content += `<div class="mb-2 pb-1 border-b border-gray-200 dark:border-neutral-700">`;
    content += `<h3 class="text-base font-semibold text-gray-900 dark:text-white mb-0">${districtName}</h3>`;
    content += `</div>`;
    
    if (districtInfo) {
        // Информация о районе (с иконками и бейджиками, как в popup для городов)
        content += '<div class="space-y-1.5 text-sm">';
        
        if (districtInfo.area) {
            content += `<div class="flex items-center justify-between gap-2">`;
            content += `<div class="flex items-center gap-2">`;
            content += `<svg class="size-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"/></svg>`;
            content += `<span class="text-gray-500 dark:text-neutral-400">Площадь:</span>`;
            content += `</div>`;
            content += `<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-500/10 dark:text-blue-400">${districtInfo.area} км²</span>`;
            content += `</div>`;
        }
        
        if (districtInfo.population) {
            content += `<div class="flex items-center justify-between gap-2">`;
            content += `<div class="flex items-center gap-2">`;
            content += `<svg class="size-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/></svg>`;
            content += `<span class="text-gray-500 dark:text-neutral-400">Население:</span>`;
            content += `</div>`;
            content += `<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-500/10 dark:text-purple-400">${districtInfo.population.toLocaleString()}</span>`;
            content += `</div>`;
        }
        
        if (districtInfo.is_visited) {
            content += `<div class="flex items-center justify-between gap-2">`;
            content += `<div class="flex items-center gap-2">`;
            content += `<svg class="size-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`;
            content += `<span class="text-gray-500 dark:text-neutral-400">Статус:</span>`;
            content += `</div>`;
            content += `<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-100 text-emerald-800 dark:bg-emerald-500/10 dark:text-emerald-400">Посещён</span>`;
            content += `</div>`;
        }
        
        content += '</div>';
        
        // Форма отметки посещения для авторизованных пользователей
        if (window.IS_AUTHENTICATED) {
            content += '<div class="mt-2 pt-2 border-t border-gray-200 dark:border-neutral-700">';
            if (districtInfo.is_visited) {
                // Если район посещён, показываем ссылку для удаления
                content += `<a href="#" id="delete-visit-link-${districtInfo.id}" class="text-sm text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 transition-colors">Удалить посещение</a>`;
            } else {
                // Если район не посещён, показываем форму для отметки
                content += `<form id="visit-district-form-${districtInfo.id}">`;
                content += `<input type="hidden" name="city_district_id" value="${districtInfo.id}">`;
                content += `<button type="submit" class="text-sm text-emerald-600 hover:text-emerald-700 dark:text-emerald-400 dark:hover:text-emerald-300 transition-colors">`;
                content += 'Отметить как посещённый';
                content += `</button>`;
                content += `</form>`;
            }
            content += '</div>';
        }
    } else {
        content += '<div class="space-y-1.5 text-sm">';
        content += `<div class="text-sm">`;
        content += `<span class="text-gray-900 dark:text-white">Информация о районе отсутствует</span>`;
        content += `</div>`;
        content += '</div>';
    }
    
    content += '</div>';
    return content;
}

/**
 * Обновляет текст бейджика со статистикой посещённых районов.
 */
function updateStatsBadge() {
    if (!window.IS_AUTHENTICATED) {
        return;
    }

    const badgeElement = document.querySelector('#section-stats .stat-badge');
    if (!badgeElement) {
        return;
    }

    // Подсчитываем количество посещённых районов
    let qtyOfVisitedDistricts = 0;
    let qtyOfDistricts = 0;
    
    districtsData.forEach((districtInfo) => {
        qtyOfDistricts++;
        if (districtInfo.is_visited) {
            qtyOfVisitedDistricts++;
        }
    });

    if (qtyOfDistricts > 0) {
        const word = pluralize(qtyOfVisitedDistricts, 'район', 'района', 'районов');
        badgeElement.innerHTML = `
            <span class="stat-badge-dot"></span>
            Посещено <strong>${qtyOfVisitedDistricts}</strong> ${word} из ${qtyOfDistricts}
        `;
    } else {
        badgeElement.innerHTML = `
            <span class="stat-badge-dot"></span>
            Нет информации о районах
        `;
    }
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
    };
    
    fetch(window.API_VISIT_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify(data),
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    const errorMessage = err.detail || err.city_district_id?.[0] || 'Ошибка при сохранении';
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
                    
                    // Обновляем бейджик со статистикой
                    updateStatsBadge();
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
 * Обрабатывает удаление посещения района.
 */
async function handleDeleteVisit(districtId, districtName) {
    if (!window.API_VISIT_DELETE_URL) {
        console.error('URL для удаления посещения не определён');
        return;
    }

    const data = {
        city_district_id: districtId,
    };

    try {
        const response = await fetch(window.API_VISIT_DELETE_URL, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            const err = await response.json();
            const errorMessage = err.detail || 'Ошибка при удалении посещения';
            throw new Error(errorMessage);
        }

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
                
                // Обновляем бейджик со статистикой
                updateStatsBadge();
            }
        }

        // Показываем уведомление об успехе
        const message = `Посещение района <span class="font-semibold">${districtName}</span> успешно удалено`;
        showSuccessToast('Успешно', message);

        // Закрываем popup
        map.closePopup();
    } catch (error) {
        console.error('Ошибка при удалении посещения:', error);
        alert('Ошибка при удалении: ' + error.message);
    }
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

    // Обработчик клика на ссылки удаления посещения (делегирование событий)
    document.addEventListener('click', (event) => {
        const target = event.target;
        if (target.id && target.id.startsWith('delete-visit-link-')) {
            event.preventDefault();
            const districtId = parseInt(target.id.replace('delete-visit-link-', ''));
            const districtName = Array.from(districtsData.keys()).find(name => {
                const info = districtsData.get(name);
                return info && info.id === districtId;
            });
            if (districtName) {
                handleDeleteVisit(districtId, districtName);
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
