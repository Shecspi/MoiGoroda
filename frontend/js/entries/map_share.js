import * as L from 'leaflet';
import {create_map} from '../components/map.js';
import {icon_visited_pin} from '../components/icons.js';

// Инициализация карты после загрузки DOM
window.addEventListener('DOMContentLoaded', () => {
    // Массив, хранящий в себе все созданные маркеры.
    // Нужен для того, чтобы отцентрировать и отмасштабировать карту.
    const allMarkers = [];

    // Массив с городами региона
    // [{lat, lon, name}]
    const cities = window.ALL_CITIES || [];
    
    // Проверяем формат данных
    if (!Array.isArray(cities)) {
        return;
    }

    // Отображаем карту на странице
    const map = create_map();
    map.setView([60, 50], 4);

    // Отображаем на карте все города
    for (let i = 0; i < cities.length; i++) {
        const city = cities[i];
        const lat = city.lat;
        const lon = city.lon;
        const name = city.name;

        if (lat != null && lon != null && name) {
            const marker = L.marker([lat, lon], {icon: icon_visited_pin}).addTo(map);
            marker.bindTooltip(name, {direction: 'top'});
            allMarkers.push(marker);
        }
    }

    // Центрируем и масштабируем карту
    if (allMarkers.length > 0) {
        const group = new L.featureGroup([...allMarkers]);
        map.fitBounds(group.getBounds());
    } else {
        // Если городов нет, устанавливаем вид по умолчанию
        map.setView([60, 50], 4);
    }
});