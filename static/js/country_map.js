const fillColorVisitedCountry = '#32b700';
const fillColorNotVisitedCountry = '#9a9a9a';
const fillOpacity = 0.6;
const strokeColor = '#FFF';
const strokeOpacity = 0.8;
const strokeWidth = 1;

// Карта, на которой будут отрисовываться все объекты стран
let myMap;

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

// ----------------------------- Действия при загрузке страницы -----------------------------

checkCalloutNewRegions();
init();

// ----------------------------- Функции -----------------------------

/**
 * Функция проверяет, отображается ли блок Callout с информацией о новых регионах.
 * Если пользователь уже читал эту информацию, то он блок удаляется из DOM-дерева.
 * Иначе он показывается на странице.
 */
function checkCalloutNewRegions() {
    const callout = document.getElementById('callout-new-regions');
    if (JSON.parse(localStorage.getItem('callout-new-regions')) === true) {
        callout.remove();
    } else {
        callout.hidden = false;
    }
}

/**
 * Функция удаляет блок Callout с информацией о новых регионах из DOM-дерева.
 */
function closeCalloutNewRegions() {
    const callout = document.getElementById('callout-new-regions');
    callout.remove();
    localStorage.setItem('callout-new-regions', JSON.stringify(true));
}

function init() {
    map = L.map('map', {
        attributionControl: false,
        zoomControl: false
    }).setView([60, 50], 4);

    // Этот код нужен для того, чтобы убрать ненужный флаг с копирайта.
    const myAttrControl = L.control.attribution().addTo(map);
    myAttrControl.setPrefix('<a href="https://leafletjs.com/">Leaflet</a>');
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
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

    // Если пользователь авторизован, то в allPromises будет храниться 5 массива,
    // а в случае неавторизованного пользователя - только 4.
    Promise.all([...allPromises]).then(([
        allPolygons,
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
        console.log(allCountryState);

        // Добавляем страны на карту, закрашивая по разному посещённые и не посещённые
        allPolygons.forEach((country) => {
            // iso3166_1_alpha2 берём из geojson файла, всю остальную информацию - из БД сервиса
            const iso3166_1_alpha2 = country.features[0].properties['ISO3166-1:alpha2'];
            const country_data = allCountryState.get(iso3166_1_alpha2);

            // Немного криво сейчас это реализовано, что какая-то информация берется из geojson,
            // а какая-то из БД. Нужно будет определиться с единым местом хранения информации о странах.
            if (!country_data) {
                console.log('Такой страны нет в БД: ', iso3166_1_alpha2);
                return;
            }

            const fullname_ru = country_data ? country_data.fullname : undefined;
            const name_ru = country_data ? country_data.name : undefined;
            const is_visited = country_data ? country_data.is_visited : undefined;
            const link_to_delete = country_data ? country_data.to_delete : undefined;
            const location = country_data ? country_data.location : undefined;
            const part_of_the_world = country_data ? country_data.part_of_the_world : undefined;

            const geoObject = addCountryOnMap(country, fullname_ru, part_of_the_world, location)
            allCountriesGeoObjects.set(iso3166_1_alpha2, geoObject);
        });

        showQtyCountries(allCountryState.size, isAuthenticated ? visitedCountryState.size : null);
        enablePartOfTheWorldButton(partsOfTheWorld);
        enableLocationsButton(getLocations);
    });
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
 * @param type Тип филльтрации - по части света или по локации.
 */
function filterCountriesOnTheMap(filterItem, type) {
    const allCountries = Array.from(allCountryState.values());

    // Фильтруем страны и оставляем в массиве filteredCountries только те, которые соответствуют фильтру
    const filteredCountries = allCountries.filter(country => {
        if (type === 'part-of-the-world') {
            return country.part_of_the_world === filterItem;
        } else if (type === 'locations') {
            return country.location === filterItem;
        }
    });

    if (filterItem === '__all__') {
        // Если фильтр - все страны, то показываем все страны на карте
        allCountriesGeoObjects.forEach(geoObject => {
            geoObject.options.set('visible', true);
        });
        return;
    }

    // Скрываем все страны на карте
    allCountriesGeoObjects.forEach(geoObject => {
        geoObject.options.set('visible', false);
    });

    // Показываем только те страны, которые соответствуют фильтру
    filteredCountries.forEach(country => {
        allCountriesGeoObjects.get(country.code).options.set('visible', true);
    });
}

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
    const url = 'http://127.0.0.1:8080/country/all';
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

function compareCountriesWithYandexAndLocalBD(yandexCountries, localCountries) {
    /**
     * Сравнивает словари стран из БД сервиса и стран, которые предоставляет Яндекс.
     * Если находятся расхождения, то они отправляются на специальный эндпоинт.
     */
    const url = document.getElementById('url_revieve_unknown_countries').dataset.url;
    let unknownCountriesFromYandex = new Map();
    let localCountriesCopy = new Map(localCountries);
    yandexCountries.forEach(function (name, code) {
        if (!localCountries.has(code)) {
            unknownCountriesFromYandex.set(code, name);
        } else {
            localCountriesCopy.delete(code);
        }
    });

    if (unknownCountriesFromYandex.size > 0 || localCountriesCopy.size > 0) {
        const data = new FormData();
        data.set('unknown_from_yandex', JSON.stringify(Object.fromEntries(unknownCountriesFromYandex)));
        data.set('unknown_to_yandex', JSON.stringify(Object.fromEntries(localCountriesCopy)));

        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie("csrftoken")
            },
            body: data
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(response.statusText)
                }
                return response
            });
    }
}

function addCountryOnMap(geoJson, part_of_the_world, location, fullname_ru) {
    const iso3166_1_alpha2 = geoJson.features[0].properties['ISO3166-1:alpha2'];
    const name_en = geoJson.features[0].properties['name:en'];
    const name_ru = geoJson.features[0].properties['name:ru'];
    const is_visited = visitedCountryState.has(iso3166_1_alpha2);

    const myStyle = {
        "fillColor": is_visited ? fillColorVisitedCountry : fillColorNotVisitedCountry,
        "fillOpacity": fillOpacity,
        "weight": strokeWidth,
        "color": strokeColor,
        "opacity": strokeOpacity
    };

    const geoObject = L.geoJSON(geoJson, {
        style: myStyle
    }).addTo(map);

    geoObject.bindTooltip(name_ru, {
        direction: 'top',
        sticky: true
    });
    geoObject.bindPopup(
        generatePopupContent(
            iso3166_1_alpha2,
            name_ru,
            fullname_ru,
            part_of_the_world,
            location
        )
    );

    return geoObject;
}

function generatePopupContent(iso3166, name_ru, fullname_ru, partOfTheWorld, location, is_visited) {
    let content = "";

    if (fullname_ru) {
        content += `<div><span class="fw-semibold">Полное название:</span> ${fullname_ru}</div>`;
    }

    content +=
        `<div><span class="fw-semibold">Часть света:</span> ${partOfTheWorld}</div>` +
        `<div><span class="fw-semibold">Расположение:</span> ${location}</div>`;

    if (isAuthenticated === true) {
        const linkToAdd = `<hr><a href="#" onclick="add_country('${iso3166}')">Отметить страну как посещённую</a>`
        const linkToDelete = `<hr><a href="#" onclick="delete_country('${iso3166}')">Удалить страну</a>`
        const link = is_visited ? linkToDelete : linkToAdd;

        return `<h4>${name_ru}</h4><br>${content + link}`;
    } else {
        return `<h4>${name_ru}</h4><br>${content}`;
    }
}

function add_country(countryCode) {
    const url = document.getElementById('url_add_visited_countries').dataset.url;
    const formData = new FormData();
    formData.set('code', countryCode);

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
        .then((data) => {
            const country = allCountriesGeoObjects.get(countryCode);

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
