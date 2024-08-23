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

                for (let i = 0; i < geojson.features.length; i++) {
                    let countryCode = geojson.features[i].properties.iso3166;
                    let countryName = geojson.features[i].properties.name;
                    let contentHeader = '<span class="fw-semibold">' + countryName + '</span>'
                    let linkToAdd = `<hr><a href="#" onclick="add_country('${countryCode}')">Отметить страну как посещённую</a>`

                    // Если такой страны нет в нашей БД, то пропускаем её и печатаем в консоль.
                    // Если есть, то удаляем её из countries, чтобы в конце посмотреть,
                    // какие страны из нашей БД не распечатались на карте.
                    if (!countries.has(countryCode)) {
                        console.log(`Страны "${countryName}" нет в нашей БД`);
                        continue;
                    } else {
                        countries.delete(countryCode);
                    }

                    let geoObject = new ymaps.GeoObject(geojson.features[i], {
                        fillColor: fillColorNotVisitedCoutry,
                        fillOpacity: fillOpacity,
                        strokeColor: strokeColor,
                        strokeOpacity: strokeOpacity,
                    });
                    geoObject.properties.set({
                        balloonContentHeader: contentHeader,
                        balloonContent: linkToAdd
                    });

                    myMap.geoObjects.add(geoObject);
                }

                console.log('Страны, которых нет в Яндексе:', countries);
            });
        });
}

function add_country(countryCode) {
    const url = document.getElementById('url_add_visited_country').dataset.url;
    const formData = new FormData();
    console.log(countryCode, typeof countryCode);
    formData.set('country', countryCode);

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
    .then((data) => {});
}
