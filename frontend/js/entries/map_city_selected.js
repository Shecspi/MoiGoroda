import {create_map} from "../components/map";
import {icon_visited_pin} from "../components/icons";
import L from "leaflet";

let map;

function setupDeleteModal(url, cityTitle) {
    document.getElementById('cityTitleOnModal').textContent = cityTitle;
    document.getElementById('deleteCityForm').action = url;
}

function initMap() {
    const lat = parseFloat(window.LAT.replace(',', '.'));
    const lon = parseFloat(window.LON.replace(',', '.'));

    map = create_map();
    // map.setView([lat, lon], 7);
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
            const polygon = L.geoJSON(geoJson, { style: myStyle }).addTo(map);
            const group = new L.featureGroup([polygon]);
            map.fitBounds(group.getBounds());
        })
        .catch(error => {
            const group = new L.featureGroup([marker]);
            map.fitBounds(group.getBounds());
            console.log('Произошла ошибка при загрузке границ региона:\n' + error);
        });
}

// Перерисовываем карту при показе модального окна Preline UI
document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('mapModal');
    
    if (modal) {
        // Используем MutationObserver для отслеживания изменений класса 'open'
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                    if (modal.classList.contains('open') && !modal.classList.contains('hidden')) {
                        // Небольшая задержка для завершения анимации
                        setTimeout(() => {
                            if (!map) {
                                initMap();
                            } else {
                                map.invalidateSize();
                            }
                        }, 100);
                    }
                }
            });
        });
        
        observer.observe(modal, {
            attributes: true,
            attributeFilter: ['class']
        });
    }
});

// Обработка клика на кнопку удаления - устанавливаем данные перед открытием модального окна
document.querySelectorAll('.delete_city').forEach(item => {
    item.addEventListener('click', (event) => {
        event.preventDefault();
        const deleteUrl = item.dataset.delete_url;
        const cityTitle = item.dataset.city_title || window.CITY_TITLE;
        setupDeleteModal(deleteUrl, cityTitle);
    });
});

// Также обрабатываем событие открытия модального окна Preline UI на случай, если данные не были установлены
document.addEventListener('DOMContentLoaded', () => {
    const deleteModal = document.getElementById('deleteModal');
    if (deleteModal) {
        deleteModal.addEventListener('open.hs.overlay', () => {
            // Если данные не были установлены, используем значения по умолчанию
            const cityTitleElement = document.getElementById('cityTitleOnModal');
            const form = document.getElementById('deleteCityForm');
            if (cityTitleElement && !cityTitleElement.textContent && window.CITY_TITLE) {
                cityTitleElement.textContent = window.CITY_TITLE;
            }
            if (form && !form.action) {
                // Если action не установлен, можно установить значение по умолчанию или оставить пустым
            }
        });
    }
});