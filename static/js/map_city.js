let myMap;

let usersVisitedCitiesJSON;

// Массив, содержащий в себе ID городов, посещённых пользователем.
// Этот массив всегда существует без изменений и может быть использован для перерисовки карты.
let usersVisitedCities = [];

// Словарь, хранящий в себе все отметки на карте.
// Ключём является ID города, а значением - объект отметки.
let stateMap = new Map();

/**
 * Содержит типы отметок, которые можно использовать на карте.
 * Полный список отметок, поддерживаемях API Яндекс.карт находится по ссылке
 * https://yandex.ru/dev/jsapi-v2-1/doc/ru/v2-1/ref/reference/option.presetStorage
 */
const PlacemarkStyle = {
    OWN: {
        preset: 'islands#darkGreenDotIcon',
        zIndex: 3
    },
    TOGETHER: {
        preset: 'islands#blueDotIcon',
        zIndex: 2
    },
    SUBSCRIPTION: {
        preset: 'islands#darkOrangeDotIcon',
        zIndex: 1
    }
}

function createMap(center_lat, center_lon, zoom) {
    let myMap = new ymaps.Map("map", {
        center: [center_lat, center_lon],
        zoom: zoom,
        controls: ['fullscreenControl', 'zoomControl', 'rulerControl']
    }, {
        searchControlProvider: 'yandex#search'
    });

    return myMap;
}

function addOwnCitiesOnMap(visited_cities) {
    for (let i = 0; i < (visited_cities.length); i++) {
        let id = visited_cities[i].id
        let city = visited_cities[i].title
        let lat = visited_cities[i].lat;
        let lon = visited_cities[i].lon;
        let placemark = addPlacemarkToMap(city, lat, lon, PlacemarkStyle.OWN);

        stateMap.set(id, placemark);
        if (!usersVisitedCities.includes(id)) {
            usersVisitedCities.push(id);
        }
    }
}

function addSubscriptionsCitiesOnMap(visited_cities) {
    for (let i = 0; i < (visited_cities.length); i++) {
        let placemark;
        let id = visited_cities[i].id
        let city = visited_cities[i].title
        let lat = visited_cities[i].lat;
        let lon = visited_cities[i].lon;

        if (usersVisitedCities.includes(id)) {
            myMap.geoObjects.remove(stateMap.get(id));
            placemark = addPlacemarkToMap(city, lat, lon, PlacemarkStyle.TOGETHER);
        }
        else {
            placemark = addPlacemarkToMap(city, lat, lon, PlacemarkStyle.SUBSCRIPTION);
        }
        stateMap.set(id, placemark);
    }
}

function addPlacemarkToMap(city, lat, lon, placemarkStyle) {
    /**
     * Добавляет на карту, находящуюся в глобальной переменной myMap, отметку города city по координатам lat и lon.
     */
    let placemark = new ymaps.Placemark(
        [lat, lon],
        {
            balloonContentHeader: city,
            // balloonContent: 'Город посещён пользователями:<br>Вы'
        }, {
            preset: placemarkStyle.preset,
            zIndex: placemarkStyle.zIndex
        }
    );
    // placemarks.push(placemark);
    myMap.geoObjects.add(placemark);

    return placemark;
}

function calculateCenterCoordinates(visited_cities) {
    if (visited_cities.length > 0) {
        // Высчитываем центральную точку карты.
        // Ей является средняя координата всех городов, отображённых на карте.
        let array_lon = Array();
        let array_lat = Array();
        let zoom = 0;

        // Добавляем все координаты в один массив и находим большее и меньшее значения из них,
        // а затем вычисляем среднее, это и будет являться центром карты.
        for (let i = 0; i < visited_cities.length; i++) {
            array_lat.push(parseFloat(visited_cities[i].lat));
            array_lon.push(parseFloat(visited_cities[i].lon));
        }
        let max_lon = Math.max(...array_lon);
        let min_lon = Math.min(...array_lon);
        let max_lat = Math.max(...array_lat);
        let min_lat = Math.min(...array_lat);
        average_lon = (max_lon + min_lon) / 2;
        average_lat = (max_lat + min_lat) / 2;

        // Меняем масштаб карты в зависимости от расположения городов
        let diff = max_lat - min_lat;
        if (diff <= 1) {
            zoom = 8;
        } else if (diff > 1 && diff <= 2) {
            zoom = 7;
        } else if (diff > 2 && diff <= 4) {
            zoom = 6
        } else if (diff > 4 && diff <= 6) {
            zoom = 5;
        } else {
            zoom = 4;
        }
        return [average_lat, average_lon, zoom];
    }
    else {
        return [56.831534, 50.987919, 5];
    }
}

function getCookie(c_name)
{
    if (document.cookie.length > 0)
    {
        c_start = document.cookie.indexOf(c_name + "=");
        if (c_start != -1)
        {
            c_start = c_start + c_name.length + 1;
            c_end = document.cookie.indexOf(";", c_start);
            if (c_end == -1) c_end = document.cookie.length;
            return unescape(document.cookie.substring(c_start,c_end));
        }
    }
    return "";
}

function removeAllPlacemarks() {
    /**
     * Удаляет все отметки с карты.
     */
    for (let [id, placemark] of stateMap.entries()) {
        myMap.geoObjects.remove(placemark);
    }
}

async function send_to_server() {
    const button = document.getElementById("button_send_to_server");
    const url = button.dataset.url

    let selectedCheckboxes = document.querySelectorAll('input.checkbox_username:checked');
    let checkedValues = Array.from(selectedCheckboxes).map(cb => Number(cb.value));
    let data = {'ids': checkedValues};

    let response = await fetch(url + '?data=' + encodeURIComponent(JSON.stringify(data)), {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie("csrftoken")
        }
    });

    if (response.ok) {
        // Закрываем модальное окно
        var myModalEl = document.getElementById('subscriptions_modal_window');
        var modal = bootstrap.Modal.getInstance(myModalEl)
        modal.hide();

        // Удаляем все отметки с карты и из stateMap
        removeAllPlacemarks();
        stateMap.clear();

        const json = await response.json();
        addOwnCitiesOnMap(usersVisitedCitiesJSON);
        addSubscriptionsCitiesOnMap(json);
    }
    else {
        const element = document.getElementById('toast_validation_error');
        const toast = new bootstrap.Toast(element);
        toast.show()
    }

    return false;
}

async function init() {
    usersVisitedCitiesJSON = await getVisitedCities();
    const [center_lat, center_lon, zoom] = calculateCenterCoordinates(usersVisitedCitiesJSON);
    myMap = createMap(center_lat, center_lon, zoom);
    addOwnCitiesOnMap(usersVisitedCitiesJSON);
}

async function getVisitedCities() {
    /**
     * Делает запрос на сервер, получает список городов, посещённых пользователем,
     * и помещает его в глобальную переменную usersVisitedCities, откуда можно получить
     * данные из любого места скрипта.
     */
    let url = document.getElementById('url-api__get_visited_cities').dataset.url;
    let response = await fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie("csrftoken")
        }
    });
    if (response.ok) {
        return await response.json();
    } else {
        const element = document.getElementById('toast_request_error');
        const toast = new bootstrap.Toast(element);
        toast.show()
    }
}

ymaps.ready(init);

const button = document.getElementById('button_send_to_server');
button.addEventListener('click', function () {
    send_to_server();
});
