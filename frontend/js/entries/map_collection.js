/**
 * Реализует отображение карты коллекции с метками городов.
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
import {pluralize} from '../components/search_services.js';

// Массив с городами коллекции
const all_cities = window.ALL_CITIES || [];

// Массив, хранящий в себе все созданные маркеры.
// Нужен для того, чтобы отцентрировать и отмасштабировать карту.
const allMarkers = [];
const markersByCityId = new Map();

// Создаём карту используя общий компонент
const map = create_map();
window.MG_MAIN_MAP = map;

// Получаем данные из window
const collectionListUrl = window.COLLECTION_LIST_URL || '';
const countryCitiesBaseUrl = window.COUNTRY_CITIES_BASE_URL || '';
const isAuthenticated = typeof window.IS_AUTHENTICATED !== 'undefined' && window.IS_AUTHENTICATED === true;

// Отображаем на карте все города, меняя тип иконки в зависимости от того, посещён город или нет
for (let i = 0; i < all_cities.length; i++) {
    const city = all_cities[i];
    const icon = city.isVisited ? icon_visited_pin : icon_not_visited_pin;
    const marker = L.marker([city.lat, city.lon], {icon: icon}).addTo(map);
    
    // Формируем ссылки на регион и страну
    const regionLink = city.regionId ? `/region/${city.regionId}/list` : null;
    const countryLink = city.countryCode ? `${countryCitiesBaseUrl}?country=${encodeURIComponent(city.countryCode)}` : null;
    
    const popupOptions = {
        regionName: city.regionName || null,
        countryName: city.countryName || null,
        regionLink: regionLink,
        countryLink: countryLink,
        isAuthenticated: isAuthenticated
    };
    
    bindPopupToMarker(marker, city, popupOptions);

    allMarkers.push(marker);
    markersByCityId.set(city.id, {marker, cityData: city});
}

// Центрируем и масштабируем карту
if (allMarkers.length > 0) {
    const group = new L.featureGroup([...allMarkers]);
    map.fitBounds(group.getBounds());
} else {
    // Если городов нет, устанавливаем вид по умолчанию
    map.setView([60, 50], 4);
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
    const cityWordElement = document.getElementById('visited-cities-word');
    const visitedWordElement = document.getElementById('visited-word');
    
    if (!strongElement) {
        return;
    }

    const currentValue = parseInt(strongElement.textContent, 10);
    if (!isNaN(currentValue)) {
        const newValue = currentValue + 1;
        strongElement.textContent = newValue.toString();
        
        // Обновляем склонение слова "город" используя общую функцию pluralize
        if (cityWordElement) {
            cityWordElement.textContent = pluralize(newValue, 'город', 'города', 'городов');
        }
        
        // Обновляем склонение слова "Посещено" используя pluralize
        if (visitedWordElement) {
            visitedWordElement.textContent = pluralize(newValue, 'Посещён', 'Посещено', 'Посещено');
        }
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
        // Сохраняем данные о регионе и стране из исходных данных, так как API их не возвращает
        const newCityData = {
            ...cityData,
            isVisited: true,
            numberOfVisits: updatedCity.number_of_visits,
            firstVisitDate: updatedCity.first_visit_date,
            lastVisitDate: updatedCity.last_visit_date,
            numberOfUsersWhoVisitCity: updatedCity.number_of_users_who_visit_city ?? null,
            numberOfVisitsAllUsers: updatedCity.number_of_visits_all_users ?? null,
            // Сохраняем данные о регионе и стране из исходных данных
            regionName: cityData.regionName,
            regionId: cityData.regionId,
            countryName: cityData.countryName,
            countryCode: cityData.countryCode
        };

        // Обновляем маркер и popup
        marker.setIcon(icon_visited_pin);
        marker.unbindPopup();
        marker.unbindTooltip();
        marker.off();
        
        // Формируем ссылки на регион и страну
        const regionLink = newCityData.regionId ? `/region/${newCityData.regionId}/list` : null;
        const countryLink = newCityData.countryCode ? `${countryCitiesBaseUrl}?country=${encodeURIComponent(newCityData.countryCode)}` : null;
        
        const popupOptions = {
            regionName: newCityData.regionName || null,
            countryName: newCityData.countryName || null,
            regionLink: regionLink,
            countryLink: countryLink,
            isAuthenticated: isAuthenticated
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
