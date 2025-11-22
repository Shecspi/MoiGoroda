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

// Массив, хранящий в себе все созданные маркеры.
// Нужен для того, чтобы отцентрировать и отмасштабировать карту.
const allMarkers = [];

// Массив с городами коллекции
// ['lat', 'lon', 'name', 'is_visited']
const cities = window.CITIES_DATA || [];

// Создаём карту используя общий компонент
const map = create_map();

// Отображаем на карте все города, меняя тип иконки в зависимости от того, посещён город или нет
for (let i = 0; i < cities.length; i++) {
    const lat = cities[i].lat;
    const lon = cities[i].lon;
    const name = cities[i].name;
    const is_visited = cities[i].is_visited;

    const icon = (is_visited === true) ? icon_visited_pin : icon_not_visited_pin;
    const marker = L.marker([lat, lon], {icon: icon}).addTo(map);
    marker.bindTooltip(name, {direction: 'top'});

    allMarkers.push(marker);
}

// Центрируем и масштабируем карту
if (allMarkers.length > 0) {
    const group = new L.featureGroup([...allMarkers]);
    map.fitBounds(group.getBounds());
} else {
    // Если городов нет, устанавливаем вид по умолчанию
    map.setView([60, 50], 4);
}
