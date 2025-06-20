import {
    icon_blue_pin,
    icon_not_visited_pin,
    icon_subscription_pin,
    icon_together_pin,
    icon_visited_pin
} from "./icons.js";
import {City, MarkerStyle} from "./schemas.js";
import {open_modal_for_add_city} from './services.js';
import {Button} from './button.js';
import {getCookie} from './get_cookie.js';
import {addErrorControl, addLoadControl} from "./map";

// Это нужно для того, чтобы open_modal_for_add_city можно было использовать в onclick.
// Иначе из-за специфичной области видимости доступа к этой функции нет.
window.open_modal_for_add_city = open_modal_for_add_city;

export class ToolbarActions {
    constructor(map, own_cities) {
        this.myMap = map;
        // Массив, содержащий в себе ID городов, посещённых пользователем.
        // Этот массив может быть использован для перерисовки карты, повторно с сервера он никогда не запрашивается.
        // Единственный момент, когда он может быть изменён - это добавление посещённого города с карты.
        // В этот момент город удаляется из this.notVisitedCities и помещается в this.ownCities.
        this.ownCities = own_cities;

        // Массив, содержащий в себе ID городов, посещённых пользователями, на которых произведена подписка.
        // Этот массив обновляется каждый раз при отображении городов пользователей, на которых произведена подписка.
        this.subscriptionCities = [];

        // Массив, содержащий в себе ID городов, не посещённых пользователем.
        // Этот массив всегда существует без изменений и может быть использован для перерисовки карты.
        this.notVisitedCities = [];

        // Словарь, хранящий в себе все маркеры с посещёнными городами, отображаемые в данный момент на карте
        this.stateOwnCities = new Map();

        // Словарь, хранящий в себе все маркеры с городами пользователей, на которых оформлена подписка,
        // отображаемые в данный момент на карте
        this.stateSubscriptionCities = new Map();

        // Словарь, хранящий в себе все маркеры с непосещёнными городами пользователей, отображаемые в данный момент на карте
        this.stateNotVisitedCities = new Map();

        // Массив, хранящий в себе все маркеры посещённых мест
        this.allPlaceMarkers = [];

        // Ниже определяются кнопки. Для каждой из них есть 2 переменные:
        // - btn... - экземпляр класса Button для доступа к его методам.
        // - element... - Непосредственно сам HTML-элемент, чтобы иметь доступ к его параметрам.
        this.btnShowSubscriptionCities = new Button(
            'btn_show-subscriptions-cities',
            'btn-success',
            'btn-outline-success'
        )
        this.elementShowSubscriptionCities = this.btnShowSubscriptionCities.get_element();

        this.btnShowPlaces = new Button(
            'btn_show-places',
            'btn-primary',
            'btn-outline-primary'
        );
        this.elementShowPlaces = this.btnShowPlaces.get_element();

        this.btnShowNotVisitedCities = new Button(
            'btn_show-not-visited-cities',
            'btn-danger',
            'btn-outline-danger'
        )
        this.elementShowNotVisitedCities = this.btnShowNotVisitedCities.get_element();

        this.btnShowVisitedCitiesPreviousYear = new Button(
            'btn_show-visited-cities-previous-year',
            'btn-primary',
            'btn-outline-primary'
        )
        this.elementShowVisitedCitiesPreviousYear = this.btnShowVisitedCitiesPreviousYear.get_element();

        this.btnShowVisitedCitiesCurrentYear = new Button(
            'btn_show-visited-cities-current-year',
            'btn-success',
            'btn-outline-success'
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

        this.elementShowPlaces.addEventListener('click', () => {
            if (this.elementShowPlaces.dataset.type === 'show') {
                this.showPlaces();
                this.btnShowPlaces.on();
            } else {
                this.hidePlaces();
                this.btnShowPlaces.off();
            }
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
        const urlParams = new URLSearchParams(window.location.search);
        const selectedCountryCode = urlParams.get('country');

        const url = new URL(this.elementShowSubscriptionCities.dataset.url, window.location.origin);
        if (selectedCountryCode !== undefined && selectedCountryCode !== null) {
            url.searchParams.set('country', selectedCountryCode);
        }

        // Добавляем в URL повторяющийся параметр user_ids
        let selectedCheckboxes = document.querySelectorAll('input.checkbox_username:checked');
        let checkedValues = Array.from(selectedCheckboxes).map(cb => Number(cb.value));
        checkedValues.forEach(id => url.searchParams.append('user_ids', id));

        let button = document.getElementById('btn_show-subscriptions-cities');
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm" aria-hidden="true"></span>&nbsp;&nbsp;&nbsp;<span role="status">Загрузка...</span>';

        let response = await fetch(url.toString(), {
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
        const load = addLoadControl(this.myMap, 'Загружаю непосещённые города...');

        const url = this.elementShowNotVisitedCities.dataset.url;

        if (this.notVisitedCities.length === 0) {
            try {
                let response = await fetch(url, {
                    method: 'GET',
                    headers: {
                        'X-CSRFToken': getCookie("csrftoken")
                    }
                });

                if (response.ok) {
                    this.notVisitedCities = await response.json();
                    this.addNotVisitedCitiesOnMap();
                    this.myMap.removeControl(load);
                } else {
                    this.myMap.removeControl(load);
                    addErrorControl(this.myMap, 'Произошла ошибка при загрузке непосещённых городов');
                    return false;
                }
            } catch (error) {
                console.error("Ошибка при выполнении запроса:", error);
                this.myMap.removeControl(load);
                addErrorControl(this.myMap, 'Произошла ошибка при загрузке непосещённых городов');
                return false;
            }
        } else {
            this.addNotVisitedCitiesOnMap();
            this.myMap.removeControl(load);
        }
    }

    showPlaces() {
        if (this.allPlaceMarkers.length > 0) {
            this.allPlaceMarkers.forEach(marker => {
                marker.addTo(this.myMap);
            });
        } else {
            fetch('/api/place/')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Произошла ошибка при получении данных с сервера');
                    }
                    return response.json();
                })
                .then(places => {
                    places.forEach(place => {
                        const marker = L.marker(
                            [place.latitude, place.longitude],
                            {
                                icon: icon_blue_pin
                            }).addTo(this.myMap);
                        marker.bindTooltip(place.name, {direction: 'top'});
                        marker.setZIndexOffset(50000);

                        this.allPlaceMarkers.push(marker);
                    });
                });
        }
    }

    hidePlaces() {
        this.allPlaceMarkers.forEach(marker => {
            this.myMap.removeLayer(marker);
        });
    }

    showVisitedCitiesPreviousYear() {
        this.removeOwnMarkers();
        this.removeSubscriptionMarkers();
        this.removeNotVisitedMarkers();
        this.stateOwnCities.clear();
        this.stateSubscriptionCities.clear();

        this.addOwnCitiesOnMap(new Date().getFullYear() - 1);
        this.addSubscriptionsCitiesOnMap(new Date().getFullYear() - 1);
    }

    showVisitedCitiesCurrentYear() {
        this.removeOwnMarkers();
        this.removeSubscriptionMarkers();
        this.removeNotVisitedMarkers();
        this.stateOwnCities.clear();
        this.stateSubscriptionCities.clear();

        this.addOwnCitiesOnMap(new Date().getFullYear());
        this.addSubscriptionsCitiesOnMap(new Date().getFullYear());
    }

    hideVisitedCitiesPreviousYear() {
        this.removeOwnMarkers();
        this.removeSubscriptionMarkers();
        this.removeNotVisitedMarkers();
        this.stateOwnCities.clear();
        this.stateSubscriptionCities.clear();

        this.addOwnCitiesOnMap();
        this.addSubscriptionsCitiesOnMap();
    }

    hideVisitedCitiesCurrentYear() {
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
         * и сохраняет объект Marker в глобальный словарь stateSubscriptionCities.
         * В случае, если город был посещён и пользователем, и адресантом подписки, то соответствующая Marker
         * удаляется из stateOwnCities и помещается в stateSubscriptionCities.
         * @param year Необязательный параметр, указывающий за какой год нужно добавлять города на карту
         */
        let usersWhoVisitedCity = this.getUsersWhoVisitedCity();

        // Объект, содержащий даты посещения городов пользователя, который просматривает страницу.
        // Нужен для того, чтобы в балун вставлять корректные даты, а не даты посещения того, на кого подписан.
        const ownCities = this.ownCities.reduce((acc, { title, first_visit_date, last_visit_date, visit_years }) => {
            acc[title] = {
                visit_years,
                first_visit_date,
                last_visit_date
            };
            return acc;
        }, {});

        for (let i = 0; i < this.subscriptionCities.length; i++) {
            const city = new City();

            city.id = this.subscriptionCities[i].id;
            city.name = this.subscriptionCities[i].title;
            city.region = this.subscriptionCities[i].region_title;
            city.country = this.subscriptionCities[i].country;
            city.lat = this.subscriptionCities[i].lat;
            city.lon = this.subscriptionCities[i].lon;
            city.visit_years = ownCities[city.name] ? ownCities[city.name].visit_years : undefined;
            city.first_visit_date = ownCities[city.name] ? ownCities[city.name].first_visit_date : undefined;
            city.last_visit_date = ownCities[city.name] ? ownCities[city.name].last_visit_date : undefined;

            // ToDo: очень неэффективно - на каждый город подписчика проходимся по всем моим городам
            this.ownCities.forEach(own_city => {
                if (city.id === own_city.id) {
                    city.date_of_first_visit = own_city.date_of_first_visit;
                    city.number_of_visits = own_city.number_of_visits;
                }
            });

            if (year !== undefined && (!this.subscriptionCities[i].visit_years || !this.subscriptionCities[i].visit_years.includes(year))) {
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
        const allMarkers = [];

        for (let i = 0; i < (this.ownCities.length); i++) {
            const city = new City();

            city.id = this.ownCities[i].id;
            city.name = this.ownCities[i].title;
            city.region = this.ownCities[i].region_title;
            city.country = this.ownCities[i].country;
            city.lat = this.ownCities[i].lat;
            city.lon = this.ownCities[i].lon;
            city.visit_years = this.ownCities[i].visit_years;
            city.first_visit_date = this.ownCities[i].first_visit_date;
            city.last_visit_date = this.ownCities[i].last_visit_date;
            city.number_of_visits = this.ownCities[i].number_of_visits;

            // Если указан год, то добавляем на карту только города, которые были посещены в указанном году
            if (year !== undefined && (!city.visit_years || !city.visit_years.includes(year))) {
                continue;
            }

            let marker = this.addMarkerToMap(city, MarkerStyle.OWN);
            allMarkers.push(marker);
            this.stateOwnCities.set(city.id, marker);
        }

        return allMarkers;
    }

    /**
     * Помещает на карту города, которые не были посещены ни пользователем, ни адресантом подписки.
     */
    addNotVisitedCitiesOnMap() {
        for (let i = 0; i < (this.notVisitedCities.length); i++) {
            const city = new City();
            city.id = this.notVisitedCities[i].id;
            city.name = this.notVisitedCities[i].title;
            city.region = this.notVisitedCities[i].region;
            city.country = this.notVisitedCities[i].country;
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
        let zIndexOffset;

        switch (marker_style) {
            case MarkerStyle.OWN:
                icon = icon_visited_pin;
                zIndexOffset = 40000;
                break;
            case MarkerStyle.NOT_VISITED:
                icon = icon_not_visited_pin;
                zIndexOffset = 0;
                break;
            case MarkerStyle.SUBSCRIPTION:
                icon = icon_subscription_pin;
                zIndexOffset = 20000;
                break;
            case MarkerStyle.TOGETHER:
                icon = icon_together_pin;
                zIndexOffset = 30000;
                break;
        }
        const marker = L.marker([city.lat, city.lon], {icon: icon}).addTo(this.myMap);
        marker.setZIndexOffset(zIndexOffset);

        let content = '';

        // Название города
        content += `<div><span class="fw-semibold fs-3"><a href="/city/${city.id}" target="_blank" rel="noopener noreferrer" class="link-offset-2 link-underline-dark link-dark link-underline-opacity-50-hover link-opacity-50-hover">${city.name}</a></span></div>`;

        // Название региона и страны
        if (city.region) {
            content += `<div class="mt-2"><small class="text-secondary fw-medium fs-6">${city.region}, ${city.country}</small></div>`;
        } else {
            content += `<div class="mt-2"><small class="text-secondary fw-medium fs-6">${city.country}</small></div>`;
        }

        let linkToAdd = `<a href="#" onclick="open_modal_for_add_city('${city.name}', '${city.id}', '${city.region}')">Отметить как посещённый</a>`
        let linkToAddAgain = `<a href="#" onclick="open_modal_for_add_city('${city.name}', '${city.id}', '${city.region}')">Добавить ещё одно посещение</a>`
        const first_visit_date = city.first_visit_date ? new Date(city.first_visit_date).toLocaleDateString() : undefined;
        const last_visit_date = city.last_visit_date ? new Date(city.last_visit_date).toLocaleDateString() : undefined;
        const visit_years = city.visit_years ? city.visit_years : undefined;
        const number_of_visits = city.number_of_visits;

        if (marker_style === MarkerStyle.SUBSCRIPTION) {
            content += '<p>Вы не были в этом городе</p>';
            content += `<p>Пользователи, посетившие город:<br> ${users.join(', ')}</p><hr>${linkToAdd}`;
        } else if (marker_style === MarkerStyle.TOGETHER) {
            content += `<p>Пользователи, посетившие город:<br> ${users.join(', ')}</p>`;
            if (first_visit_date !== undefined && last_visit_date !== undefined && first_visit_date === last_visit_date) {
                content += `<p><span class='fw-semibold'>Дата посещения:</span> ${first_visit_date ? first_visit_date : 'Не указана'}</p>`
            } else if (first_visit_date !== undefined && last_visit_date !== undefined && first_visit_date !== last_visit_date) {
                content += `<p><span class='fw-semibold'>Дата первого посещения:</span> ${first_visit_date ? first_visit_date : 'Не указана'}</p>`
                content += `<p><span class='fw-semibold'>Дата последнего посещения:</span> ${last_visit_date ? last_visit_date : 'Не указана'}</p>`
            }
            content += `<p><span class='fw-semibold'>Всего посещений: ${number_of_visits}</span></p><hr>${linkToAddAgain}`;
        } else if (marker_style === MarkerStyle.NOT_VISITED) {
            content += `<p>Вы не были в этом городе</p><hr>${linkToAdd}`;
        } else {
            if (first_visit_date !== undefined && last_visit_date !== undefined && first_visit_date === last_visit_date) {
                content += `<p><span class='fw-semibold'>Дата посещения:</span> ${first_visit_date ? first_visit_date : 'Не указана'}</p>`
            } else if (first_visit_date !== undefined && last_visit_date !== undefined && first_visit_date !== last_visit_date) {
                content += `<p><span class='fw-semibold'>Дата первого посещения:</span> ${first_visit_date ? first_visit_date : 'Не указана'}</p>`
                content += `<p><span class='fw-semibold'>Дата последнего посещения:</span> ${last_visit_date ? last_visit_date : 'Не указана'}</p>`
            }
            content += `<p><span class='fw-semibold'>Всего посещений:</span> ${number_of_visits}</p><hr>${linkToAddAgain}`;
        }
        marker.bindPopup(content);

        marker.bindTooltip(city.name, {
            direction: 'top'
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

    updateMarker(city) {
        const id = city.id;

        if (this.stateNotVisitedCities.has(id)) {
            // Удаляем метку на карте и в глобальном состоянии
            let marker = this.stateNotVisitedCities.get(id);
            this.stateNotVisitedCities.delete(id);
            this.myMap.removeLayer(marker);

            // Добавляем новую метку на карту
            this.ownCities.push(city);
            this.stateOwnCities.set(id, marker);
            this.addMarkerToMap(city, MarkerStyle.OWN);
        } else if (this.stateSubscriptionCities.has(id)) {
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
        } else if (this.stateOwnCities.has(id)) {
            // Удаление старого маркера
            let old_marker = this.stateOwnCities.get(city.id);
            this.stateOwnCities.delete(city.id);
            this.myMap.removeLayer(old_marker);

            // Обновление информации о городе в this.ownCities
            for (let i = 0; i < this.ownCities.length; i++) {
                if (this.ownCities[i].id === id) {
                    this.ownCities[i].number_of_visits = city.number_of_visits;
                    this.ownCities[i].first_visit_date = city.first_visit_date;
                    this.ownCities[i].last_visit_date = city.last_visit_date;
                    this.ownCities[i].visit_dates = city.visit_dates;
                    break;
                }
            }

            // Создание нового маркета
            const new_marker = this.addMarkerToMap(city, MarkerStyle.OWN);
            this.stateOwnCities.set(id, new_marker);
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
}
