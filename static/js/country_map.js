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

function updateQtyVisitedCountiesPlaceholder() {
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

function init() {
    // Удаляем спиннер
    const map_element = document.getElementById('map');
    map_element.innerHTML = '';

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
            allCountryState = new Map(allCountries.map(country => {
                return [country.code, {name: country.name, 'to_delete': country.to_delete}]
            }));
            if (isAuthenticated === true) {
                visitedCountryState = new Set(visitedCountries.map(country => {
                    return country.code
                }));
            }

            // Словарь стран, которые есть в Яндексе
            let yandexCountries = new Map();
            geojson.features.forEach(function (country) {
                yandexCountries.set(country.properties.iso3166, country.properties.name);
            });

            compareCountriesWithYandexAndLocalBD(yandexCountries, allCountryState);

            if (isAuthenticated === true) {
                showQtyVisitedCountiesPlaceholder(visitedCountryState.size, allCountryState.size);
            } else {
                showQtyAllCountries(allCountryState.size);
            }

            let reserveAllCountryState = new Map(allCountryState);

            for (let i = 0; i < geojson.features.length; i++) {
                let countryCode = geojson.features[i].properties.iso3166;
                let countryName = geojson.features[i].properties.name;

                // Если такой страны нет в нашей БД, то пропускаем её и печатаем в консоль.
                // Если есть, то удаляем её из countries, чтобы в конце посмотреть,
                // какие страны из нашей БД не распечатались на карте.
                if (!allCountryState.has(countryCode)) {
                    console.log(`Страны "${countryName}" нет в нашей БД`);
                    continue;
                } else {
                    reserveAllCountryState.delete(countryCode);
                }

                const isVisited = isAuthenticated === true ? visitedCountryState.has(countryCode) : false;
                let geoObject = addCountryOnMap(geojson.features[i], countryCode, countryName, isVisited);
                allCountriesGeoObjects.set(countryCode, geoObject);
            }
        });
    });
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

function addCountryOnMap(geojson, countryCode, countryName, isVisited) {
    let contentHeader = '<span class="fw-semibold">' + countryName + '</span>'

    let geoObject = new ymaps.GeoObject(geojson, {
        fillColor: isVisited ? fillColorVisitedCountry : fillColorNotVisitedCountry,
        fillOpacity: fillOpacity,
        strokeColor: strokeColor,
        strokeOpacity: strokeOpacity,
    });

    if (isAuthenticated === true) {
        let linkToAdd = `<hr><a href="#" onclick="add_country('${countryCode}')">Отметить страну как посещённую</a>`
        let linkToDelete = `<hr><a href="#" onclick="delete_country('${countryCode}')">Удалить страну</a>`
        geoObject.properties.set({
            balloonContentHeader: contentHeader,
            balloonContent: isVisited ? linkToDelete : linkToAdd
        });
    } else {
        geoObject.properties.set({
            balloonContentHeader: contentHeader
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
            updateQtyVisitedCountiesPlaceholder();

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

            updateQtyVisitedCountiesPlaceholder();

            showSuccessToast('Успешно', `Страна <strong>${country.properties._data.name}</strong> успешно удалена из списка посещённых Вами`);
        });
}
