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

        /**
         * Содержит типы отметок, которые можно использовать на карте.
         * Полный список отметок, поддерживаемях API Яндекс.карт находится по ссылке
         * https://yandex.ru/dev/jsapi-v2-1/doc/ru/v2-1/ref/reference/option.presetStorage
         */
        this.PlacemarkStyle = {
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
            this.removeOwnPlacemarks();
            this.removeSubscriptionPlacemarks();
            this.removeNotVisitedPlacemarks();
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

        this.removeOwnPlacemarks();
        this.removeSubscriptionPlacemarks();
        this.removeNotVisitedPlacemarks();
        this.stateOwnCities.clear();
        this.stateSubscriptionCities.clear();

        this.addOwnCitiesOnMap(new Date().getFullYear() - 1);
        this.addSubscriptionsCitiesOnMap(new Date().getFullYear() - 1);
    }

    showVisitedCitiesCurrentYear() {
        const btn = document.getElementById('btn_show-visited-cities-previous-year');

        this.removeOwnPlacemarks();
        this.removeSubscriptionPlacemarks();
        this.removeNotVisitedPlacemarks();
        this.stateOwnCities.clear();
        this.stateSubscriptionCities.clear();

        this.addOwnCitiesOnMap(new Date().getFullYear());
        this.addSubscriptionsCitiesOnMap(new Date().getFullYear());
    }

    hideVisitedCitiesPreviousYear() {
        const btn = document.getElementById('btn_show-visited-cities-previous-year');

        this.removeOwnPlacemarks();
        this.removeSubscriptionPlacemarks();
        this.removeNotVisitedPlacemarks();
        this.stateOwnCities.clear();
        this.stateSubscriptionCities.clear();

        this.addOwnCitiesOnMap();
        this.addSubscriptionsCitiesOnMap();
    }

    hideVisitedCitiesCurrentYear() {
        const btn = document.getElementById('btn_show-visited-cities-previous-year');

        this.removeOwnPlacemarks();
        this.removeSubscriptionPlacemarks();
        this.removeNotVisitedPlacemarks();
        this.stateOwnCities.clear();
        this.stateSubscriptionCities.clear();

        this.addOwnCitiesOnMap();
        this.addSubscriptionsCitiesOnMap();
    }

    hideNotVisitedCities() {
        this.removeNotVisitedPlacemarks();
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
            let placemark;
            let placemarkStyle;
            let id = this.subscriptionCities[i].id;
            let city = this.subscriptionCities[i].title;
            let region_title = this.subscriptionCities[i].region_title;
            let lat = this.subscriptionCities[i].lat;
            let lon = this.subscriptionCities[i].lon;
            let year_city = this.subscriptionCities[i].year;

            if (year !== undefined && year !== year_city) {
                continue;
            }
            if (this.stateSubscriptionCities.has(id)) {
                continue;
            }

            if (this.stateOwnCities.has(id)) {
                this.myMap.geoObjects.remove(this.stateOwnCities.get(id));
                placemarkStyle = this.PlacemarkStyle.TOGETHER
            } else {
                placemarkStyle = this.PlacemarkStyle.SUBSCRIPTION;
            }
            placemark = this.addPlacemarkToMap(
                city,
                id,
                region_title,
                lat,
                lon,
                placemarkStyle,
                usersWhoVisitedCity.get(id)
            );
            this.stateSubscriptionCities.set(id, placemark);
        }
    }

    addOwnCitiesOnMap(year) {
        /**
         * Помещает на карту отметку посещённого города и сохраняет объект Placemark в глобальный словарь stateOwnCities.
         * @param year Необязательный параметр, уазывающий за какой год нужно добавлять города на карту
         */
        for (let i = 0; i < (this.ownCities.length); i++) {
            let id = this.ownCities[i].id;
            let city = this.ownCities[i].title;
            let region_title = this.ownCities[i].region_title;
            let lat = this.ownCities[i].lat;
            let lon = this.ownCities[i].lon;
            let year_city = this.ownCities[i].year;

            if (year !== undefined && year !== year_city) {
                continue;
            }

            let placemark = this.addPlacemarkToMap(city, id, region_title, lat, lon, this.PlacemarkStyle.OWN);
            this.stateOwnCities.set(id, placemark);
        }
    }

    addNotVisitedCitiesOnMap() {
        /**
         * Помещает на карту города, которые не были посещены ни пользователем, ни адресантом подписки.
         */
        for (let i = 0; i < (this.notVisitedCities.length); i++) {
            let placemark;
            let id = this.notVisitedCities[i].id;
            let city = this.notVisitedCities[i].title;
            let region_title = this.notVisitedCities[i].region_title;
            let lat = this.notVisitedCities[i].lat;
            let lon = this.notVisitedCities[i].lon;

            if (!this.stateOwnCities.has(id) && !this.stateSubscriptionCities.has(id)) {
                placemark = this.addPlacemarkToMap(city, id, region_title, lat, lon, this.PlacemarkStyle.NOT_VISITED);
                this.stateNotVisitedCities.set(id, placemark);
            }
        }
    }

    addPlacemarkToMap(city, city_id, region_title, lat, lon, placemarkStyle, users) {
        /**
         * Добавляет на карту this.myMap отметку города 'city' по координатам 'lat' и 'lon'.
         * Создаёт балун, открывающийся по нажатию на метку, в котором содержится
         * информация о городе и регионе, кто его уже посетил, а также
         * ссылка для того, чтобы отметить город как посещённый.
         *
         * Возвращает созданный объект типа Placemark.
         */
        let contentHeader =
            '<span class="fw-semibold">' + city + '</span>, ' +
            '<small class="text-secondary fw-medium">' + region_title + '</small>';
        let linkToAdd = `<a href="#" onclick="open_modal_for_add_city('${city}', '${city_id}', '${region_title}')">Отметить как посещённый</a>`
        let content = "";
        if (placemarkStyle === this.PlacemarkStyle.SUBSCRIPTION) {
            content = `Пользователи, посетившие город:<br> ${users.join(', ')}<hr>${linkToAdd}`;
        } else if (placemarkStyle === this.PlacemarkStyle.TOGETHER) {
            content = `Пользователи, посетившие город:<br> ${users.join(', ')}`;
        } else if (placemarkStyle === this.PlacemarkStyle.NOT_VISITED) {
            content = `Этот город не был посещён ни Вами, ни кем-то из выбранный пользователей<hr>${linkToAdd}`;
        } else {
            content = "Этот город был посещён только Вами";
        }

        let placemark = new ymaps.Placemark(
            [lat, lon],
            {
                balloonContentHeader: contentHeader,
                balloonContent: content
            }, {
                preset: placemarkStyle.preset,
                zIndex: placemarkStyle.zIndex
            }
        );
        this.myMap.geoObjects.add(placemark);

        return placemark;
    }

    updatePlacemark(id) {
        if (this.stateNotVisitedCities.has(id)) {
            // Получаем данные города и удаляем его из списка непосещённых
            let city = [];
            for (let i = this.notVisitedCities.length - 1; i >= 0; i--) {
                if (this.notVisitedCities[i].id === id) {
                    city = this.notVisitedCities[i];
                    this.notVisitedCities.splice(i, 1);
                    break;
                }
            }

            // Удаляем метку на карте и в глобальном состоянии
            let placemark = this.stateNotVisitedCities.get(id);
            this.stateNotVisitedCities.delete(id);
            this.myMap.geoObjects.remove(placemark);

            // Добавляем новую метку на карту
            this.ownCities.push(city);
            this.stateOwnCities.set(id, placemark);
            this.addPlacemarkToMap(
                city.title,
                city.id,
                city.region_title,
                city.lat,
                city.lon,
                this.PlacemarkStyle.OWN
            );
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
            let old_placemark = this.stateSubscriptionCities.get(id);
            this.stateSubscriptionCities.delete(id);
            this.myMap.geoObjects.remove(old_placemark);

            // Добавляем новую метку на карту
            this.ownCities.push(city);
            // this.stateOwnCities.set(id, placemark);
            let usersWhoVisitedCity = this.getUsersWhoVisitedCity();
            let new_placemark = this.addPlacemarkToMap(
                city.title,
                city.id,
                city.region_title,
                city.lat,
                city.lon,
                this.PlacemarkStyle.TOGETHER,
                usersWhoVisitedCity.get(id)
            );
            this.stateSubscriptionCities.set(id, new_placemark);
        } else {
            throw new Error(`Неизвестное состояние добавленного города с ID ${id}`);
        }
    }

    removeOwnPlacemarks() {
        for (let [id, placemark] of this.stateOwnCities.entries()) {
            this.myMap.geoObjects.remove(placemark);
        }
    }

    removeSubscriptionPlacemarks() {
        for (let [id, placemark] of this.stateSubscriptionCities.entries()) {
            this.myMap.geoObjects.remove(placemark);
        }
    }

    removeNotVisitedPlacemarks() {
        for (let [id, placemark] of this.stateNotVisitedCities.entries()) {
            this.myMap.geoObjects.remove(placemark);
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
        this.myMap = new ymaps.Map("map", {
            center: [center_lat, center_lon],
            zoom: zoom,
            controls: ['fullscreenControl', 'zoomControl', 'rulerControl']
        }, {
            searchControlProvider: 'yandex#search'
        });
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

ymaps.ready(init);
