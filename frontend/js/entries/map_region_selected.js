import * as L from 'leaflet';
import 'leaflet-fullscreen';
import {SimpleMapScreenshoter} from 'leaflet-simple-map-screenshoter';

const fillOpacity = 0.1;
const fillColor = '#6382ff';
const strokeColor = '#0033ff';
const strokeOpacity = 0.3;
const strokeWidth = 2;
const iso3166_code = document.getElementById('iso3166_code').dataset.iso3166_code
const region_code = iso3166_code.split('-')[1];
const country_code = iso3166_code.split('-')[0];

let map;

/**
 * Добавляет кнопки приближения и отдаления карты, а также полноэкранного режима.
 */
function addControlsToMap() {
    const myAttrControl = L.control.attribution().addTo(map);
    myAttrControl.setPrefix('<a href="https://leafletjs.com/">Leaflet</a>');
    L.tileLayer(`${window.TILE_LAYER}`, {
        maxZoom: 19,
        attribution: 'Используются карты &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> под лицензией <a href="https://opendatacommons.org/licenses/odbl/">ODbL.</a>'
    }).addTo(map);

    // Добавляем кнопки приближения и отдаления карты.
    // Их пришлось удалить и вручную добавить, чтобы перевести текст подсказки на русский.
    const zoomControl = L.control.zoom({
      zoomInTitle: 'Нажмите, чтобы приблизить карту',
      zoomOutTitle: 'Нажмите, чтобы отдалить карту'
    });
    zoomControl.addTo(map);

    // Добавляем кнопку полноэкранного режима
    map.addControl(new L.Control.Fullscreen({
        title: {
            'false': 'Полноэкранный режим',
            'true': 'Выйти из полноэкранного режима'
        }
    }));
}

let all_cities = window.ALL_CITIES;

map = L.map('map', {
    attributionControl: false,
    zoomControl: false,
    center: [55.751244, 37.618423],
    zoom: 3
});
addControlsToMap();
new SimpleMapScreenshoter().addTo(map);

const allMarkers = [];

// Отображаем на карте все города,
// меняя цвет иконки в зависимости от того, посещён город или нет
for (let i = 0; i < (all_cities.length); i++) {
    let coordinateWidth = all_cities[i][0];
    let coordinateLongitude = all_cities[i][1];
    let city = all_cities[i][2];

    // TODO: Использовать глобальные иконки без дублирования кода
    // Иконка для посещённого пользователем города
    const icon_visited_pin = L.divIcon({
        className: 'custom-icon-visited-pin',
        html: '<i class="fa-solid fa-location-dot fs-3 icon-visited-pin" style="color: rgb(90, 170, 90) !important; text-shadow: 0 0 2px #333333;"></i>',
        iconSize: [21, 28],
        anchor: [10.5, 28],
        iconAnchor: [10.5, 28],
        popupAnchor: [0, -28],
        tooltipAnchor: [0, -28]
    });
    // Иконка для города, который не посетил ни пользователь, ни те, на кого он подписан
    const icon_not_visited_pin = L.divIcon({
        className: 'custom-icon-not_visited-pin',
        html: '<i class="fa-solid fa-location-dot fs-3 icon-not-visited-pin" style="color: rgb(210, 90, 90) !important; text-shadow: 0 0 2px #333333;"></i>',
        iconSize: [21, 28],
        anchor: [10.5, 28],
        iconAnchor: [10.5, 28],
        popupAnchor: [0, -28],
        tooltipAnchor: [0, -28]
    });
    const icon = (all_cities[i][3] === true) ? icon_visited_pin : icon_not_visited_pin;
    const marker = L.marker([coordinateWidth, coordinateLongitude], {icon: icon}).addTo(map);
    marker.bindTooltip(city, {direction: 'top'});

    allMarkers.push(marker);
}

// Загружаем полигон региона
const url = `${window.URL_GEO_POLYGONS}/region/hq/${country_code}/${region_code}`
fetch(url)
    .then(response => {
        if (!response.ok) {
            throw new Error(response.statusText)
        }
        return response.json()
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
        if (allMarkers.length === 0) {
            map.fitBounds(geojson.getBounds());
        }
    })
    .catch(error => {
        console.log('Произошла ошибка при загрузке границ региона:\n' + error);
    });

// Центрируем и масштабируем карту
if (allMarkers.length > 0) {
    const group = new L.featureGroup([...allMarkers]);
    map.fitBounds(group.getBounds());
}