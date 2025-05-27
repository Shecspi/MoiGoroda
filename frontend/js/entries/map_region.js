import * as L from 'leaflet';
import 'leaflet-fullscreen';
import {SimpleMapScreenshoter} from 'leaflet-simple-map-screenshoter';

const fillColorVisitedRegion = '#30b200';
const fillColorNotVisitedRegion = '#adadad';
const fillOpacity = 0.6;
const fillOpacityHighlight = 0.8;
const strokeColor = '#444444';
const strokeOpacity = 0.2;
const strokeOpacityHighlight = 0.2;
const strokeWidth = 1;
const strokeWidthHighlight = 2;

let map;

function init() {
    map = L.map('map', {
        attributionControl: false,
        zoomControl: false
    }).setView([60, 50], 4);

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

    // Этот код нужен для того, чтобы убрать ненужный флаг с копирайта.
    const myAttrControl = L.control.attribution().addTo(map);
    myAttrControl.setPrefix('<a href="https://leafletjs.com/">Leaflet</a>');
    L.tileLayer(`${window.TILE_LAYER}`, {
        maxZoom: 19,
        attribution: 'Используются карты &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> под лицензией <a href="https://opendatacommons.org/licenses/odbl/">ODbL.</a>'
    }).addTo(map);

    const load = addLoadControl(map);
    new SimpleMapScreenshoter().addTo(map);

    createLegendControl(map);

    const url_all_geo_polygons = `${window.URL_GEO_POLYGONS}/region/lq/RU/all`;
    fetch(url_all_geo_polygons)
        .then(response => {
            if (!response.ok) {
                throw new Error(response.statusText)
            }
            return response.json();
        })
        .then(data => {
            // Удаляем информацию о загрузке регионов
            map.removeControl(load);

            // Добавляем полигоны на карту
            data.forEach(region => {
                const iso3166 = region.features[0].properties.iso3166;
                const title = window.REGION_LIST.get(iso3166).title;
                const num_visited = window.REGION_LIST.get(iso3166).num_visited;
                const ratio_visited = window.REGION_LIST.get(iso3166).ratio_visited;
                console.log(ratio_visited);

                let color;
                if (ratio_visited === undefined || ratio_visited === 0) {
                    color = '#bbbbbb'; // серый, чуть темнее
                } else if (ratio_visited > 0 && ratio_visited <= 20) {
                    color = '#b9dca8'; // мягкий светло-зелёный
                } else if (ratio_visited > 20 && ratio_visited <= 40) {
                    color = '#8cc07b'; // травяной зелёный
                } else if (ratio_visited > 40 && ratio_visited <= 60) {
                    color = '#61a35a'; // насыщенный зелёный
                } else if (ratio_visited > 60 && ratio_visited <= 80) {
                    color = '#40843f'; // тёмно-зелёный
                } else {
                    color = '#2b5726'; // глубокий насыщенный зелёный
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
            });
        })
        .catch(error => {
            map.removeControl(load);
            addErrorControl(map);
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

/**
 * Создаёт на карте map панель с информацией о том, что идёт загрузка полигонов.
 */
function addLoadControl(map) {
    const load = L.control();

    load.onAdd = function (map) {
        this._div = L.DomUtil.create('div', 'load');
        this.update();
        return this._div;
    };
    load.update = function (props) {
        this._div.innerHTML = '<div class="d-flex align-items-center justify-content-center gap-2">'
                            + '<div class="spinner-border spinner-border-sm" role="status">'
                            + '<span class="visually-hidden">Загрузка...</span></div><div>Загружаю границы регионов...</div></div>';
    };
    load.addTo(map);

    return load
}

/**
 * Создаёт на карте map панель с информацией о том, что произошла ошибка при загрузке полигонов.
 */
function addErrorControl(map) {
    const error = L.control();

    error.onAdd = function (map) {
        this._div = L.DomUtil.create('div', 'error');
        this.update();
        return this._div;
    };
    error.update = function (props) {
        this._div.innerHTML = '<div>Произошла ошибка при загрузке границ регионов</div>';
    };
    error.addTo(map);

    return error
}

function createLegendControl(map) {
  // Контрол легенды
  const legend = L.control({ position: 'bottomright' });

  legend.onAdd = function () {
    const div = L.DomUtil.create('div', 'legend');
    div.style.display = 'none'; // скрываем по умолчанию
    div.innerHTML = `
      <div class="legend-title">Посещённость городов (%) 
        <button id="toggle-legend-btn" title="Скрыть легенду" style="float:right; cursor:pointer; background:none; border:none; font-weight:bold;">×</button>
      </div>
      <div class="legend-item"><span class="color-box" style="background:#bbbbbb"></span>0% — не посещено</div>
      <div class="legend-item"><span class="color-box" style="background:#b9dca8"></span>1% – 20%</div>
      <div class="legend-item"><span class="color-box" style="background:#8cc07b"></span>21% – 40%</div>
      <div class="legend-item"><span class="color-box" style="background:#61a35a"></span>41% – 60%</div>
      <div class="legend-item"><span class="color-box" style="background:#40843f"></span>61% – 80%</div>
      <div class="legend-item"><span class="color-box" style="background:#2b5726"></span>81% – 100%</div>
    `;
    L.DomEvent.disableClickPropagation(div);
    return div;
  };

  legend.addTo(map);

  // Контрол кнопки показа легенды
  const showBtn = L.control({ position: 'bottomright' });

  showBtn.onAdd = function () {
    const div = L.DomUtil.create('div', 'show-legend-btn');
    div.innerHTML = `<button title="Показать легенду" style="cursor:pointer; padding: 5px 10px;">Показать легенду</button>`;
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