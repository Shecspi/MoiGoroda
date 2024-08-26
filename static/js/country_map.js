const fillColorVisitedCountry = '#32b700';
const fillColorNotVisitedCountry = '#9a9a9a';
const fillOpacity = 0.6;
const strokeColor = '#FFF';
const strokeOpacity = 0.5;
let allCountriesGoeObjects = new Map();
let myMap;

let allCountryState;
let visitedCountryState;

ymaps.ready(init);

function getCountries(url) {
    return fetch(url)
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

function removeQtyVisitedCountiesPlaceholder(qtyVisitedCities, qtyAllCities) {
    const block_qty_visited_countries = document.getElementById('block-qty_visited_countries');
    block_qty_visited_countries.classList.remove('placeholder');
    block_qty_visited_countries.classList.remove('bg-secondary');
    block_qty_visited_countries.innerText = `Посещено ${qtyVisitedCities} ${declensionCountry(qtyVisitedCities)} из ${qtyAllCities}`;

    const block_statistic = document.getElementById('block-statistic');
    block_statistic.classList.remove('placeholder-glow');
}

function updateQtyVisitedCountiesPlaceholder() {
    const block_qty_visited_countries = document.getElementById('block-qty_visited_countries');
    const qtyVisitedCities = visitedCountryState.size;
    const qtyAllCities = allCountryState.size;
    block_qty_visited_countries.innerText = `Посещено ${qtyVisitedCities} ${declensionCountry(qtyVisitedCities)} из ${qtyAllCities}`;
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

function init() {
    myMap = new ymaps.Map("map", {
        center: [55.76, 37.64],
        zoom: 2
    });
    const allCountryPromise = getAllCountries();
    const visitedCountryPromise = getVisitedCountries();

    Promise.all([allCountryPromise, visitedCountryPromise]).then(([allCountries, visitedCountries]) => {
        ymaps.borders.load('001', {lang: 'ru', quality: 1}).then(function (geojson) {
            allCountryState = new Map(allCountries.map(country => { return [country.code, country.name]}));
            visitedCountryState = new Set(visitedCountries.map(country => { return country.code }));

            console.log('allCountryState: ', allCountryState);
            console.log('visitedCountryState: ', visitedCountryState);

            removeQtyVisitedCountiesPlaceholder(visitedCountryState.size, allCountryState.size);

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

                const isVisited = visitedCountryState.has(countryCode);
                let geoObject = addCountryOnMap(geojson.features[i], countryCode, countryName, isVisited);
                allCountriesGoeObjects.set(countryCode, geoObject);
            }

            console.log('Страны, которых нет в Яндексе:', reserveAllCountryState);
        });
    });
}

function addCountryOnMap(geojson, countryCode, countryName, isVisited) {
    let contentHeader = '<span class="fw-semibold">' + countryName + '</span>'
    let linkToAdd = `<hr><a href="#" onclick="add_country('${countryCode}')">Отметить страну как посещённую</a>`
    let linkToDelete = `<hr><a href="#" onclick="delete_country('${countryCode}')">Удалить страну</a>`

    let geoObject = new ymaps.GeoObject(geojson, {
        fillColor: isVisited ? fillColorVisitedCountry : fillColorNotVisitedCountry,
        fillOpacity: fillOpacity,
        strokeColor: strokeColor,
        strokeOpacity: strokeOpacity,
    });
    geoObject.properties.set({
        balloonContentHeader: contentHeader,
        balloonContent: isVisited ? linkToDelete : linkToAdd
    });
    myMap.geoObjects.add(geoObject);

    return geoObject;
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
            const country = allCountriesGoeObjects.get(countryCode);

            allCountriesGoeObjects.delete(countryCode);
            myMap.geoObjects.remove(country);

            let geoObject = addCountryOnMap(country, countryCode, 'countryName', true);
            allCountriesGoeObjects.set(countryCode, geoObject);
            visitedCountryState.add(countryCode);
            updateQtyVisitedCountiesPlaceholder();
        });
}

function delete_country(countryCode) {

}
