const fillColorVisitedCountry = '#32b700';
const fillColorNotVisitedCountry = '#9a9a9a';
const fillOpacity = 0.6;
const strokeColor = '#FFF';
const strokeOpacity = 0.5;

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
ymaps.ready(init);

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
    removeSpinner();

    myMap = new ymaps.Map("map", {
        center: [55.76, 37.64],
        zoom: 3
    });

    const allPromises = [];
    if (isAuthenticated === true) {
        allPromises.push(getAllCountries());
        allPromises.push(getVisitedCountries());
        allPromises.push(getPartsOfTheWorld());
        allPromises.push(getLocations());
    } else {
        allPromises.push(getAllCountries());
    }

    // Если пользователь авторизован, то в allPromises будет храниться 2 массива,
    // а в случае неавторизованного пользователя - только один allCountries.
    Promise.all([...allPromises]).then(([
                                            allCountries,
                                            visitedCountries,
                                            partsOfTheWorld,
                                            getLocations,
                                        ]) => {
        ymaps.borders.load('001', {lang: 'ru', quality: 1}).then(function (geojson) {
            // Словари со странами и посещёнными странами из БД сервиса
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
            allPartsOfTheWorld = new Set(partsOfTheWorld.map(country => country.name));
            allLocations = new Set(getLocations.map(location => location.name));

            // Достаём из geojson все страны, которые есть в Яндексе и добавляем их на карту.
            // А также сверяем с нашей базой. Если находятся какие-то расхождения,
            // то отправляем их на сервер для дальнейшего исследования.
            let yandexCountries = new Map();
            geojson.features.forEach(function (country) {
                const countryCode = country.properties.iso3166;
                yandexCountries.set(countryCode, country.properties.name);

                // Если в Яндексе есть страна, которой нет в БД сервиса,
                // то просто пропускаем такую страну и не отображаем её на карте.
                // Дальше специальный обработчик отправит все такие страны на сервер.
                if (!allCountryState.has(countryCode)) {
                    return;
                }

                const geoObject = addCountryOnMap(country, allCountryState.get(countryCode));
                allCountriesGeoObjects.set(countryCode, geoObject);
            });
            compareCountriesWithYandexAndLocalBD(yandexCountries, allCountryState);

            showQtyCountries(allCountryState.size, isAuthenticated ? visitedCountryState.size : null);
            enablePartOfTheWorldButton(partsOfTheWorld);
            enableLocationsButton(getLocations);
        });
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

function addCountryOnMap(geojson, countryObject) {
    const contentHeader = `<div>${countryObject.name}</div>`;
    let content = `<div><span class="fw-semibold">Часть света:</span> ${countryObject.part_of_the_world}</div>` +
        `<div><span class="fw-semibold">Расположение:</span> ${countryObject.location}</div>`;
    if (countryObject.fullname) {
        content = `<div><span class="fw-semibold">Полное название:</span> ${countryObject.fullname}</div>` + content;
    }

    const geoObject = new ymaps.GeoObject(geojson, {
        fillColor: countryObject.is_visited ? fillColorVisitedCountry : fillColorNotVisitedCountry,
        fillOpacity: fillOpacity,
        strokeColor: strokeColor,
        strokeOpacity: strokeOpacity,
    });

    if (isAuthenticated === true) {
        const linkToAdd = `<hr><a href="#" onclick="add_country('${countryObject.code}')">Отметить страну как посещённую</a>`
        const linkToDelete = `<hr><a href="#" onclick="delete_country('${countryObject.code}')">Удалить страну</a>`
        const link = countryObject.is_visited ? linkToDelete : linkToAdd;

        geoObject.properties.set({
            balloonContentHeader: contentHeader,
            balloonContent: content + link
        });
    } else {
        geoObject.properties.set({
            balloonContentHeader: contentHeader,
            balloonContent: content
        });
    }

    myMap.geoObjects.add(geoObject);

    return geoObject;
}

function add_country(countryCode) {
    const url = document.getElementById('url_add_visited_countries').dataset.url;
    const countryName = allCountryState.get(countryCode).name;
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

            allCountriesGeoObjects.delete(countryCode);
            myMap.geoObjects.remove(country);

            allCountryState.get(countryCode).is_visited = true;
            let geoObject = addCountryOnMap(country, allCountryState.get(countryCode));
            allCountriesGeoObjects.set(countryCode, geoObject);
            visitedCountryState.add(countryCode);
            updateQtyVisitedCountries();

            showSuccessToast('Успешно', `Страна <strong>${country.properties._data.name}</strong> успешно добавлена как посещённая Вами`);
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
    } else if ([2, 3, 4].includes(qtyOfCountries % 10)) {
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

/**
 * Функция удаляет спиннер загрузки карты.
 */
function removeSpinner() {
    const map_element = document.getElementById('map');
    map_element.innerHTML = '';
}
