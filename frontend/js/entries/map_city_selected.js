import {create_map} from "../components/map";
import {icon_visited_pin} from "../components/icons";

let map;

function openDeleteModal(url) {
    document.getElementById('cityTitleOnModal').textContent = window.CITY_TITLE;
    document.getElementById('deleteCityForm').action = url;
    new bootstrap.Modal(document.getElementById('deleteModal')).show();
}

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

    // Загружаем полигон региона или страны
    let url;
    if (window.ISO3166) {
        const [country, region] = window.ISO3166.split('-');
        url = `${URL_GEO_POLYGONS}/region/hq/${country}/${region}`;
    } else {
        url = `${URL_GEO_POLYGONS}/country/hq/${window.COUNTRY_CODE}`;
    }

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

document.querySelectorAll('.delete_city').forEach(item => {
    item.addEventListener('click', () => {
        event.preventDefault();
        openDeleteModal(item.dataset.delete_url);
    })
})