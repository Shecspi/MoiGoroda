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
const isCollectionOwner = typeof window.IS_COLLECTION_OWNER !== 'undefined' && window.IS_COLLECTION_OWNER === true;
const isOwnerFlagProvided = typeof window.IS_COLLECTION_OWNER !== 'undefined';
const canMarkVisited = isOwnerFlagProvided ? isCollectionOwner : isAuthenticated;
const collectionOwnerUsername = window.COLLECTION_OWNER_USERNAME || null;

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
        isAuthenticated: isAuthenticated,
        canMarkVisited: canMarkVisited,
        isCollectionOwner: isCollectionOwner,
        collectionOwnerUsername: collectionOwnerUsername
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
    const statBadge = document.querySelector('.js-visited-cities-stat');
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

document.addEventListener('city-added', (e) => {
    const { city: updatedCity } = e.detail;
    const stored = markersByCityId.get(updatedCity.id);
    if (!stored) {
        return;
    }

    const {marker, cityData} = stored;

    const newCityData = {
        ...cityData,
        isVisited: true,
        numberOfVisits: updatedCity.number_of_visits,
        firstVisitDate: updatedCity.first_visit_date,
        lastVisitDate: updatedCity.last_visit_date,
        numberOfUsersWhoVisitCity: updatedCity.number_of_users_who_visit_city ?? null,
        numberOfVisitsAllUsers: updatedCity.number_of_visits_all_users ?? null,
        regionName: cityData.regionName,
        regionId: cityData.regionId,
        countryName: cityData.countryName,
        countryCode: cityData.countryCode
    };

    marker.setIcon(icon_visited_pin);
    marker.unbindPopup();
    marker.unbindTooltip();
    marker.off();
    
    const regionLink = newCityData.regionId ? `/region/${newCityData.regionId}/list` : null;
    const countryLink = newCityData.countryCode ? `${countryCitiesBaseUrl}?country=${encodeURIComponent(newCityData.countryCode)}` : null;
    
    const popupOptions = {
        regionName: newCityData.regionName || null,
        countryName: newCityData.countryName || null,
        regionLink: regionLink,
        countryLink: countryLink,
        isAuthenticated: isAuthenticated,
        canMarkVisited: canMarkVisited,
        isCollectionOwner: isCollectionOwner,
        collectionOwnerUsername: collectionOwnerUsername
    };
    bindPopupToMarker(marker, newCityData, popupOptions);

    markersByCityId.set(updatedCity.id, {marker, cityData: newCityData});

    const isFirstVisit = !cityData.isVisited;
    if (isFirstVisit) {
        updateVisitedCitiesBadge();
    }
});
