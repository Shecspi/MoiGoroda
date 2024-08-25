const fillColorVisitedCountry = '#32b700';
const fillColorNotVisitedCountry = '#9a9a9a';
const fillOpacity = 0.6;
const strokeColor = '#FFF';
const strokeOpacity = 0.5;
let allCountriesGoeObjects = new Map();
let myMap;

ymaps.ready(init);

function init() {
    myMap = new ymaps.Map("map", {
        center: [55.76, 37.64],
        zoom: 2
    });
    const allCountryPromise = fetch('/api/country/all')
        .then((response) => {
            if (!response.ok) {
                throw new Error(response.statusText)
            }
            return response.json();
        })
        .then((data) => {
            return data;
        });

    const visitedCountryPromise = fetch('/api/country/visited')
        .then((response) => {
            if (!response.ok) {
                throw new Error(response.statusText)
            }
            return response.json();
        })
        .then((data) => {
            return data;
        });

    Promise.all([allCountryPromise, visitedCountryPromise]).then(([allCountries, visitedCountries]) => {
        ymaps.borders.load('001', {lang: 'ru', quality: 1}).then(function (geojson) {
            let countries = new Map();
            for (let i = 0; i < allCountries.length; i++) {
                countries.set(allCountries[i].code, allCountries[i].name);
            }
            console.log('Всего стран в БД: ', countries);

            let visitedCountriesSet = new Set();
            for (let i = 0; i < visitedCountries.length; i++) {
                visitedCountriesSet.add(visitedCountries[i].code);
            }

            for (let i = 0; i < geojson.features.length; i++) {
                let countryCode = geojson.features[i].properties.iso3166;
                let countryName = geojson.features[i].properties.name;
                const isVisited = visitedCountriesSet.has(countryCode);

                // Если такой страны нет в нашей БД, то пропускаем её и печатаем в консоль.
                // Если есть, то удаляем её из countries, чтобы в конце посмотреть,
                // какие страны из нашей БД не распечатались на карте.
                if (!countries.has(countryCode)) {
                    console.log(`Страны "${countryName}" нет в нашей БД`);
                    continue;
                } else {
                    countries.delete(countryCode);
                }

                let geoObject = addCountryOnMap(geojson.features[i], countryCode, countryName, isVisited);
                allCountriesGoeObjects.set(countryCode, geoObject);
            }

            console.log('Страны, которых нет в Яндексе:', countries);
        });
    });
}

function addCountryOnMap(geojson, countryCode, countryName, isVisited) {
    let contentHeader = '<span class="fw-semibold">' + countryName + '</span>'
    let linkToAdd = `<hr><a href="#" onclick="add_country('${countryCode}')">Отметить страну как посещённую</a>`

    let geoObject = new ymaps.GeoObject(geojson, {
        fillColor: isVisited ? fillColorVisitedCountry : fillColorNotVisitedCountry,
        // visitedCountriesSet.has(countryCode) ? fillColorVisitedCountry : fillColorNotVisitedCountry
        fillOpacity: fillOpacity,
        strokeColor: strokeColor,
        strokeOpacity: strokeOpacity,
    });
    geoObject.properties.set({
        balloonContentHeader: contentHeader,
        balloonContent: linkToAdd
    });
    myMap.geoObjects.add(geoObject);

    return geoObject;
}

function add_country(countryCode) {
    const url = document.getElementById('url_add_visited_country').dataset.url;
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
        });
}
