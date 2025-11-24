import * as L from 'leaflet';
import {create_map} from '../components/map.js';

// Массив, хранящий в себе все созданные маркеры.
// Нужен для того, чтобы отцентрировать и отмасштабировать карту.
const allMarkers = [];

// Иконка для посещённого пользователем города
const icon = L.divIcon({
    className: 'custom-icon-visited-pin',
    html: '<i class="fa-solid fa-location-dot fs-3 icon-visited-pin" style="color: rgb(90, 170, 90) !important; text-shadow: 0 0 2px #333333;"></i>',
    iconSize: [21, 28],
    anchor: [10.5, 28],
    iconAnchor: [10.5, 28],
    popupAnchor: [0, -28],
    tooltipAnchor: [0, -28]
});

// Массив с городами региона
// ['lat', 'lon', 'name']
const cities = window.ALL_CITIES || [];

// Отображаем карту на странице
const map = create_map();
map.setView([60, 50], 4);

// Отображаем на карте все города
for (let i = 0; i < (cities.length); i++) {
    let lat = cities[i].lat;
    let lon = cities[i].lon;
    let name = cities[i].name;

    const marker = L.marker([lat, lon], {icon: icon}).addTo(map);
    marker.bindTooltip(name, {direction: 'top'});

    allMarkers.push(marker);
}

// Центрируем и масштабируем карту
const group = new L.featureGroup([...allMarkers]);
map.fitBounds(group.getBounds());