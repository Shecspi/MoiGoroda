const fillColorVisitedCoutry = '#32b700';
const fillColorNotVisitedCoutry = '#9a9a9a';
const fillOpacity = 0.6;
const strokeColor = '#FFF';
const strokeOpacity = 0.5;

ymaps.ready(init);

function init() {
    var myMap = new ymaps.Map("map", {
        center: [55.76, 37.64],
        zoom: 2
    });
    fetch('/api/country/all')
        .then((response) => {
            if (!response.ok) {
                throw new Error(response.statusText)
            }
            return response.json();
        })
        .then((data) => {
            ymaps.borders.load('001', {lang: 'ru', quality: 1}).then(function (geojson) {
                let countries = new Map();
                for (let i = 0; i < data.length; i++) {
                    countries.set(data[i].code, data[i].name);
                }
                console.log('Всего стран в БД: ', countries);

                let countryGeoQuery = ymaps.geoQuery(geojson);
                const countryGeoQueryIterator = countryGeoQuery.getIterator();
                console.log('Всего стран у Яндекса: ', countryGeoQuery.getLength());

                // Проходим по всем странам, которые Яндекс вернул.
                // Удаляем из результатов те, которых нет в нашей базе данных.
                let country;
                while ((country = countryGeoQueryIterator.getNext()) !== countryGeoQueryIterator.STOP_ITERATION) {
                    let countryCode = country.properties._data.iso3166;
                    let countryName = country.properties._data.name;

                    if (!countries.has(countryCode)) {
                        console.log(`Страны "${countryName}" нет в нашей БД`);
                        countryGeoQuery = countryGeoQuery.remove(country);
                    } else {
                        countries.delete(countryCode);
                    }
                }
                console.log('На карте отобразилось стран: ', countryGeoQuery.getLength());
                console.log('Страны, которых нет в Яндексе:', countries);

                countryGeoQuery
                    .setOptions('fillColor', fillColorNotVisitedCoutry)
                    .setOptions('fillOpacity', fillOpacity)
                    .setOptions('strokeColor', strokeColor)
                    .setOptions('strokeOpacity', strokeOpacity)
                    .addToMap(myMap);
            });
        });
}
