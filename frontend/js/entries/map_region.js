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
// Хранилище полигонов регионов для фильтрации по годам
const regionPolygons = new Map();

document.addEventListener('DOMContentLoaded', async (event) => {
    await initCountrySelect({showAllOption: false});
    initYearFilter();
});

function init() {
    map = create_map();
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

                    // Сохраняем ссылку на полигон для фильтрации по годам
                    regionPolygons.set(iso3166, geojson);

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

/**
 * Инициализирует выпадающий список с годами для фильтрации регионов.
 */
function initYearFilter() {
    if (!window.IS_AUTHENTICATED || !window.ALL_VISIT_YEARS || window.ALL_VISIT_YEARS.length === 0) {
        return;
    }

    const yearFilterContainer = document.getElementById('year-filter-container');
    const yearSelect = document.getElementById('id_year_filter');

    if (!yearFilterContainer || !yearSelect) {
        return;
    }

    // Показываем контейнер фильтра по годам
    yearFilterContainer.style.display = 'block';

    // Сначала уничтожаем существующий экземпляр Preline UI, если он есть
    // Это важно, чтобы Preline UI не инициализировался автоматически до добавления опций
    let existingInstance = window.HSSelect && window.HSSelect.getInstance ? window.HSSelect.getInstance('#id_year_filter') : null;
    if (existingInstance && typeof existingInstance.destroy === 'function') {
        existingInstance.destroy();
    }

    // Удаляем старую разметку Preline UI, если она есть
    const oldSelectContainer = yearSelect.closest('.hs-select');
    if (oldSelectContainer && oldSelectContainer !== yearSelect.parentElement) {
        const parent = oldSelectContainer.parentElement;
        parent.insertBefore(yearSelect, oldSelectContainer);
        oldSelectContainer.remove();
    }

    // Убеждаемся, что select элемент видимый (не hidden)
    if (yearSelect.classList.contains('hidden')) {
        yearSelect.classList.remove('hidden');
    }

    // Сохраняем опцию "Все годы" из шаблона, если она есть
    // Проверяем как старое значение (пустая строка), так и новое ("all")
    const existingAllYearsOption = yearSelect.querySelector('option[value="all"]') || yearSelect.querySelector('option[value=""]');
    const allYearsText = existingAllYearsOption ? existingAllYearsOption.textContent.trim() : 'Все годы';
    
    // Очищаем select полностью
    yearSelect.innerHTML = '';

    // Добавляем опцию "Все годы" первой
    // Используем специальное значение "all" вместо пустой строки,
    // так как Preline UI может игнорировать опции с пустым значением
    const allYearsOption = document.createElement('option');
    allYearsOption.value = 'all';
    allYearsOption.textContent = allYearsText;
    yearSelect.appendChild(allYearsOption);

    // Заполняем выпадающий список годами (после опции "Все годы")
    window.ALL_VISIT_YEARS.forEach(year => {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        yearSelect.appendChild(option);
    });
    
    // Финальная проверка: опция "Все годы" должна быть первой
    const firstOption = yearSelect.firstElementChild;
    if (!firstOption || firstOption.value !== 'all') {
        const allYearsOpt = yearSelect.querySelector('option[value="all"]');
        if (allYearsOpt && allYearsOpt !== firstOption) {
            yearSelect.insertBefore(allYearsOpt, firstOption);
        }
    }
    
    // Проверяем, что опции добавлены
    const optionsAfterAdd = yearSelect.options.length;
    const allYearsAfterAdd = yearSelect.querySelector('option[value="all"]');
    
    if (!allYearsAfterAdd || optionsAfterAdd < 1) {
        console.error('Ошибка: опции не добавлены в select', {
            hasAllYears: !!allYearsAfterAdd,
            optionsCount: optionsAfterAdd,
            firstOptionValue: yearSelect.firstElementChild?.value,
            firstOptionText: yearSelect.firstElementChild?.textContent
        });
        return;
    }

    // Инициализируем Preline UI компонент после небольшой задержки
    // чтобы убедиться, что DOM обновлен и Preline UI загружен
    const initPrelineSelect = () => {
        // Финальная проверка: опции должны быть в DOM
        const finalOptionsCount = yearSelect.options.length;
        const finalAllYearsOption = yearSelect.querySelector('option[value="all"]');
        const firstOption = yearSelect.firstElementChild;
        
        // Проверяем, что опция "Все годы" есть и она первая
        if (!finalAllYearsOption) {
            console.error('Опция "Все годы" не найдена перед инициализацией Preline UI');
            // Добавляем опцию "Все годы" если её нет
            const allYearsOpt = document.createElement('option');
            allYearsOpt.value = 'all';
            allYearsOpt.textContent = 'Все годы';
            yearSelect.insertBefore(allYearsOpt, yearSelect.firstChild);
        } else if (firstOption && firstOption.value !== 'all') {
            // Если опция "Все годы" не первая, перемещаем её
            yearSelect.insertBefore(finalAllYearsOption, firstOption);
        }
        
        if (finalOptionsCount < 1) {
            console.error('Нет опций в select перед инициализацией Preline UI');
            return;
        }
        
        // Проверяем, что опция "Все годы" действительно первая
        const finalFirstOption = yearSelect.firstElementChild;
        if (!finalFirstOption || finalFirstOption.value !== 'all') {
            console.error('Опция "Все годы" не является первой опцией', {
                firstOptionValue: finalFirstOption?.value,
                firstOptionText: finalFirstOption?.textContent,
                allOptions: Array.from(yearSelect.options).map(opt => ({ value: opt.value, text: opt.textContent }))
            });
            return;
        }

        // Проверяем, инициализирован ли компонент уже (на случай, если autoInit сработал)
        let hsSelectInstance = window.HSSelect && window.HSSelect.getInstance ? window.HSSelect.getInstance('#id_year_filter') : null;

        // Если компонент уже был инициализирован, уничтожаем его
        if (hsSelectInstance && typeof hsSelectInstance.destroy === 'function') {
            hsSelectInstance.destroy();
            hsSelectInstance = null;
        }

        // Удаляем старую разметку Preline UI, если она есть
        const oldSelectContainer = yearSelect.closest('.hs-select');
        if (oldSelectContainer && oldSelectContainer !== yearSelect.parentElement) {
            // Восстанавливаем оригинальный select на место
            const parent = oldSelectContainer.parentElement;
            parent.insertBefore(yearSelect, oldSelectContainer);
            oldSelectContainer.remove();
        }
        
        // Убеждаемся, что select элемент видимый для Preline UI (не hidden)
        if (yearSelect.classList.contains('hidden')) {
            yearSelect.classList.remove('hidden');
        }
        
        if (window.HSSelect) {
            try {
                // Создаем новый экземпляр Preline Select, передавая элемент напрямую
                hsSelectInstance = new window.HSSelect(yearSelect);
            } catch (e) {
                // Если не получилось создать через конструктор с элементом, пробуем через селектор
                try {
                    hsSelectInstance = new window.HSSelect('#id_year_filter');
                } catch (e2) {
                    // Если не получилось создать через конструктор, используем autoInit
                    if (window.HSStaticMethods && typeof window.HSStaticMethods.autoInit === 'function') {
                        window.HSStaticMethods.autoInit();
                        hsSelectInstance = window.HSSelect.getInstance('#id_year_filter');
                    }
                }
            }
        }

        // Обработчик изменений значения
        const handleChange = () => {
            // Получаем значение из select элемента
            const selectedValue = yearSelect.value || '';
            // Если выбрано "all", передаем пустую строку для сброса фильтра
            const filterValue = selectedValue === 'all' ? '' : selectedValue;
            filterRegionsByYear(filterValue);
        };

        if (hsSelectInstance) {
            // Используем Preline UI API для обработки изменений
            // Слушаем клики на опциях в выпадающем списке
            const selectContainer = yearSelect.closest('.hs-select');
            if (selectContainer) {
                selectContainer.addEventListener('click', (e) => {
                    const option = e.target.closest('.hs-select-option, [class*="hs-select-option"]');
                    if (option) {
                        // Получаем значение опции из data-value атрибута или из соответствующей option
                        const optionValue = option.getAttribute('data-value') || option.dataset.value || '';
                        
                        // Находим соответствующую option в select элементе
                        const selectOption = Array.from(yearSelect.options).find(opt => {
                            return opt.value === optionValue || 
                                   (optionValue === 'all' && opt.value === 'all') ||
                                   opt.textContent.trim() === option.textContent.trim();
                        });
                        
                        // Небольшая задержка, чтобы Preline UI успел обновить значение
                        setTimeout(() => {
                            if (selectOption) {
                                // Устанавливаем значение в select элементе
                                yearSelect.value = selectOption.value;
                            }
                            handleChange();
                        }, 50);
                    }
                });
            }
        }

        // Также слушаем изменения напрямую на select элементе (fallback)
        yearSelect.addEventListener('change', handleChange);
    };

    // Ждем загрузки Preline UI и обновления DOM
    const waitAndInit = () => {
        requestAnimationFrame(() => {
            if (window.HSSelect) {
                initPrelineSelect();
            } else {
                // Если Preline UI еще не загружен, ждем его загрузки
                const checkPreline = setInterval(() => {
                    if (window.HSSelect) {
                        clearInterval(checkPreline);
                        requestAnimationFrame(() => {
                            initPrelineSelect();
                        });
                    }
                }, 50);
                
                // Таймаут на случай, если Preline UI не загрузится
                setTimeout(() => {
                    clearInterval(checkPreline);
                    if (window.HSSelect) {
                        requestAnimationFrame(() => {
                            initPrelineSelect();
                        });
                    }
                }, 2000);
            }
        });
    };
    
    waitAndInit();
}

/**
 * Фильтрует регионы на карте по выбранному году.
 * @param {string} selectedYear - Выбранный год (пустая строка для показа всех регионов)
 */
function filterRegionsByYear(selectedYear) {
    if (!window.REGION_LIST || regionPolygons.size === 0) {
        return;
    }

    const visiblePolygons = [];

    regionPolygons.forEach((polygon, iso3166) => {
        const regionData = window.REGION_LIST.get(iso3166);
        
        if (!regionData) {
            return;
        }

        // Если год не выбран или выбрано "Все годы" (значение "all"), показываем все регионы
        if (!selectedYear || selectedYear === 'all') {
            if (!map.hasLayer(polygon)) {
                polygon.addTo(map);
            }
            visiblePolygons.push(polygon);
        } else {
            // Проверяем, содержит ли регион выбранный год в visit_years
            const year = parseInt(selectedYear, 10);
            const visitYears = regionData.visit_years || [];
            
            if (visitYears.includes(year)) {
                // Показываем регион
                if (!map.hasLayer(polygon)) {
                    polygon.addTo(map);
                }
                visiblePolygons.push(polygon);
            } else {
                // Скрываем регион
                if (map.hasLayer(polygon)) {
                    map.removeLayer(polygon);
                }
            }
        }
    });

    // Перецентрируем карту по видимым регионам
    if (visiblePolygons.length > 0) {
        const group = new L.featureGroup(visiblePolygons);
        map.fitBounds(group.getBounds());
    }
}


init();