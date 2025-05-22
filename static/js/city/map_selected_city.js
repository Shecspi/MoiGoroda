import {addExternalBorderControl, addInternalBorderControl, create_map} from "../map.js";
import {icon_visited_pin} from "../icons.js";

function openDeleteModal(city_id, city_title) {
    document.getElementById('cityTitleOnModal').textContent = city_title;
    let url = "{% url 'city-delete' 0 %}".replace('0', city_id);
    document.getElementById('deleteCityForm').action = url;
    new bootstrap.Modal(document.getElementById('deleteModal')).show();
}
let map;

function initMap() {
    const lat = parseFloat(window.LAT.replace(',', '.'));
    const lon = parseFloat(window.LON.replace(',', '.'));

    map = create_map();
    map.setView([lat, lon], 7);
    const marker = L.marker([lat, lon], {icon: icon_visited_pin}).addTo(map);
    marker.bindTooltip(window.CITY_TITLE, {
        direction: 'top',
        permanent: true,
    });

    // Загружаем полигон региона
    const [country, region] = window.ISO3166.split('-')
    const url = `${URL_GEO_POLYGONS}/region/hq/${country}/${region}`;
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(response.statusText);
            }
            return response.json();
        })
        .then(geoJson => {
            const myStyle = {
                fillOpacity: 0.1,
                fillColor: '#6382ff',
                weight: 2,
                color: '#0033ff',
                opacity: 0.3
            };
            L.geoJSON(geoJson, { style: myStyle }).addTo(map);
        })
        .catch(error => {
            console.log('Произошла ошибка при загрузке границ региона:\n' + error);
        });
}

// Перерисовываем карту при показе модального окна
document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('mapModal');

    modal.addEventListener('shown.bs.modal', () => {
        if (!map) {
            initMap();
        } else {
            map.invalidateSize();
        }
    });
});