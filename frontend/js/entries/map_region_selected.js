/**
 * Реализует отображение карты региона с метками городов и границами региона.
 *
 * ----------------------------------------------
 *
 * Copyright © Egor Vavilov (Shecspi)
 * Licensed under the Apache License, Version 2.0
 *
 * ----------------------------------------------
 */

import L from 'leaflet';
import {create_map} from '../components/map.js';
import {initAddCityForm} from "../components/add_city_modal.js";
import {icon_visited_pin, icon_not_visited_pin} from '../components/icons.js';
import {bindPopupToMarker} from '../components/city_popup.js';

// Стили для полигона региона
const fillOpacity = 0.1;
const fillColor = '#6382ff';
const strokeColor = '#0033ff';
const strokeOpacity = 0.3;
const strokeWidth = 2;

// Получаем код региона из DOM
const iso3166_code = document.getElementById('iso3166_code').dataset.iso3166_code;
const region_code = iso3166_code.split('-')[1];
const country_code = iso3166_code.split('-')[0];

// Массив с городами региона
// ['latitude', 'longitude', 'city name', 'is_visited']
const all_cities = window.ALL_CITIES || [];

const regionName = window.REGION_NAME || '';
const countryName = window.COUNTRY_NAME || '';

// Массив, хранящий в себе все созданные маркеры.
// Нужен для того, чтобы отцентрировать и отмасштабировать карту.
const allMarkers = [];
const markersByCityId = new Map();

// Создаём карту используя общий компонент
const map = create_map();
window.MG_MAIN_MAP = map;

// Отображаем на карте все города, меняя тип иконки в зависимости от того, посещён город или нет
const regionLink = window.REGION_LIST_URL || '';
const countryCitiesBaseUrl = window.COUNTRY_CITIES_BASE_URL || '';
const isAuthenticated = typeof window.IS_AUTHENTICATED !== 'undefined' && window.IS_AUTHENTICATED === true;

for (let i = 0; i < all_cities.length; i++) {
    const city = all_cities[i];
    const icon = city.isVisited ? icon_visited_pin : icon_not_visited_pin;
    const marker = L.marker([city.lat, city.lon], {icon: icon}).addTo(map);
    
    const countryLink = countryCitiesBaseUrl ? `${countryCitiesBaseUrl}?country=${encodeURIComponent(country_code)}` : '';
    const popupOptions = {
        regionName: regionName,
        countryName: countryName,
        regionLink: regionLink,
        countryLink: countryLink,
        showAddButton: isAuthenticated
    };
    
    bindPopupToMarker(marker, city, popupOptions);

    allMarkers.push(marker);
    markersByCityId.set(city.id, {marker, cityData: city});
}

// Загружаем полигон региона
const url = `${window.URL_GEO_POLYGONS}/region/hq/${country_code}/${region_code}`;
fetch(url)
    .then(response => {
        if (!response.ok) {
            throw new Error(response.statusText);
        }
        return response.json();
    })
    .then(geoJson => {
        const myStyle = {
            fillOpacity: fillOpacity,
            fillColor: fillColor,
            weight: strokeWidth,
            color: strokeColor,
            opacity: strokeOpacity
        };
        const geojson = L.geoJSON(geoJson, {
            style: myStyle,
        }).addTo(map);
        
        // Если нет маркеров, центрируем карту по границам региона
        if (allMarkers.length === 0) {
            map.fitBounds(geojson.getBounds());
        }
    })
    .catch(error => {
        console.log('Произошла ошибка при загрузке границ региона:\n' + error);
    });

// Центрируем и масштабируем карту по маркерам городов
if (allMarkers.length > 0) {
    const group = new L.featureGroup([...allMarkers]);
    map.fitBounds(group.getBounds());
}

/**
 * Обновляет бейджик с количеством посещённых городов в тулбаре
 */
const updateVisitedCitiesBadge = () => {
    const statBadge = document.querySelector('.stat-badge-success');
    if (!statBadge) {
        return;
    }

    const strongElement = statBadge.querySelector('strong');
    if (!strongElement) {
        return;
    }

    const currentValue = parseInt(strongElement.textContent, 10);
    if (!isNaN(currentValue)) {
        const newValue = currentValue + 1;
        strongElement.textContent = newValue.toString();
    }
};

// Инициализируем форму добавления города, если она есть на странице
if (document.getElementById('form-add-city')) {
    initAddCityForm(null, (updatedCity) => {
        const stored = markersByCityId.get(updatedCity.id);
        if (!stored) {
            return;
        }

        const {marker, cityData} = stored;

        // Обновляем данные о городе из ответа сервера
        const newCityData = {
            ...cityData,
            isVisited: true,
            numberOfVisits: updatedCity.number_of_visits,
            firstVisitDate: updatedCity.first_visit_date,
            lastVisitDate: updatedCity.last_visit_date,
            numberOfUsersWhoVisitCity: updatedCity.number_of_users_who_visit_city ?? null,
            numberOfVisitsAllUsers: updatedCity.number_of_visits_all_users ?? null,
        };

        // Обновляем маркер и popup
        marker.setIcon(icon_visited_pin);
        marker.unbindPopup();
        marker.unbindTooltip();
        marker.off();
        
        const countryLink = countryCitiesBaseUrl ? `${countryCitiesBaseUrl}?country=${encodeURIComponent(country_code)}` : '';
        const popupOptions = {
            regionName: regionName,
            countryName: countryName,
            regionLink: regionLink,
            countryLink: countryLink,
            showAddButton: isAuthenticated
        };
        bindPopupToMarker(marker, newCityData, popupOptions);

        // Сохраняем обновлённые данные
        markersByCityId.set(updatedCity.id, {marker, cityData: newCityData});

        // Обновляем бейджик в тулбаре только если это первое посещение города
        const isFirstVisit = !cityData.isVisited;
        if (isFirstVisit) {
            updateVisitedCitiesBadge();
        }
    });
}
