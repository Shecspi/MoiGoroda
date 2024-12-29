/**
 * Реализует отображение карты и меток на ней, запрос посещённых
 * и непосещённых городов с сервера и обновление меток на карте.
 *
 * ----------------------------------------------
 *
 * Copyright © Egor Vavilov (Shecspi)
 * Licensed under the Apache License, Version 2.0
 *
 * ----------------------------------------------
 */

class City {
    id;
    name;
    region;
    lat;
    lon;
    year_of_visit;
    date_of_visit;
}

const MarkerStyle = {
    OWN: 'own',
    TOGETHER: 'together',
    SUBSCRIPTION: 'subscription',
    NOT_VISITED: 'not_visited'
}

// Иконка для посещённого пользователем города
const icon_visited_pin = L.divIcon({
    className: 'custom-icon-visited-pin',
    html: '<i class="fa-solid fa-location-dot fs-3 text-success" style="text-shadow: 0 0 2px #333333;"></i>',
    iconSize: [21, 28],
    anchor: [10.5, 28]
});

// Иконка для города, который не посетил ни пользователь, ни те, на кого он подписан
const icon_not_visited_pin = L.divIcon({
    className: 'custom-icon-not_visited-pin',
    html: '<i class="fa-solid fa-location-dot fs-3 text-danger" style="text-shadow: 0 0 2px #333333;"></i>',
    iconSize: [21, 28],
    anchor: [10.5, 28]
});

// Иконка для города, который был посещён пользователем и кем-то из тех, на кого он подписан
const icon_together_pin = L.divIcon({
    className: 'custom-icon-together-pin',
    html: '<i class="fa-solid fa-location-dot fs-3 text-primary" style="text-shadow: 0 0 2px #333333;"></i>',
    iconSize: [21, 28],
    anchor: [10.5, 28]
});

// Иконка для города, который не был посещён пользователя, но посещён кем-то из тех, на кого он подписан
const icon_subscription_pin = L.divIcon({
    className: 'custom-icon-together-pin',
    html: '<i class="fa-solid fa-location-dot fs-3 text-secondary" style="text-shadow: 0 0 2px #333333;"></i>',
    iconSize: [21, 28],
    anchor: [10.5, 28]
});

class ToolbarActions {
    constructor() {
        // Массив, содержащий в себе ID городов, посещённых пользователем.
        // Этот массив может быть использован для перерисовки карты, повторно с сервера он никогда не запрашивается.
        // Единственный момент, когда он может быть изменён - это добавление посещённого города с карты.
        // В этот момент город удаляется из this.notVisitedCities и помещается в this.ownCities.
        this.ownCities = [];

        // Массив, содержащий в себе ID городов, посещённых пользователями, на которых произведена подписка.
        // Этот массив обновляется каждый раз при отображении городов пользователей, на которых произведена подписка.
        this.subscriptionCities = [];

        // Массив, содержащий в себе ID городов, не посещённых пользователем.
        // Этот массив всегда существует без изменений и может быть использован для перерисовки карты.
        this.notVisitedCities = [];

        // Словарь, хранящий в себе все отментки с посещёнными городами, отображаемые в данный момент на карте
        this.stateOwnCities = new Map();

        // Словарь, хранящий в себе все отментки с городами пользователей, на которых оформлена подписка,
        // отображаемые в данный момент на карте
        this.stateSubscriptionCities = new Map();

        // Словарь, хранящий в себе все отментки с непосещёнными городами пользователей, отображаемые в данный момент на карте
        this.stateNotVisitedCities = new Map();

        // Ниже определяются кнопки. Для каждой из них есть 2 переменные:
        // - btn... - экземпляр класса Button для доступа к его методам.
        // - element... - Непосредственно сам HTML-элемент, чтобы иметь доступ к его параметрам.
        this.btnShowSubscriptionCities = new Button(
            'btn_show-subscriptions-cities',
            'btn-success',
            'btn-outline-success'
        )
        this.elementShowSubscriptionCities = this.btnShowSubscriptionCities.get_element();

        this.btnShowNotVisitedCities = new Button(
            'btn_show-not-visited-cities',
            'btn-danger',
            'btn-outline-danger'
        )
        this.elementShowNotVisitedCities = this.btnShowNotVisitedCities.get_element();

        this.btnShowVisitedCitiesPreviousYear = new Button(
            'btn_show-visited-cities-previous-year',
            'btn-secondary',
            'btn-outline-secondary'
        )
        this.elementShowVisitedCitiesPreviousYear = this.btnShowVisitedCitiesPreviousYear.get_element();

        this.btnShowVisitedCitiesCurrentYear = new Button(
            'btn_show-visited-cities-current-year',
            'btn-primary',
            'btn-outline-primary'
        )
        this.elementShowVisitedCitiesCurrentYear = this.btnShowVisitedCitiesCurrentYear.get_element();

        this.set_handlers();
    }

    set_handlers() {
        this.elementShowSubscriptionCities.addEventListener('click', () => {
            this.showSubscriptionCities();

            this.btnShowVisitedCitiesPreviousYear.off()
            this.btnShowVisitedCitiesCurrentYear.off();
        });

        this.elementShowNotVisitedCities.addEventListener('click', () => {
            if (this.elementShowNotVisitedCities.dataset.type === 'show') {
                this.showNotVisitedCities();
                this.btnShowNotVisitedCities.on();
            } else {
                this.hideNotVisitedCities();
                this.btnShowNotVisitedCities.off();
            }
        })

        this.elementShowVisitedCitiesPreviousYear.addEventListener('click', () => {
            if (this.elementShowVisitedCitiesPreviousYear.dataset.type === 'show') {
                this.showVisitedCitiesPreviousYear();
                this.btnShowVisitedCitiesPreviousYear.on();
                this.btnShowNotVisitedCities.off();
                this.btnShowNotVisitedCities.disable();
                this.btnShowVisitedCitiesCurrentYear.off();
            } else {
                this.hideVisitedCitiesPreviousYear();
                this.btnShowVisitedCitiesPreviousYear.off();
                this.btnShowNotVisitedCities.enable();
            }
        });

        this.elementShowVisitedCitiesCurrentYear.addEventListener('click', () => {
            if (this.elementShowVisitedCitiesCurrentYear.dataset.type === 'show') {
                this.showVisitedCitiesCurrentYear();

                this.btnShowVisitedCitiesCurrentYear.on();
                this.btnShowNotVisitedCities.off();
                this.btnShowNotVisitedCities.disable();
                this.btnShowVisitedCitiesPreviousYear.off();
            } else {
                this.hideVisitedCitiesCurrentYear();
                this.btnShowVisitedCitiesCurrentYear.off();
                this.btnShowNotVisitedCities.enable();
            }
        });
    }

    async showSubscriptionCities() {
        const url = this.elementShowSubscriptionCities.dataset.url

        let selectedCheckboxes = document.querySelectorAll('input.checkbox_username:checked');
        let checkedValues = Array.from(selectedCheckboxes).map(cb => Number(cb.value));
        let data = {'id': checkedValues};

        let button = document.getElementById('btn_show-subscriptions-cities');
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm" aria-hidden="true"></span>&nbsp;&nbsp;&nbsp;<span role="status">Загрузка...</span>';

        let response = await fetch(url + '?data=' + encodeURIComponent(JSON.stringify(data)), {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie("csrftoken")
            }
        });

        if (response.ok) {
            // Закрываем модальное окно
            let myModalEl = document.getElementById('subscriptions_modal_window');
            let modal = bootstrap.Modal.getInstance(myModalEl)
            modal.hide();

            // Удаляем все отметки с карты и из stateMap
            this.removeOwnMarkers();
            this.removeSubscriptionMarkers();
            this.removeNotVisitedMarkers();
            this.stateOwnCities.clear();
            this.stateSubscriptionCities.clear();
            this.stateNotVisitedCities.clear();

            this.subscriptionCities = await response.json();

            this.addOwnCitiesOnMap();
            this.addSubscriptionsCitiesOnMap();
            if (this.elementShowNotVisitedCities.dataset.type === 'hide') {
                this.addNotVisitedCitiesOnMap();
            }
        } else {
            const element = document.getElementById('toast_validation_error');
            const toast = new bootstrap.Toast(element);
            toast.show()
        }

        button.disabled = false;
        button.innerText = 'Применить';

        return false;
    }

    async showNotVisitedCities() {
        const url = this.elementShowNotVisitedCities.dataset.url;

        if (this.notVisitedCities.length === 0) {
            let response = await fetch(url, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': getCookie("csrftoken")
                }
            });

            if (response.ok) {
                this.notVisitedCities = await response.json();
                this.addNotVisitedCitiesOnMap();
            } else {
                showDangerToast('Ошибка', 'Произошла ошибка при загрузке данных');
                return false;
            }
        } else {
            this.addNotVisitedCitiesOnMap();
        }
    }

    showVisitedCitiesPreviousYear() {
        const btn = document.getElementById('btn_show-visited-cities-previous-year');

        this.removeOwnMarkers();
        this.removeSubscriptionMarkers();
        this.removeNotVisitedMarkers();
        this.stateOwnCities.clear();
        this.stateSubscriptionCities.clear();

        this.addOwnCitiesOnMap(new Date().getFullYear() - 1);
        this.addSubscriptionsCitiesOnMap(new Date().getFullYear() - 1);
    }

    showVisitedCitiesCurrentYear() {
        const btn = document.getElementById('btn_show-visited-cities-previous-year');

        this.removeOwnMarkers();
        this.removeSubscriptionMarkers();
        this.removeNotVisitedMarkers();
        this.stateOwnCities.clear();
        this.stateSubscriptionCities.clear();

        this.addOwnCitiesOnMap(new Date().getFullYear());
        this.addSubscriptionsCitiesOnMap(new Date().getFullYear());
    }

    hideVisitedCitiesPreviousYear() {
        const btn = document.getElementById('btn_show-visited-cities-previous-year');

        this.removeOwnMarkers();
        this.removeSubscriptionMarkers();
        this.removeNotVisitedMarkers();
        this.stateOwnCities.clear();
        this.stateSubscriptionCities.clear();

        this.addOwnCitiesOnMap();
        this.addSubscriptionsCitiesOnMap();
    }

    hideVisitedCitiesCurrentYear() {
        const btn = document.getElementById('btn_show-visited-cities-previous-year');

        this.removeOwnMarkers();
        this.removeSubscriptionMarkers();
        this.removeNotVisitedMarkers();
        this.stateOwnCities.clear();
        this.stateSubscriptionCities.clear();

        this.addOwnCitiesOnMap();
        this.addSubscriptionsCitiesOnMap();
    }

    hideNotVisitedCities() {
        this.removeNotVisitedMarkers();
        this.stateNotVisitedCities.clear();
    }

    addSubscriptionsCitiesOnMap(year) {
        /**
         * Помещает на карту отметку города, посещённого пользователем, на которого произведена подписка
         * и сохраняет объект Placemark в глобальный словарь stateSubscriptionCities.
         * В случае, если город был посещён и пользователем, и адресантом подписки, то соответствующая Placemark
         * удаляется из stateOwnCities и помещается в stateSubscriptionCities.
         * @param year Необязательный параметр, уазывающий за какой год нужно добавлять города на карту
         */
        let usersWhoVisitedCity = this.getUsersWhoVisitedCity();

        for (let i = 0; i < this.subscriptionCities.length; i++) {
            const city = new City();

            city.id = this.subscriptionCities[i].id;
            city.name = this.subscriptionCities[i].title;
            city.region = this.subscriptionCities[i].region_title;
            city.lat = this.subscriptionCities[i].lat;
            city.lon = this.subscriptionCities[i].lon;
            city.year_of_visit = this.subscriptionCities[i].year;

            if (year !== undefined && year !== city.year_of_visit) {
                continue;
            }
            if (this.stateSubscriptionCities.has(city.id)) {
                continue;
            }

            let marker_style;
            if (this.stateOwnCities.has(city.id)) {
                this.myMap.removeLayer(this.stateOwnCities.get(city.id));
                marker_style = MarkerStyle.TOGETHER
            } else {
                marker_style = MarkerStyle.SUBSCRIPTION;
            }

            const marker = this.addMarkerToMap(
                city,
                marker_style,
                usersWhoVisitedCity.get(city.id)
            );
            this.stateSubscriptionCities.set(city.id, marker);
        }
    }

    addOwnCitiesOnMap(year) {
        /**
         * Помещает на карту отметку посещённого города и сохраняет объект Placemark в глобальный словарь stateOwnCities.
         * @param year Необязательный параметр, указывающий за какой год нужно добавлять города на карту
         */
        for (let i = 0; i < (this.ownCities.length); i++) {
            const city = new City();

            city.id = this.ownCities[i].id;
            city.name = this.ownCities[i].title;
            city.region = this.ownCities[i].region_title;
            city.lat = this.ownCities[i].lat;
            city.lon = this.ownCities[i].lon;
            city.year_of_visit = this.ownCities[i].year;
            city.date_of_visit = this.ownCities[i].date_of_visit;

            // Если указан год, то добавляем на карту только города, которые были посещены в указанном году
            if (year !== undefined && year !== city.year_of_visit) {
                continue;
            }

            let marker = this.addMarkerToMap(city, MarkerStyle.OWN);
            this.stateOwnCities.set(city.id, marker);
        }
    }

    /**
     * Помещает на карту города, которые не были посещены ни пользователем, ни адресантом подписки.
     */
    addNotVisitedCitiesOnMap() {
        for (let i = 0; i < (this.notVisitedCities.length); i++) {
            const city = new City();
            city.id = this.notVisitedCities[i].id;
            city.name = this.notVisitedCities[i].title;
            city.region = this.notVisitedCities[i].region_title;
            city.lat = this.notVisitedCities[i].lat;
            city.lon = this.notVisitedCities[i].lon;

            // Добавляем не посещённый город только в том случае, если его не посетил ни сам пользователь,
            // ни те, на кого он подписан. То есть этого города не должно быть в stateOwnCities и stateSubscriptionCities.
            if (!this.stateOwnCities.has(city.id) && !this.stateSubscriptionCities.has(city.id)) {
                const marker = this.addMarkerToMap(city, MarkerStyle.NOT_VISITED);
                this.stateNotVisitedCities.set(city.id, marker);
            }
        }
    }

    addMarkerToMap(city, marker_style, users) {
        /**
         * Добавляет на карту this.myMap маркер города 'city.name' по координатам 'city.lat' и 'city.lon'.
         * Добавляет к маркеру окно, открывающееся по клику на него, в котором содержится
         * дополнительная информация о городе.
         *
         * Возвращает созданный маркер.
         */
        let icon;
        switch (marker_style) {
            case MarkerStyle.OWN:
                icon = icon_visited_pin;
                break;
            case MarkerStyle.NOT_VISITED:
                icon = icon_not_visited_pin;
                break;
            case MarkerStyle.SUBSCRIPTION:
                icon = icon_subscription_pin;
                break;
            case MarkerStyle.TOGETHER:
                icon = icon_together_pin;
                break;
        }
        const marker = L.marker([city.lat, city.lon], {icon: icon}).addTo(this.myMap);

        let content = '';
        content += `<div><span class="fw-semibold fs-3">${city.name}</span></div>`;
        content += `<div><small class="text-secondary fw-medium fs-6">${city.region}</small></div>`;
        let linkToAdd = `<a href="#" onclick="open_modal_for_add_city('${city.name}', '${city.id}', '${city.region}')">Отметить как посещённый</a>`
        const date_of_visit = new Date(city.date_of_visit).toLocaleDateString();

        if (marker_style === MarkerStyle.SUBSCRIPTION) {
            content += '<p>Вы не были в этом городе</p>';
            content += `<p>Пользователи, посетившие город:<br> ${users.join(', ')}</p><hr>${linkToAdd}`;
        } else if (marker_style === MarkerStyle.TOGETHER) {
            content += `<p>Пользователи, посетившие город:<br> ${users.join(', ')}</p>`;
        } else if (marker_style === MarkerStyle.NOT_VISITED) {
            content += `<p>Вы не были в этом городе</p><hr>${linkToAdd}`;
        } else {
            content += `<p><span class='fw-semibold'>Дата посещения:</span> ${date_of_visit}</p>`
        }
        marker.bindPopup(content, {offset: [0, -7]});

        marker.bindTooltip(city.name, {
            direction: 'top',
            offset: [0, -14]
        });
        marker.on('mouseover', function () {
            const tooltip = this.getTooltip();
            if (this.isPopupOpen()) {
                tooltip.setOpacity(0.0);
            } else {
                tooltip.setOpacity(0.9);
            }
        });
        marker.on('click', function () {
            this.getTooltip().setOpacity(0.0);
        });

        return marker;
    }

    updatePlacemark(id) {
        if (this.stateNotVisitedCities.has(id)) {
            // Получаем данные города и удаляем его из списка не посещённых
            let city = [];
            for (let i = this.notVisitedCities.length - 1; i >= 0; i--) {
                if (this.notVisitedCities[i].id === id) {
                    city = this.notVisitedCities[i];
                    this.notVisitedCities.splice(i, 1);
                    break;
                }
            }

            // Удаляем метку на карте и в глобальном состоянии
            let marker = this.stateNotVisitedCities.get(id);
            this.stateNotVisitedCities.delete(id);
            this.myMap.removeLayer(marker);

            // Добавляем новую метку на карту
            this.ownCities.push(city);
            this.stateOwnCities.set(id, marker);
            this.addMarkerToMap(city, MarkerStyle.OWN);
        } else if (this.stateSubscriptionCities.has(id)) {
            // Получаем данные города
            let city = [];
            for (let i = this.subscriptionCities.length - 1; i >= 0; i--) {
                if (this.subscriptionCities[i].id === id) {
                    city = this.subscriptionCities[i];
                    break;
                }
            }

            // Удаляем старую метку на карте и в глобальном состоянии
            let old_marker = this.stateSubscriptionCities.get(id);
            this.stateSubscriptionCities.delete(id);
            this.myMap.removeLayer(old_marker);

            // Добавляем новую метку на карту
            this.ownCities.push(city);
            let usersWhoVisitedCity = this.getUsersWhoVisitedCity();
            let new_marker = this.addMarkerToMap(
                city,
                MarkerStyle.TOGETHER,
                usersWhoVisitedCity.get(id)
            );
            this.stateSubscriptionCities.set(id, new_marker);
        } else {
            throw new Error(`Неизвестное состояние добавленного города с ID ${id}`);
        }
    }

    removeOwnMarkers() {
        for (let [id, marker] of this.stateOwnCities.entries()) {
            this.myMap.removeLayer(marker);
        }
    }

    removeSubscriptionMarkers() {
        for (let [id, marker] of this.stateSubscriptionCities.entries()) {
            this.myMap.removeLayer(marker);
        }
    }

    removeNotVisitedMarkers() {
        for (let [id, marker] of this.stateNotVisitedCities.entries()) {
            this.myMap.removeLayer(marker);
        }
    }

    getUsersWhoVisitedCity() {
        let usersWhoVisitedCity = new Map();

        for (let i = 0; i < (this.subscriptionCities.length); i++) {
            let city = this.subscriptionCities[i];
            if (!usersWhoVisitedCity.has(city.id)) {
                usersWhoVisitedCity.set(city.id, [])
                if (this.stateOwnCities.has(city.id)) {
                    usersWhoVisitedCity.get(city.id).push('Вы');
                }
            }
            usersWhoVisitedCity.get(city.id).push(city.username);
        }

        return usersWhoVisitedCity
    }

    createMap(center_lat, center_lon, zoom) {
        /**
         * Создаёт и возвращает карту с центром и зумом, указанными в аргументах.
         */
        this.myMap = L.map('map', {
            attributionControl: false,
            zoomControl: false
        }).setView([center_lat, center_lon], zoom);

        const myAttrControl = L.control.attribution().addTo(this.myMap);
        myAttrControl.setPrefix('');
        L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
            maxZoom: 19,
            attribution: 'Используются карты &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> под лицензией <a href="https://opendatacommons.org/licenses/odbl/">ODbL.</a>'
        }).addTo(this.myMap);

        const zoomControl = L.control.zoom({
            zoomInTitle: 'Нажмите, чтобы приблизить карту',
            zoomOutTitle: 'Нажмите, чтобы отдалить карту'
        });
        zoomControl.addTo(this.myMap);

        this.myMap.addControl(new L.Control.Fullscreen({
            title: {
                'false': 'Полноэкранный режим',
                'true': 'Выйти из полноэкранного режима'
            }
        }));
    }

    async getVisitedCities() {
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
            this.ownCities = await response.json();
        } else {
            showDangerToast('Ошибка', 'Что-то пошло не так. Попробуйте ещё раз.')
            this.ownCities = [];
        }

        return this.ownCities;
    }
}

class Button {
    constructor(element, style_on, style_off) {
        this.button = document.getElementById(element);
        this.style_on = style_on;
        this.style_off = style_off;
    }

    get_element() {
        return this.button;
    }

    off() {
        this.button.dataset.type = 'show';
        this.button.classList.remove(this.style_on);
        this.button.classList.add(this.style_off);
    }

    on() {
        this.button.dataset.type = 'hide';
        this.button.classList.remove(this.style_off);
        this.button.classList.add(this.style_on);
    }

    disable() {
        this.button.classList.add('disabled');
    }

    enable() {
        this.button.classList.remove('disabled')
    }
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
    } else {
        return [56.831534, 50.987919, 5];
    }
}

let actions = new ToolbarActions();

async function init() {
    let ownCities = await actions.getVisitedCities();

    const [center_lat, center_lon, zoom] = calculateCenterCoordinates(ownCities);
    actions.createMap(center_lat, center_lon, zoom)

    actions.addOwnCitiesOnMap();
}

window.onload = () => {
    init();
}

// ymaps.ready(init);
