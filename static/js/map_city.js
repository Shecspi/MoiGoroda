// Карта, на которой будут отображаться города
let myMap;

// Массив, содержащий в себе ID городов, посещённых пользователем.
// Этот массив всегда существует без изменений и может быть использован для перерисовки карты.
let ownCities = [];

let subscriptionCities = [];

// Массив, содержащий в себе ID городов, не посещённых пользователем.
// Этот массив всегда существует без изменений и может быть использован для перерисовки карты.
let notVisitedCities = [];

// Словарь, хранящий в себе все отментки с посещёнными городами, отображаемые в данный момент на карте
let stateOwnCities = new Map();

// Словарь, хранящий в себе все отментки с городами пользователей, на которых оформлена подписка,
// отображаемые в данный момент на карте
let stateSubscriptionCities = new Map();

// Словарь, хранящий в себе все отментки с непосещёнными городами пользователей, отображаемые в данный момент на карте
let stateNotVisitedCities = new Map();

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
        preset: 'islands#darkBlueDotIcon',
        zIndex: 2
    },
    SUBSCRIPTION: {
        preset: 'islands#brownDotIcon',
        zIndex: 4
    },
    NOT_VISITED: {
        preset: 'islands#redDotIcon',
        zIndex: 1
    }
}

function createMap(center_lat, center_lon, zoom) {
    /**
     * Создаёт и возвращает карту с центром и зумом, указанными в аргументах.
     */
    let myMap = new ymaps.Map("map", {
        center: [center_lat, center_lon],
        zoom: zoom,
        controls: ['fullscreenControl', 'zoomControl', 'rulerControl']
    }, {
        searchControlProvider: 'yandex#search'
    });

    return myMap;
}

function addOwnCitiesOnMap(visited_cities, year) {
    /**
     * Помещает на карту отметку посещённого города и сохраняет объект Placemark в глобальный словарь stateOwnCities.
     * @param visited_cities JSON-объект со списком городов
     * @param year Необязательный параметр, уазывающий за какой год нужно добавлять города на карту
     */
    for (let i = 0; i < (visited_cities.length); i++) {
        let placemark;
        let id = visited_cities[i].id
        let city = visited_cities[i].title
        let lat = visited_cities[i].lat;
        let lon = visited_cities[i].lon;
        let year_city = visited_cities[i].year

        if (year !== undefined && year !== year_city) {
            continue;
        }

        placemark = addPlacemarkToMap(city, lat, lon, PlacemarkStyle.OWN);
        stateOwnCities.set(id,  placemark);
    }
}

function addSubscriptionsCitiesOnMap(visited_cities, year) {
    /**
     * Помещает на карту отметку города, посещённого пользователем, на которого произведена подписка
     * и сохраняет объект Placemark в глобальный словарь stateSubscriptionCities.
     * В случае, если город был посещён и пользователем, и адресантом подписки, то соответствующая Placemark
     * удаляется из stateOwnCities и помещается в stateSubscriptionCities.
     * @param visited_cities JSON-объект со списком городов
     * @param year Необязательный параметр, уазывающий за какой год нужно добавлять города на карту
     */
    for (let i = 0; i < (visited_cities.length); i++) {
        let placemark;
        let id = visited_cities[i].id
        let city = visited_cities[i].title
        let lat = visited_cities[i].lat;
        let lon = visited_cities[i].lon;
        let year_city = visited_cities[i].year

        if (year !== undefined && year !== year_city) {
            continue;
        }

        if (stateOwnCities.has(id)) {
            myMap.geoObjects.remove(stateOwnCities.get(id));
            placemark = addPlacemarkToMap(city, lat, lon, PlacemarkStyle.TOGETHER);
        } else {
            placemark = addPlacemarkToMap(city, lat, lon, PlacemarkStyle.SUBSCRIPTION);
        }
        stateSubscriptionCities.set(id,  placemark);
    }
}

function addNotVisitedCitiesOnMap(not_visited_cities) {
    /**
     * Помещает на карту города, которые не были посещены ни пользователем, ни адресантом подписки.
     */
    for (let i = 0; i < (not_visited_cities.length); i++) {
        let placemark;
        let id = not_visited_cities[i].id
        let city = not_visited_cities[i].title
        let lat = not_visited_cities[i].lat;
        let lon = not_visited_cities[i].lon;

        if (!stateOwnCities.has(id) && !stateSubscriptionCities.has(id)) {
            placemark = addPlacemarkToMap(city, lat, lon, PlacemarkStyle.NOT_VISITED);
            stateNotVisitedCities.set(id, placemark);
        }
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
    /**
     * Рассчитывает координаты и зум карты в зависимости от городов, переданных в visited_cities.
     */
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

function removeOwnPlacemarks() {
    for (let [id, placemark] of stateOwnCities.entries()) {
        myMap.geoObjects.remove(placemark);
    }
}

function removeSubscriptionPlacemarks() {
    for (let [id, placemark] of stateSubscriptionCities.entries()) {
        myMap.geoObjects.remove(placemark);
    }
}

function removeNotVisitedPlacemarks() {
    for (let [id, placemark] of stateNotVisitedCities.entries()) {
        myMap.geoObjects.remove(placemark);
    }
}

async function showSubscriptionCities() {
    const button = document.getElementById("btn_show-subscriptions-cities");
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
        removeOwnPlacemarks();
        removeSubscriptionPlacemarks();
        removeNotVisitedPlacemarks();
        stateOwnCities.clear();
        stateSubscriptionCities.clear();
        stateNotVisitedCities.clear();

        subscriptionCities = await response.json();

        addOwnCitiesOnMap(ownCities);
        addSubscriptionsCitiesOnMap(subscriptionCities);
        addNotVisitedCitiesOnMap(notVisitedCities);
    }
    else {
        const element = document.getElementById('toast_validation_error');
        const toast = new bootstrap.Toast(element);
        toast.show()
    }

    return false;
}

async function showNotVisitedCities() {
    const btn = document.getElementById('btn_show-not-visited-cities');
    const url = btn.dataset.url;

    if (notVisitedCities.length === 0) {
        let response = await fetch(url, {
            method: 'GET',
            headers: {
                'X-CSRFToken': getCookie("csrftoken")
            }
        });

        if (response.ok) {
            notVisitedCities = await response.json();
            addNotVisitedCitiesOnMap(notVisitedCities);
        } else {
            const element = document.getElementById('toast_validation_error');
            const toast = new bootstrap.Toast(element);
            toast.show();

            return false;
        }
    } else {
        addNotVisitedCitiesOnMap(notVisitedCities);
    }
}

function showVisitedCitiesPreviousYear() {
    const btn = document.getElementById('btn_show-visited-cities-previous-year');

    removeOwnPlacemarks();
    removeSubscriptionPlacemarks();
    removeNotVisitedPlacemarks();
    stateOwnCities.clear();
    stateSubscriptionCities.clear();

    addOwnCitiesOnMap(ownCities, new Date().getFullYear() - 1);
    addSubscriptionsCitiesOnMap(subscriptionCities, new Date().getFullYear() - 1);
}

function hideVisitedCitiesPreviousYear() {
    const btn = document.getElementById('btn_show-visited-cities-previous-year');

    removeOwnPlacemarks();
    removeSubscriptionPlacemarks();
    removeNotVisitedPlacemarks();
    stateOwnCities.clear();
    stateSubscriptionCities.clear();

    addOwnCitiesOnMap(ownCities);
    addSubscriptionsCitiesOnMap(subscriptionCities);
}

function showVisitedCitiesCurrentYear() {
    const btn = document.getElementById('btn_show-visited-cities-previous-year');

    removeOwnPlacemarks();
    removeSubscriptionPlacemarks();
    removeNotVisitedPlacemarks();
    stateOwnCities.clear();
    stateSubscriptionCities.clear();

    addOwnCitiesOnMap(ownCities, new Date().getFullYear());
    addSubscriptionsCitiesOnMap(subscriptionCities, new Date().getFullYear());
}

function hideVisitedCitiesCurrentYear() {
    const btn = document.getElementById('btn_show-visited-cities-previous-year');

    removeOwnPlacemarks();
    removeSubscriptionPlacemarks();
    removeNotVisitedPlacemarks();
    stateOwnCities.clear();
    stateSubscriptionCities.clear();

    addOwnCitiesOnMap(ownCities);
    addSubscriptionsCitiesOnMap(subscriptionCities);
}

function hideNotVisitedCities() {
    removeNotVisitedPlacemarks();
    stateNotVisitedCities.clear();
}

async function init() {
    // Загрузка списка посещённых городов
    ownCities = await getVisitedCities();

    // Создание и центрирование карты
    const [center_lat, center_lon, zoom] = calculateCenterCoordinates(ownCities);
    myMap = createMap(center_lat, center_lon, zoom);

    // Добавление на карту посещённых городов
    addOwnCitiesOnMap(ownCities);
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
            'X-CSRFToken': getCookie("csrftoken")
        }
    });
    if (response.ok) {
        return await response.json();
    } else {
        const element = document.getElementById('toast_request_error');
        const toast = new bootstrap.Toast(element);
        toast.show();

        return [];
    }
}

ymaps.ready(init);

const button = document.getElementById('btn_show-subscriptions-cities');
const btnShowNotVisitedCities = document.getElementById('btn_show-not-visited-cities');
const btnShowVisitedCitiesPreviousYear = document.getElementById('btn_show-visited-cities-previous-year')
const btnShowVisitedCitiesCurrentYear = document.getElementById('btn_show-visited-cities-current-year')

button.addEventListener('click', function () {
    showSubscriptionCities();
});
btnShowNotVisitedCities.addEventListener('click', function () {
    if (btnShowNotVisitedCities.dataset.type === 'show') {
        showNotVisitedCities();
        btnShowNotVisitedCities.dataset.type = 'hide';
        btnShowNotVisitedCities.classList.remove('btn-outline-danger');
        btnShowNotVisitedCities.classList.add('btn-danger');
    } else {
        hideNotVisitedCities();
        btnShowNotVisitedCities.dataset.type = 'show';
        btnShowNotVisitedCities.classList.remove('btn-danger');
        btnShowNotVisitedCities.classList.add('btn-outline-danger');
    }
})
btnShowVisitedCitiesPreviousYear.addEventListener('click', function () {
    if (btnShowVisitedCitiesPreviousYear.dataset.type === 'show') {
        showVisitedCitiesPreviousYear();
        btnShowVisitedCitiesPreviousYear.dataset.type = 'hide';
        btnShowVisitedCitiesPreviousYear.classList.remove('btn-outline-secondary');
        btnShowVisitedCitiesPreviousYear.classList.add('btn-secondary');
    } else {
        hideVisitedCitiesPreviousYear();
        btnShowVisitedCitiesPreviousYear.dataset.type = 'show';
        btnShowVisitedCitiesPreviousYear.classList.remove('btn-secondary');
        btnShowVisitedCitiesPreviousYear.classList.add('btn-outline-secondary');
    }
});
btnShowVisitedCitiesCurrentYear.addEventListener('click', function () {
    if (btnShowVisitedCitiesCurrentYear.dataset.type === 'show') {
        showVisitedCitiesCurrentYear();
        btnShowVisitedCitiesCurrentYear.dataset.type = 'hide';
        btnShowVisitedCitiesCurrentYear.classList.remove('btn-outline-primary');
        btnShowVisitedCitiesCurrentYear.classList.add('btn-primary');
    } else {
        hideVisitedCitiesCurrentYear();
        btnShowVisitedCitiesCurrentYear.dataset.type = 'show';
        btnShowVisitedCitiesCurrentYear.classList.remove('btn-primary');
        btnShowVisitedCitiesCurrentYear.classList.add('btn-outline-primary');
    }
});
