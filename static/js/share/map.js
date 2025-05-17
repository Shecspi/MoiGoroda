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

    // Добавляем кнопку создания скриншота
    L.simpleMapScreenshoter().addTo(map);
}

// Массив с городами региона
// ['lat', 'lon', 'name']
const cities = window.ALL_CITIES || [];

// Отображаем карту на странице
const map = L.map('map', {
    attributionControl: false,
    zoomControl: false
}).setView([60, 50], 4);
addControlsToMap();

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