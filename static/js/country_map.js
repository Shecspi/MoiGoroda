const fillColorVisitedCountry = '#32b700';
const fillColorNotVisitedCountry = '#9a9a9a';
const fillOpacity = 0.6;
const strokeColor = '#FFF';
const strokeOpacity = 0.5;
let allCountriesGeoObjects = new Map();

let myMap;
let allCountryState;
let visitedCountryState;

ymaps.ready(init);

function init() {
    removeSpinner();

    myMap = new ymaps.Map("map", {
        center: [55.76, 37.64],
        zoom: 2
    });

    const allPromises = [];
    if (isAuthenticated === true) {
        allPromises.push(getAllCountries());
        allPromises.push(getVisitedCountries());
    } else {
        allPromises.push(getAllCountries());
    }

    // Если пользователь авторизован, то в allPromises будет храниться 2 массива,
    // а в случае неавторизованного пользователя - только один allCountries.
    Promise.all([...allPromises]).then(([allCountries, visitedCountries]) => {
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

            // Достаём из geojson все страны, которые есть в Яндексе и добавляем их на карту.
            // А также сверяем с нашей базой. Если находятся какие-то расхождения,
            // то отправляем их на сервер для дальнейшего исследования.
            let yandexCountries = new Map();
            geojson.features.forEach(function (country) {
                const countryCode = country.properties.iso3166;
                const geoObject = addCountryOnMap(country, allCountryState.get(countryCode));
                allCountriesGeoObjects.set(countryCode, geoObject);

                yandexCountries.set(countryCode, country.properties.name);
            });
            compareCountriesWithYandexAndLocalBD(yandexCountries, allCountryState);

            // Обновляем информацию на тулбаре
            if (isAuthenticated === true) {
                showQtyVisitedCountiesPlaceholder(visitedCountryState.size, allCountryState.size);
            } else {
                showQtyAllCountries(allCountryState.size);
            }
        });
    });
}

function getCountries(url) {
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
    return getCountries(url);
}

function getVisitedCountries() {
    const url = document.getElementById('url_get_visited_countries').dataset.url;
    return getCountries(url);
}

function compareCountriesWithYandexAndLocalBD(yandexCountries, localCountries) {
    /**
     * Сравнивает словари стран из БД сервиса и стран, которые предоставляет Яндекс.
     * Если находятся расхождения, то они отправляются на специальный эндпоинт.
     */
    const url = document.getElementById('url_revieve_unknown_countries').dataset.url;
    let unknownCountiesFromYandex = new Map();
    let localCountriesCopy = new Map(localCountries);
    yandexCountries.forEach(function (name, code) {
        if (!localCountries.has(code)) {
            unknownCountiesFromYandex.set(code, name);
        } else {
            localCountriesCopy.delete(code);
        }
    });

    if (unknownCountiesFromYandex.size > 0 || localCountriesCopy.size > 0) {
        const data = new FormData();
        data.set('unknown_from_yandex', JSON.stringify(Object.fromEntries(unknownCountiesFromYandex)));
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

            let geoObject = addCountryOnMap(country, countryCode, countryName, true);
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

            let geoObject = addCountryOnMap(country, countryCode, countryName, false);
            allCountriesGeoObjects.set(countryCode, geoObject);

            updateQtyVisitedCountries();

            showSuccessToast('Успешно', `Страна <strong>${country.properties._data.name}</strong> успешно удалена из списка посещённых Вами`);
        });
}

function showQtyVisitedCountiesPlaceholder(qtyVisitedCities, qtyAllCities) {
    const block_qty_visited_countries = document.getElementById('block-qty_visited_countries');
    block_qty_visited_countries.classList.remove('placeholder');
    block_qty_visited_countries.classList.remove('bg-secondary');
    block_qty_visited_countries.classList.remove('placeholder-lg');
    block_qty_visited_countries.innerHTML = `${declensionVisited(qtyVisitedCities)} <span class="fs-4 fw-medium">${qtyVisitedCities}</span> ${declensionCountry(qtyVisitedCities)} из ${qtyAllCities}`;

    const block_statistic = document.getElementById('block-statistic');
    block_statistic.classList.remove('placeholder-glow');
}

/**
 * Функция отображает количество всех стран в блоке с id 'block-qty_visited_countries'.
 * Она используется для неавторизованных пользователей.
 * @param {number} qtyAllCountries - количество всех стран.
 */
function showQtyAllCountries(qtyAllCountries) {
    const block_qty_visited_countries = document.getElementById('block-qty_visited_countries');
    block_qty_visited_countries.classList.remove('placeholder');
    block_qty_visited_countries.classList.remove('bg-secondary');
    block_qty_visited_countries.classList.remove('placeholder-lg');
    block_qty_visited_countries.innerHTML = `Всего <span class="fs-4 fw-medium">${qtyAllCountries}</span> ${declensionCountry(qtyAllCountries)}`;

    const block_statistic = document.getElementById('block-statistic');
    block_statistic.classList.remove('placeholder-glow');
}


/**
 * Функция обновляет количество посещенных стран в тулбаре.
 */
function updateQtyVisitedCountries() {
    const block_qty_visited_countries = document.getElementById('block-qty_visited_countries');
    const qtyVisitedCities = visitedCountryState.size;
    const qtyAllCities = allCountryState.size;
    block_qty_visited_countries.innerHTML = `${declensionVisited(qtyVisitedCities)} <span class="fs-4 fw-medium">${qtyVisitedCities}</span> ${declensionCountry(qtyVisitedCities)} из ${qtyAllCities}`;
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
