let placemarks = Array();
let unique_placemarks = new Map();
let myMap;

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

function addCitiesOnMap(visited_cities, myMap) {
    for (let i = 0; i < (visited_cities.length); i++) {
        let lat = visited_cities[i][0];
        let lon = visited_cities[i][1];
        let city = visited_cities[i][2]
        add_placemark_to_map(city, lat, lon, PlacemarkStyle.OWN);
    }
}

function add_placemark_to_map(city, lat, lon, placemarkStyle,) {
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
    placemarks.push(placemark);
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
            array_lat.push(parseFloat(visited_cities[i][0]));
            array_lon.push(parseFloat(visited_cities[i][1]));
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

function remove_all_placemarks() {
    for (let placemark of placemarks) {
        myMap.geoObjects.remove(placemark);
    }
    placemarks.length = 0;
    unique_placemarks.clear();
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
        var myModalEl = document.getElementById('subscriptions_modal_window');
        var modal = bootstrap.Modal.getInstance(myModalEl)
        modal.hide();

        remove_all_placemarks()

        const json = await response.json();
        // const own_cities = json.own;
        // const subscriptions_cities = json.subscriptions

        // Наносим собственные города на карту
        // for (let i = 0; i < own_cities.length; i++) {
        //     const id = own_cities[i].id
        //     const city = own_cities[i].title;
        //     const lat = own_cities[i].coordinates.lat;
        //     const lon = own_cities[i].coordinates.lon;
        //
        //     let placemark = add_placemark_to_map(city, lat, lon, PlacemarkStyle.OWN);
        //     unique_placemarks.set(id, placemark);
        // }

        // Наносим города пользователей, на которых оформлена подписка
        for (let i = 0; i < json.length; i++) {
            const username = json[i].username;
            const id = json[i].id;
            const city = json[i].title;
            const lat = json[i].lat;
            const lon = json[i].lon;
            let placemark;

            if (unique_placemarks.has(id)) {
                myMap.geoObjects.remove(unique_placemarks.get(id));
                placemark = add_placemark_to_map(city, lat, lon, PlacemarkStyle.TOGETHER);
            }
            else {
                placemark = add_placemark_to_map(city, lat, lon, PlacemarkStyle.SUBSCRIPTION);
            }
            unique_placemarks.set(id, placemark);
        }
    }
    else {
        const element = document.getElementById('toast_validation_error');
        const toast = new bootstrap.Toast(element);
        toast.show()
    }

    return false;
}

async function init() {
    const [center_lat, center_lon, zoom] = calculateCenterCoordinates(visited_cities);
    myMap = createMap(center_lat, center_lon, zoom);
    addCitiesOnMap(visited_cities, myMap);
}

ymaps.ready(init);

const button = document.getElementById('button_send_to_server');
button.addEventListener('click', function () {
    send_to_server();
});
