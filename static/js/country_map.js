import {create_map} from './map.js';
import {addCountryOnMap} from "./country/map_helpers.js";
import {
    getAllCountries,
    getAllPolygons,
    getLocations,
    getPartsOfTheWorld,
    getVisitedCountries
} from "./country/fetch.js";


const fillColorVisitedCountry = '#32b700';
const fillColorNotVisitedCountry = '#9a9a9a';
const fillOpacity = 0.6;
const strokeColor = '#FFF';
const strokeOpacity = 0.8;
const strokeWidth = 1;

// Карта, на которой будут отрисовываться все объекты стран
let map;

// Словарь, хранящий в себе все добавленные на карте объекты стран
let allCountriesGeoObjects = new Map();

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
let allCountryState;

// Множество, содержащее информацию обо всех частях света, которые есть в БД
let allPartsOfTheWorld;

// Множество, содержащее информацию обо всех локациях, которые есть в БД.
let allLocations;


// Множество, содержащее информацию обо всех посещённых пользователем странах.
let visitedCountryState;

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
        // Множество с посещёнными странами пользователя
        // Эта же информация есть в allCountryState (параметр is_visited), но там информация обновляется
        // только в момент первоначальной загрузки. Если пользователь добавил новую страну, то нужно перерисовать полигоны.
        // Поэтому здесь мы создаём ещё одно множество, которое будет хранить актуальную информацию о посещённых странах.
        if (isAuthenticated === true) {
            visitedCountryState = new Set(visitedCountries.map(country => {
                return country.code
            }));
        }

        allCountryState = new Map(allCountries.map(country => {
            return [country.code, {
                code: country.code,
                name: country.name,
                fullname: country.fullname,
                location: country.location,
                part_of_the_world: country.part_of_the_world,
                to_delete: country.to_delete,
                is_visited: isAuthenticated === true ? visitedCountryState.has(country.code) : false
            }]
        }));

        // Добавляем страны на карту, закрашивая по разному посещённые и не посещённые
        polygons.forEach((polygon) => {
            // iso3166_1_alpha2 берём из geojson файла, всю остальную информацию - из БД сервиса
            const iso3166_1_alpha2 = polygon.features[0].properties['ISO3166-1:alpha2'];

            const country_data = allCountryState.get(iso3166_1_alpha2);
            if (!country_data) {
                console.log('Такой страны нет в БД: ', iso3166_1_alpha2);
                return;
            }

            const country = create_country_object(iso3166_1_alpha2, country_data);
            const geoJSON = addCountryOnMap(polygon, country, map);
            allCountriesGeoObjects.set(iso3166_1_alpha2, geoJSON);
        });

        showQtyCountries(allCountryState.size, isAuthenticated ? visitedCountryState.size : null);
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
    country.name_en = "";
    country.fullname_ru = country_data.fullname ? country_data.fullname : "";
    country.fullname_en = "";
    country.location = country_data.location ? country_data.location : "";
    country.part_of_the_world = country_data.part_of_the_world ? country_data.part_of_the_world : "";
    country.to_delete = country_data.to_delete ? country_data.to_delete : "";
    country.is_visited = country_data.is_visited ? country_data.is_visited : false;

    return country
}

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
    menu.appendChild(document.createElement('li').appendChild(all_countries));
    all_countries.addEventListener('click', () => {
        filterCountriesOnTheMap('__all__', type);
    });
}

/**
 * Функция фильтрует страны на карте и оставляет только те, которые соответствуют переданным параметрам.
 * @param filterItem Элемент, по которому производится фильтрация.
 * @param type Тип фильтрации - по части света или по локации.
 */
function filterCountriesOnTheMap(filterItem, type) {
    const all_country_codes_on_map = Array.from(allCountriesGeoObjects.keys());

    const filtered_countries = new Map();

    all_country_codes_on_map.forEach((country_code) => {
        if (!allCountryState.has(country_code)) {
            return;
        }

        const country = allCountryState.get(country_code);

        if (
            (type === 'part-of-the-world' && country.part_of_the_world === filterItem)
         || (type === 'locations' && country.location === filterItem)
         || (type === '__all__')
        ) {
            filtered_countries.set(country_code, country);
        }
    });

    // Скрываем все страны на карте
    allCountriesGeoObjects.forEach(geoObject => {
        map.removeLayer(geoObject);
    });

    // Показываем только те страны, которые соответствуют фильтру
    filtered_countries.forEach(country => {
        map.addLayer(allCountriesGeoObjects.get(country.code));
    });
}


function add_country(iso3166_1_alpha2) {
    const url = document.getElementById('url_add_visited_countries').dataset.url;
    const formData = new FormData();
    formData.set('code', iso3166_1_alpha2);

    let response = fetch(url, {
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
            const country = allCountriesGeoObjects.get(iso3166_1_alpha2);

            // Меняем цвет заливки полигона на тот, который используется для посещённых стран
            country.eachLayer(layer => {
                layer.setStyle(
                    {
                        'fillColor': fillColorVisitedCountry
                    }
                );
            });

            // Обновляем Popup, для этого удаляем старый и создаём новый
            country.getPopup().remove();
            country.bindPopup(
                generatePopupContent(
                    countryCode,
                    allCountryState.get(countryCode).name,
                    allCountryState.get(countryCode).part_of_the_world,
                    allCountryState.get(countryCode).location,
                    true
                )
            )

            allCountriesGeoObjects.delete(countryCode);
            allCountriesGeoObjects.set(countryCode, country);
            allCountryState.get(countryCode).is_visited = true;
            visitedCountryState.add(countryCode);
            updateQtyVisitedCountries();

            showSuccessToast(
                'Успешно',
                `Страна <strong>${allCountryState.get(countryCode).name}</strong> успешно добавлена как посещённая Вами`
            );
        });
}

function delete_country(countryCode) {
    const url = allCountryState.get(countryCode).to_delete;
    const countryName = allCountryState.get(countryCode).name;
    const formData = new FormData();
    formData.set('from', 'country map');

    let response = fetch(url, {
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

            const country = allCountriesGeoObjects.get(countryCode);

            allCountriesGeoObjects.delete(countryCode);
            visitedCountryState.delete(countryCode);
            myMap.geoObjects.remove(country);

            allCountryState.get(countryCode).is_visited = false;
            let geoObject = addCountryOnMap(country, allCountryState.get(countryCode));
            allCountriesGeoObjects.set(countryCode, geoObject);

            updateQtyVisitedCountries();

            showSuccessToast('Успешно', `Страна <strong>${country.properties._data.name}</strong> успешно удалена из списка посещённых Вами`);
        });
}

/**
 * Функция отображает количество посещенных стран в блоке с id 'block-qty_visited_countries'.
 * В зависимости от того, авторизован опльзователь или нет, функция вызывает соответствующую функцию.
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
    const qtyVisitedCities = visitedCountryState.size;
    const qtyAllCities = allCountryState.size;
    block_qty_countries.innerHTML = `${declensionVisited(qtyVisitedCities)} <span class="fs-4 fw-medium">${qtyVisitedCities}</span> ${declensionCountry(qtyVisitedCities)} из ${qtyAllCities}`;
}

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
