import {create_map} from "../components/map";
import {icon_blue_pin, icon_not_visited_pin, icon_visited_pin} from "../components/icons";
import {buildCityPolygonUrl, getCityPolygonStyle} from "../components/region_city_polygons";
import L from "leaflet";

let map;

/** Стиль полигона города на странице деталей (без зелёного/красного для гостей). */
function getCityDetailPolygonStyle() {
    if (!window.IS_AUTHENTICATED) {
        return {
            fillColor: "rgb(99, 130, 255)",
            fillOpacity: 0.4,
            color: "rgb(0, 51, 255)",
            weight: 2,
            opacity: 0.8,
        };
    }
    return getCityPolygonStyle({isVisited: window.IS_VISITED});
}

function getCityDetailMarkerIcon() {
    if (!window.IS_AUTHENTICATED) {
        return icon_blue_pin;
    }
    return window.IS_VISITED ? icon_visited_pin : icon_not_visited_pin;
}

function setupDeleteModal(url, cityTitle) {
    document.getElementById('cityTitleOnModal').textContent = cityTitle;
    document.getElementById('deleteCityForm').action = url;
}

function initMap() {
    const lat = parseFloat(window.LAT.replace(',', '.'));
    const lon = parseFloat(window.LON.replace(',', '.'));

    map = create_map();

    const marker = L.marker([lat, lon], {icon: getCityDetailMarkerIcon()});
    marker.bindTooltip(window.CITY_TITLE, {
        direction: 'top',
        permanent: true,
    });

    // Загружаем полигон региона или страны (фон)
    let regionUrl;
    if (window.ISO3166) {
        const [country, region] = window.ISO3166.split('-');
        regionUrl = `${URL_GEO_POLYGONS}/region/hq/${country}/${region}`;
    } else {
        regionUrl = `${URL_GEO_POLYGONS}/country/hq/${window.COUNTRY_CODE}`;
    }

    const regionPolygonPromise = fetch(regionUrl)
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
            return L.geoJSON(geoJson, {style: myStyle}).addTo(map);
        })
        .catch(error => {
            console.log('Произошла ошибка при загрузке границ региона:\n' + error);
            return null;
        });

    // Загружаем полигон города
    const hasRegion = window.ISO3166 && window.ISO3166.includes('-');
    let cityPolygonPromise = null;

    if (hasRegion) {
        const [countryCode, regionCode] = window.ISO3166.split('-');
        const cityUrl = buildCityPolygonUrl(window.CITY_TITLE, countryCode, regionCode);
        cityPolygonPromise = fetch(cityUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error(response.statusText);
                }
                return response.json();
            })
            .then(geoJson => {
                const style = getCityDetailPolygonStyle();
                return L.geoJSON(geoJson, {style: style}).addTo(map);
            })
            .catch(error => {
                console.log('Произошла ошибка при загрузке границ города:\n' + error);
                return null;
            });
    }

    // Масштабируем карту: полигон города или маркер как fallback
    Promise.all([regionPolygonPromise, cityPolygonPromise])
        .then(([regionPolygon, cityPolygon]) => {
            if (cityPolygon) {
                map.fitBounds(cityPolygon.getBounds());
                return;
            }

            marker.addTo(map);
            const fitLayers = [marker];
            if (regionPolygon) {
                fitLayers.unshift(regionPolygon);
            }
            map.fitBounds(L.featureGroup(fitLayers).getBounds());
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