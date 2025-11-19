import * as L from 'leaflet';
import 'leaflet-fullscreen';
import {SimpleMapScreenshoter} from 'leaflet-simple-map-screenshoter';
import {initCountrySelect} from "../components/initCountrySelect";
import {addLoadControl, addErrorControl, create_map} from "../components/map";

const fillOpacity = 0.7;
const fillOpacityHighlight = 0.9;
const strokeColor = '#444444';
const strokeOpacity = 0.2;
const strokeOpacityHighlight = 0.2;
const strokeWidth = 1;
const strokeWidthHighlight = 2;

let map;

document.addEventListener('DOMContentLoaded', async (event) => {
    await initCountrySelect({showAllOption: false});
});

function init() {
    const map = create_map();
    if (window.NUMBER_OF_REGIONS > 0) {
        createLegendControl(map);
    }
    const load = addLoadControl(map, 'Загружаю регионы...');

    const allMarkers = [];

    let url_all_geo_polygons;
    if (window.NUMBER_OF_REGIONS > 0) {
        url_all_geo_polygons = `${window.URL_GEO_POLYGONS}/region/lq/${window.COUNTRY_CODE}/all`;
    } else {
        url_all_geo_polygons = `${window.URL_GEO_POLYGONS}/country/hq/${window.COUNTRY_CODE}`;
    }

    fetch(url_all_geo_polygons)
        .then(response => {
            if (!response.ok) {
                throw new Error(response.statusText)
            }
            return response.json();
        })
        .then(data => {
            // Добавляем полигоны на карту
            if (window.NUMBER_OF_REGIONS > 0) {
                data.forEach(region => {
                    const iso3166 = region.features[0].properties.iso3166;
                    const title = window.REGION_LIST.get(iso3166).title;
                    const num_visited = window.REGION_LIST.get(iso3166).num_visited;
                    const ratio_visited = window.REGION_LIST.get(iso3166).ratio_visited;

                    let color;
                    if (ratio_visited === undefined || ratio_visited === 0) {
                        color = '#bbbbbb';
                    } else if (ratio_visited > 0 && ratio_visited <= 20) {
                        color = '#b8e2b8';
                    } else if (ratio_visited > 20 && ratio_visited <= 40) {
                        color = '#7fd07f';
                    } else if (ratio_visited > 40 && ratio_visited <= 60) {
                        color = '#4fbf4f';
                    } else if (ratio_visited > 60 && ratio_visited <= 80) {
                        color = '#30b200';
                    } else if (ratio_visited > 80 && ratio_visited < 100) {
                        color = '#228000';
                    } else {
                        color = '#006400';
                    }

                    const myStyle = {
                        "fillColor": color,
                        "fillOpacity": fillOpacity,
                        "weight": strokeWidth,
                        "color": strokeColor,
                        "opacity": strokeOpacity
                    };
                    const geojson = L.geoJSON(region, {
                        style: myStyle,
                        onEachFeature: onEachFeature
                    }).addTo(map);

                    let description = '';
                    if (num_visited > 0) {
                        description += `Посещено городов: ${num_visited}`;
                    } else {
                        description += 'Вы ещё не посетили ни одного города в этом регионе';
                    }
                    description += `<br><br><a href="/region/${window.REGION_LIST.get(iso3166)['id']}/map" `
                        + `class="link-offset-2 link-underline-dark link-dark link-opacity-75 `
                        + `link-underline-opacity-75 link-opacity-100-hover">Карта городов</a><br>`
                        + `<a href="/region/${window.REGION_LIST.get(iso3166)['id']}/list" `
                        + `class="link-offset-2 link-underline-dark link-dark link-opacity-75 `
                        + `link-underline-opacity-75 link-opacity-100-hover">Список городов</a>`
                    geojson.bindPopup(`<h4>${title}</h4><br>${description}`);
                    geojson.bindTooltip(title, {
                        direction: 'top',
                        sticky: true
                    });
                    geojson.on('mouseover', function () {
                        const tooltip = this.getTooltip();
                        if (this.isPopupOpen()) {
                            tooltip.setOpacity(0.0);
                        } else {
                            tooltip.setOpacity(0.9);
                        }
                    });
                    geojson.on('click', function () {
                        this.getTooltip().setOpacity(0.0);
                    });

                    allMarkers.push(geojson);
                });
                const group = new L.featureGroup([...allMarkers]);
                map.fitBounds(group.getBounds());
            } else {
                const myStyle = {
                    fillOpacity: 0.1,
                    fillColor: '#6382ff',
                    weight: 2,
                    color: '#0033ff',
                    opacity: 0.3
                };
                const geoJsonLayer = L.geoJSON(data, { style: myStyle }).addTo(map);
                map.fitBounds(geoJsonLayer.getBounds());
            }
            map.removeControl(load);
        })
        .catch(error => {
            map.removeControl(load);
            addErrorControl(map, 'Произошла ошибка при загрузке регионов');
        });
}

/**
 * Меняет цвет и выделение полигона более акцентированными.
 */
function highlightFeature(e) {
    const layer = e.target;

    layer.setStyle({
        weight: strokeWidthHighlight,
        opacity: strokeOpacityHighlight,
        fillOpacity: fillOpacityHighlight
    });

    layer.bringToFront();
}

/**
 * Возвращает цвет и выделение региона в оригинальные.
 */
function resetHighlight(e) {
    e.target.setStyle({
        weight: strokeWidth,
        opacity: strokeOpacity,
        fillOpacity: fillOpacity
    });
}

/**
 * Увеличивает карту при клике на регион.
 */
function zoomToFeature(e) {
    map.fitBounds(e.target.getBounds());
}

/**
 * Добавляет обработчики событий для полигонов.
 */
function onEachFeature(feature, layer) {
    layer.on({
        mouseover: highlightFeature,
        mouseout: resetHighlight,
        click: zoomToFeature
    });
}

function createLegendControl(map) {
  // Контрол легенды
  const legend = L.control({ position: 'bottomright' });

  legend.onAdd = function () {
    const div = L.DomUtil.create('div', 'legend');
    div.style.display = 'none'; // скрываем по умолчанию
    div.innerHTML = `
      <div class="legend-title">
        <span>Посещённость городов (%)</span>
        <button id="toggle-legend-btn" class="legend-close-btn" title="Скрыть легенду">×</button>
      </div>
      <div class="legend-item"><span class="color-box" style="background:#bbbbbb"></span>Регион не посещён</div>
      <div class="legend-item"><span class="color-box" style="background:#b8e2b8"></span>1% – 20%</div>
      <div class="legend-item"><span class="color-box" style="background:#7fd07f"></span>21% – 40%</div>
      <div class="legend-item"><span class="color-box" style="background:#4fbf4f"></span>41% – 60%</div>
      <div class="legend-item"><span class="color-box" style="background:#30b200"></span>61% – 80%</div>
      <div class="legend-item"><span class="color-box" style="background:#228000"></span>81% – 99%</div>
      <div class="legend-item"><span class="color-box" style="background:#006400"></span>100% - посещены все города</div>
    `;
    L.DomEvent.disableClickPropagation(div);
    return div;
  };

  legend.addTo(map);

  // Контрол кнопки показа легенды
  const showBtn = L.control({ position: 'bottomright' });

  showBtn.onAdd = function () {
    const div = L.DomUtil.create('div', 'show-legend-btn');
    div.innerHTML = `<button class="show-legend-button" title="Показать легенду">Показать легенду</button>`;
    L.DomEvent.disableClickPropagation(div);

    div.querySelector('button').addEventListener('click', () => {
      const legendDiv = document.querySelector('.legend');
      if (legendDiv) {
        legendDiv.style.display = 'block';
      }
      div.style.display = 'none';
    });

    return div;
  };

  showBtn.addTo(map);

  // Делегируем обработчик клика на кнопку закрытия легенды
  document.addEventListener('click', (e) => {
    if (e.target && e.target.id === 'toggle-legend-btn') {
      const legendDiv = document.querySelector('.legend');
      const showBtnDiv = document.querySelector('.show-legend-btn');
      if (legendDiv && showBtnDiv) {
        legendDiv.style.display = 'none';
        showBtnDiv.style.display = 'block';
      }
    }
  });
}


init();