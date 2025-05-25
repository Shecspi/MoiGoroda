import * as L from 'leaflet';

import {SimpleMapScreenshoter} from 'leaflet-simple-map-screenshoter';

import {getCookie} from '../components/get_cookie.js';

const fillColorVisitedCountry = '#32b700';
const fillColorNotVisitedCountry = '#9a9a9a';
const fillOpacity = 0.6;
const strokeColor = '#FFF';
const strokeOpacity = 0.8;
const strokeWidth = 1;

// Карта, на которой будут отрисовываться все объекты стран
let map;

// Словарь, хранящий в себе все добавленные на карте объекты стран
let allGeoJsons = new Map();

/**
 * Словарь, содержащий информацию обо всех странах, которые есть в БД.
 * Формат:
 *      "RU": {
 *          code: "RU",
 *          name: "Россия",
 *          fullname: "Российская Федерация",
 *          location: "Восточная Европа",
 *          part_of_the_world: "Европа",
 *          to_delete: "/api/country/delete/RU",
 *          is_visited: true
 *      } ...
 */
let allCountriesFromDB;

/**
Множество, содержащее информацию обо всех посещённых пользователем странах.
Информация о посещённых странах есть в allCountryState (параметр is_visited),
но удобно, когда все посещённые страны хранятся в одном множестве.
Можно легко узнать количество посещённых стран (allVisitedCountries.size)
или проверить, посещена ли страна (allVisitedCountries.has(countryCode)).
*/
let allVisitedCountries;

// Структура для хранения информации о стране
class Country {
    iso3166_1_alpha2;
    name_ru;
    name_en;
    fullname_ru;
    fullname_en;
    location;
    part_of_the_world;
    to_delete;
    is_visited;
}

// ----------------------------- Действия при загрузке страницы -----------------------------

init();

// ----------------------------- Функции -----------------------------

function init() {
    map = create_map([50, 60], 4)

    // Загружаем всю необходимую информацию
    const allPromises = [];
    if (isAuthenticated === true) {
        allPromises.push(getAllPolygons());
        allPromises.push(getPartsOfTheWorld());
        allPromises.push(getLocations());
        allPromises.push(getAllCountries());
        allPromises.push(getVisitedCountries());
    } else {
        allPromises.push(getAllPolygons());
        allPromises.push(getPartsOfTheWorld());
        allPromises.push(getLocations());
        allPromises.push(getAllCountries());
    }

    // Если пользователь авторизован, то в allPromises будет храниться 5 массивов,
    // а в случае неавторизованного пользователя - только 4 (последнего visitedCountries не будет).
    Promise.all([...allPromises]).then(([
                                            polygons,
                                            partsOfTheWorld,
                                            getLocations,
                                            allCountries,
                                            visitedCountries,
                                        ]) => {
        if (isAuthenticated === true) {
            allVisitedCountries = new Set(visitedCountries.map(country => {
                return country.code
            }));
        }

        allCountriesFromDB = new Map(allCountries.map(country => {
            return [country.code, {
                        code: country.code,
                        name: country.name,
                        fullname: country.fullname,
                        location: country.location,
                        part_of_the_world: country.part_of_the_world,
                        to_delete: country.to_delete,
                        is_visited: isAuthenticated === true ? allVisitedCountries.has(country.code) : false,
                        owner: country.owner
                    }]
        }));

        // Добавляем страны на карту, закрашивая по-разному посещённые и не посещённые.
        // За основу списка стран берутся загруженные полигоны,
        // но вся информация о стране (кроме iso3166_1_alpha2) - из БД сервиса.
        polygons.forEach((polygon) => {
            const iso3166_1_alpha2 = polygon.features[0].properties['ISO3166-1:alpha2'];

            const country_data = allCountriesFromDB.get(iso3166_1_alpha2);
            if (!country_data) {
                console.log('Страны нет в БД: ', iso3166_1_alpha2, polygon.features[0].properties['name:ru']);
                return;
            }

            const country = create_country_object(iso3166_1_alpha2, country_data);
            const geoJSON = addCountryOnMap(polygon, country, map);
            allGeoJsons.set(iso3166_1_alpha2, geoJSON);
        });

        let not_found_polygons = 0;
        allCountriesFromDB.forEach((country) => {
            const code = country.code;
            let found = false;
            polygons.forEach((polygon) => {
                if (polygon.features[0].properties['ISO3166-1:alpha2'] === code) {
                    found = true;
                }
            });
            if (!found) {
                console.log('Нет полигона ', code, country.name_ru);
                not_found_polygons += 1;
            }
        })
        if (not_found_polygons > 0) {
            console.log('Всего нет полигонов: ', not_found_polygons);
        }

        showQtyCountries(allCountriesFromDB.size, isAuthenticated ? allVisitedCountries.size : null);
        enablePartOfTheWorldButton(partsOfTheWorld);
        enableLocationsButton(getLocations);
    });
}

/**
 * Подготавливает объект типа Country со всей необходимой информацией о стране.
 * @param iso3166_1_alpha2 Код страны, для которой подготавливается объект
 * @param country_data {Map} Информация о стране
 * @returns {Country}
 */
function create_country_object(iso3166_1_alpha2, country_data) {
    const country = new Country();

    country.iso3166_1_alpha2 = iso3166_1_alpha2;
    country.name_ru = country_data.name ? country_data.name : "";
    country.name_en = "";  // На данный момент это поле не используется
    country.fullname_ru = country_data.fullname ? country_data.fullname : "";
    country.fullname_en = "";  // На данный момент это поле не используется
    country.location = country_data.location ? country_data.location : "";
    country.part_of_the_world = country_data.part_of_the_world ? country_data.part_of_the_world : "";
    country.to_delete = country_data.to_delete ? country_data.to_delete : "";
    country.is_visited = country_data.is_visited ? country_data.is_visited : false;
    country.owner = country_data.owner;

    return country
}

/**
 * Функция фильтрует страны на карте и оставляет только те, которые соответствуют переданным параметрам.
 * @param filterItem Элемент, по которому производится фильтрация.
 * @param type Тип фильтрации - по части света или по локации.
 */
function filterCountriesOnTheMap(filterItem, type) {
    const all_country_codes_on_map = Array.from(allGeoJsons.keys());

    // Скрываем все страны на карте
    allGeoJsons.forEach(geoObject => {
        map.removeLayer(geoObject);
    });

    all_country_codes_on_map.forEach((country_code) => {
        if (!allCountriesFromDB.has(country_code)) {
            return;
        }

        const country = allCountriesFromDB.get(country_code);

        if (
            (filterItem === '__all__')
            || (type === 'part-of-the-world' && country.part_of_the_world === filterItem)
            || (type === 'locations' && country.location === filterItem)
        ) {
            // Отображаем на карте только те страны, которые соответствуют фильтру
            map.addLayer(allGeoJsons.get(country.code));
        }
    });
}


function add_country(iso3166_1_alpha2) {
    const url = document.getElementById('url_add_visited_countries').dataset.url;
    const formData = new FormData();
    formData.set('code', iso3166_1_alpha2);

    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie("csrftoken")
        },
        body: formData
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error(response.statusText)
            }
            return response.json()
        })
        .then(() => {
            const country = allGeoJsons.get(iso3166_1_alpha2);

            // Меняем цвет заливки полигона на тот, который используется для посещённых стран
            country.eachLayer(layer => {
                layer.setStyle(
                    {
                        'fillColor': fillColorVisitedCountry
                    }
                );
            });

            allGeoJsons.delete(iso3166_1_alpha2);
            allGeoJsons.set(iso3166_1_alpha2, country);
            allCountriesFromDB.get(iso3166_1_alpha2).is_visited = true;
            allVisitedCountries.add(iso3166_1_alpha2);

            // Обновляем Popup, для этого удаляем старый и создаём новый
            country.getPopup().remove();
            const country_data = allCountriesFromDB.get(iso3166_1_alpha2);
            const country_obj = create_country_object(iso3166_1_alpha2, country_data);
            country.bindPopup(generatePopupContent(country_obj));

            updateQtyVisitedCountries();

            showSuccessToast(
                'Успешно',
                `Страна <strong>${allCountriesFromDB.get(iso3166_1_alpha2).name}</strong> успешно добавлена как посещённая Вами`
            );
        });
}

function delete_country(iso3166_1_alpha2) {
    const url = allCountriesFromDB.get(iso3166_1_alpha2).to_delete;
    const formData = new FormData();
    formData.set('from', 'country map');

    fetch(url, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': getCookie("csrftoken")
        },
        body: formData
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error(response.statusText)
            }
            return response.text();
        })
        .then(() => {
            const country = allGeoJsons.get(iso3166_1_alpha2);

            // Меняем цвет заливки полигона на тот, который используется для непосещённых стран
            country.eachLayer(layer => {
                layer.setStyle(
                    {
                        'fillColor': fillColorNotVisitedCountry
                    }
                );
            });

            allGeoJsons.delete(iso3166_1_alpha2);
            allGeoJsons.set(iso3166_1_alpha2, country);
            allCountriesFromDB.get(iso3166_1_alpha2).is_visited = false;
            allVisitedCountries.delete(iso3166_1_alpha2);

            // Обновляем Popup, для этого удаляем старый и создаём новый
            country.getPopup().remove();
            const country_data = allCountriesFromDB.get(iso3166_1_alpha2);
            const country_obj = create_country_object(iso3166_1_alpha2, country_data);
            country.bindPopup(generatePopupContent(country_obj))

            updateQtyVisitedCountries();

            showSuccessToast(
                'Успешно',
                `Страна <strong>${allCountriesFromDB.get(iso3166_1_alpha2).name}</strong> успешно удалена из списка посещённых Вами`);
        });
}

/**
 * Производит добавление geoJSON, переданного в параметре 'polygon', на карту 'map'.
 * Также для добавленного geoJSON создаёт Tooltip и Popup, информация для которых берётся из 'country'.
 * @param polygon {json}
 * @param country {Country}
 * @param map {Map}
 * @returns {geoJSON}
 */
function addCountryOnMap(polygon, country, map) {
    const myStyle = {
        "fillColor": country.is_visited ? fillColorVisitedCountry : fillColorNotVisitedCountry,
        "fillOpacity": fillOpacity,
        "weight": strokeWidth,
        "color": strokeColor,
        "opacity": strokeOpacity
    };

    const geoJSON = L.geoJSON(polygon, {
        style: myStyle
    }).addTo(map);

    const name = country.owner ? country.name_ru + ` (${country.owner})` : country.name_ru;
    geoJSON.bindPopup(generatePopupContent(country));
    geoJSON.bindTooltip(name, {
        direction: 'top',
        sticky: true
    });
    geoJSON.on('mouseover', function () {
        const tooltip = this.getTooltip();
        if (this.isPopupOpen()) {
            tooltip.setOpacity(0.0);
        } else {
            tooltip.setOpacity(0.9);
        }
    });
    geoJSON.on('click', function () {
        this.getTooltip().setOpacity(0.0);
    });

    return geoJSON;
}


/**
 * Подготавливает HTML-содержимое для popup-окна с информацией о стране
 * @param country {Country} Объект, содержащий в себе всю необходимую информацию о стране.
 * @returns {string}
 */
function generatePopupContent(country) {
    let content = "";

    if (country.fullname_ru) {
        content += `<div><span class="fw-semibold">Полное название:</span> ${country.fullname_ru}</div>`;
    }

    content +=
        `<div><span class="fw-semibold">Часть света:</span> ${country.part_of_the_world}</div>` +
        `<div><span class="fw-semibold">Расположение:</span> ${country.location}</div>`;

    if (isAuthenticated === true) {
        const linkToAdd = `<hr><a href="#" onclick="add_country('${country.iso3166_1_alpha2}');">Отметить страну как посещённую</a>`
        const linkToDelete = `<hr><a href="#" onclick="delete_country('${country.iso3166_1_alpha2}')">Удалить страну</a>`
        const link = country.is_visited ? linkToDelete : linkToAdd;
        const name = country.owner ? country.name_ru + ` (${country.owner})` : country.name_ru;

        return `<h4>${name}</h4><country.name_rubr>${content + link}`;
    } else {
        return `<h4>${country.name_ru}</h4><br>${content}`;
    }
}

// ------------------------------------------------ //
//                                                  //
// Функции, отвечающие за загрузку данных с сервера //
//                                                  //
// ------------------------------------------------ //
function getDataFromServer(url) {
    return fetch(url + '?' + new URLSearchParams({'from': 'country map'}))
        .then((response) => {
            if (!response.ok) {
                throw new Error(response.statusText)
            }
            return response.json();
        })
        .then((data) => {
            return data;
        });
}

function getAllPolygons() {
    const url = `${document.getElementById('url_get_polygons').dataset.url}/country/all`;
    return getDataFromServer(url);
}

function getAllCountries() {
    const url = document.getElementById('url_get_all_countries').dataset.url;
    return getDataFromServer(url);
}

function getVisitedCountries() {
    const url = document.getElementById('url_get_visited_countries').dataset.url;
    return getDataFromServer(url);
}

function getPartsOfTheWorld() {
    const url = document.getElementById('url_get_parts_of_the_world').dataset.url;
    return getDataFromServer(url);
}

function getLocations() {
    const url = document.getElementById('url_get_locations').dataset.url;
    return getDataFromServer(url);
}

// --------------------------------------- //
//                                         //
// Функции, отображающие карту на странице //
//                                         //
// --------------------------------------- //
function create_map(center, zoom) {
    const map = L.map('map', {
        attributionControl: false,
        zoomControl: false
    }).setView(center, zoom);

    add_attribution(map);
    add_zoom_control(map);
    add_fullscreen_control(map);
    new SimpleMapScreenshoter().addTo(map);

    return map
}


/**
 * Добавляет кнопку полноэкранного просмотра.
 * @param map Объект карты, на которую нужно добавить кнопки.
 */
function add_fullscreen_control(map) {
    map.addControl(new L.Control.Fullscreen({
        title: {
            'false': 'Полноэкранный режим',
            'true': 'Выйти из полноэкранного режима'
        }
    }));
}


/**
 * Добавляет кнопки приближения и отдаления карты.
 * @param map Объект карты, на которую нужно добавить кнопки.
 */
function add_zoom_control(map) {
    const zoomControl = L.control.zoom({
        zoomInTitle: 'Нажмите, чтобы приблизить карту',
        zoomOutTitle: 'Нажмите, чтобы отдалить карту'
    });
    zoomControl.addTo(map);
}

/**
 * Добавляет в правый нижний угол указание об использовании карт OopenStreetMap и их лицензии.
 * @param map Объект карты, на который нужно добавить информацию.
 */
function add_attribution(map) {
    const myAttrControl = L.control.attribution().addTo(map);
    myAttrControl.setPrefix('');
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: 'Используются карты &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> под лицензией <a href="https://opendatacommons.org/licenses/odbl/">ODbL.</a>'
    }).addTo(map);
}

// -------------------------------------------------- //
//                                                    //
// Функции, взаимодействующие с элементами интерфейса //
//                                                    //
// -------------------------------------------------- //
function enablePartOfTheWorldButton(array) {
    const button = document.getElementById('btn-show-part-of-the-world');
    const menu = document.getElementById('dropdown-menu-parts-of-the-world');
    enableDropdownButton(array, button, menu, 'fa-solid fa-earth-americas', 'part-of-the-world');
}

function enableLocationsButton(array) {
    const button = document.getElementById('btn-show-locations');
    const menu = document.getElementById('dropdown-menu-locations');
    enableDropdownButton(array, button, menu, 'fa-solid fa-location-dot', 'locations');
}

function enableDropdownButton(array, button, menu, icon, type) {
    // Убираем спиннер с кнопки и делаем её активной
    button.disabled = false;
    button.innerHTML = `<i class="${icon}"></i>&nbsp;&nbsp;`;

    // Очищаем меню
    menu.innerHTML = '';

    // Добавляем заголовок в меню
    const header = document.createElement('h6');
    header.classList.add('dropdown-header');
    header.innerHTML = 'Выберите, какие страны отобразить на карте:';
    menu.appendChild(document.createElement('li').appendChild(header));

    // Добавляем элементы в меню
    array.forEach(item => {
        const a = document.createElement('a');
        a.classList.add('dropdown-item');
        a.innerHTML = item.name;
        a.style.cursor = 'pointer';
        a.addEventListener('click', () => {
            filterCountriesOnTheMap(item.name, type);
        });
        menu.appendChild(document.createElement('li').appendChild(a));
    });

    // Добавляем пункт "Все страны"
    const divider = document.createElement('hr');
    divider.classList.add('dropdown-divider')
    menu.appendChild(document.createElement('li').appendChild(divider));

    const all_countries = document.createElement('a');
    all_countries.classList.add('dropdown-item');
    all_countries.innerHTML = 'Показать все страны';
    all_countries.style.cursor = 'pointer';
    menu.appendChild(document.createElement('li').appendChild(all_countries));
    all_countries.addEventListener('click', () => {
        filterCountriesOnTheMap('__all__', type);
    });
}

/**
 * Функция отображает количество посещенных стран в блоке с id 'block-qty_countries'.
 * В зависимости от того, авторизован пользователь или нет, функция вызывает соответствующую функцию.
 * @param qtyAllCountries - общее количество всех стран в сервисе
 * @param qtyVisitedCountries - количество посещённых стран
 */
function showQtyCountries(qtyAllCountries, qtyVisitedCountries) {
    const block_qty_visited_countries = document.getElementById('block-qty_countries');
    block_qty_visited_countries.classList.remove('placeholder');
    block_qty_visited_countries.classList.remove('bg-secondary');
    block_qty_visited_countries.classList.remove('placeholder-lg');

    const block_statistic = document.getElementById('block-statistic');
    block_statistic.classList.remove('placeholder-glow');

    if (isAuthenticated === true) {
        showQtyVisitedForAuthUsers(block_qty_visited_countries, qtyVisitedCountries, qtyAllCountries);
    } else {
        showQtyAllCountriesForGuest(block_qty_visited_countries, qtyAllCountries);
    }
}

/**
 * Функция отображает количество посещенных стран в блоке с id 'block-qty_visited_countries' для авторизованных пользователей.
 * @param element - DOM-элемент, в котором будет отображаться количество посещённых стран
 * @param qtyVisitedCities - количество посещённых стран
 * @param qtyAllCities - общее количество всех стран в сервисе
 */
function showQtyVisitedForAuthUsers(element, qtyVisitedCities, qtyAllCities) {
    element.innerHTML = `${declensionVisited(qtyVisitedCities)} <span class="fs-4 fw-medium">${qtyVisitedCities}</span> ${declensionCountry(qtyVisitedCities)} из ${qtyAllCities}`;
}

/**
 * Функция отображает количество всех стран в блоке с id 'block-qty_visited_countries' для неавторизованных пользователей.
 * @param element - DOM-элемент, в котором будет отображаться количество посещённых стран
 * @param {number} qtyAllCountries - количество всех стран
 */
function showQtyAllCountriesForGuest(element, qtyAllCountries) {
    element.innerHTML = `Всего <span class="fs-4 fw-medium">${qtyAllCountries}</span> ${declensionCountry(qtyAllCountries)}`;
}

/**
 * Функция обновляет количество посещенных стран в тулбаре.
 */
function updateQtyVisitedCountries() {
    const block_qty_countries = document.getElementById('block-qty_countries');
    const qtyVisitedCities = allVisitedCountries.size;
    const qtyAllCities = allCountriesFromDB.size;
    block_qty_countries.innerHTML = `${declensionVisited(qtyVisitedCities)} <span class="fs-4 fw-medium">${qtyVisitedCities}</span> ${declensionCountry(qtyVisitedCities)} из ${qtyAllCities}`;
}

// ------------------------------------------------ //
//                                                  //
// Функции, склоняющие слова на основе числительных //
//                                                  //
// ------------------------------------------------ //
function declensionCountry(qtyOfCountries) {
    /**
     * Возвращает слово "страна", корректно склонённое для использования с числом qtyOfCountries.
     */
    if (qtyOfCountries % 10 === 1 && qtyOfCountries !== 11) {
        return 'страна';
    } else if ([2, 3, 4].includes(qtyOfCountries % 10) && ![12, 13, 14].includes(qtyOfCountries)) {
        return 'страны';
    } else {
        return 'стран';
    }
}

function declensionVisited(qtyOfCountries) {
    /**
     * Возвращает слово "посещено", корректно склонённое для использования с числом qtyOfCountries.
     */
    if (qtyOfCountries % 10 === 1 && qtyOfCountries !== 11) {
        return 'Посещена';
    } else {
        return 'Посещено';
    }
}