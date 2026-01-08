import {
    icon_blue_pin,
    icon_not_visited_pin,
    icon_subscription_pin,
    icon_together_pin,
    icon_visited_pin
} from "./icons.js";
import {City, MarkerStyle} from "./schemas.js";
import {open_modal_for_add_city, close_modal_for_add_city} from './services.js';
import {getCookie} from './get_cookie.js';
import {addErrorControl, addLoadControl} from "./map";

// Это нужно для того, чтобы open_modal_for_add_city можно было использовать в onclick.
// Иначе из-за специфичной области видимости доступа к этой функции нет.
window.open_modal_for_add_city = open_modal_for_add_city;
window.close_modal_for_add_city = close_modal_for_add_city;

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

        this.elementShowSubscriptionCities = document.getElementById('btn_show-subscriptions-cities');
        this.elementShowPlaces = document.getElementById('btn_show-places');
        this.elementShowNotVisitedCities = document.getElementById('btn_show-not-visited-cities');

        this.set_handlers();
    }

    set_handlers() {
        this.elementShowSubscriptionCities.addEventListener('click', () => {
            this.showSubscriptionCities();
        });


        this.elementShowPlaces.addEventListener('click', () => {
            const isActive = this.elementShowPlaces.classList.contains('bg-blue-100');
            if (isActive) {
                this.hidePlaces();
                this.setPlacesButtonActive(false);
            } else {
                this.showPlaces();
                this.setPlacesButtonActive(true);
            }
        });

        this.elementShowNotVisitedCities.addEventListener('click', () => {
            if (this.elementShowNotVisitedCities.dataset.type === 'show') {
                this.showNotVisitedCities();
                this.setButtonState(this.elementShowNotVisitedCities, true);
            } else {
                this.hideNotVisitedCities();
                this.setButtonState(this.elementShowNotVisitedCities, false);
            }
        });
    }

    setButtonState(element, isActive) {
        element.dataset.type = isActive ? 'hide' : 'show';
    }

    /**
     * Устанавливает активное состояние кнопки "Показать места" через CSS классы.
     * В активном состоянии добавляется только фон, остальные стили остаются без изменений.
     * @param {boolean} isActive - Активна ли кнопка
     */
    setPlacesButtonActive(isActive) {
        if (!this.elementShowPlaces) {
            return;
        }

        if (isActive) {
            // Активное состояние: добавляем синий фон, остальное не меняем
            this.elementShowPlaces.classList.remove('bg-white', 'hover:bg-gray-50', 'focus:bg-gray-50', 'dark:bg-neutral-800', 'dark:hover:bg-neutral-700', 'dark:focus:bg-neutral-700');
            this.elementShowPlaces.classList.add('bg-blue-100', 'hover:bg-blue-200', 'focus:bg-blue-200', 'dark:bg-blue-800/30', 'dark:hover:bg-blue-800/20', 'dark:focus:bg-blue-800/20');
        } else {
            // Неактивное состояние: возвращаем стандартный фон
            this.elementShowPlaces.classList.remove('bg-blue-100', 'hover:bg-blue-200', 'focus:bg-blue-200', 'dark:bg-blue-800/30', 'dark:hover:bg-blue-800/20', 'dark:focus:bg-blue-800/20');
            this.elementShowPlaces.classList.add('bg-white', 'hover:bg-gray-50', 'focus:bg-gray-50', 'dark:bg-neutral-800', 'dark:hover:bg-neutral-700', 'dark:focus:bg-neutral-700');
        }
    }

    disableButton(element, shouldDisable) {
        if (shouldDisable) {
            element.disabled = true;
        } else {
            element.disabled = false;
        }
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
        button.innerHTML = '<span class="animate-spin inline-block size-4 border-[3px] border-current border-t-transparent text-white rounded-full" role="status" aria-label="loading"></span><span>Загрузка...</span>';

        let response = await fetch(url.toString(), {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie("csrftoken")
            }
        });

        if (response.ok) {
            // Закрываем модальное окно (Preline UI)
            const modalElement = document.getElementById('subscriptionsModal');
            if (modalElement) {
                // Ищем кнопку закрытия и программно кликаем на неё
                const closeButton = modalElement.querySelector('[data-hs-overlay="#subscriptionsModal"]');
                if (closeButton) {
                    closeButton.click();
                } else {
                    // Если кнопка не найдена, просто скрываем модальное окно
                    modalElement.classList.add('hidden');
                    modalElement.classList.remove('open');
                }
            }

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

            // Применяем фильтр по годам, если он выбран
            const yearSelect = document.getElementById('id_year_filter');
            if (yearSelect && typeof window.filterCitiesByYear === 'function') {
                const selectedYear = yearSelect.value || '';
                const filterValue = selectedYear === 'all' ? '' : selectedYear;
                window.filterCitiesByYear(filterValue);
            }
            
            // Обновляем состояние кнопки "Показать непосещённые города"
            if (typeof window.updateNotVisitedCitiesButtonState === 'function') {
                window.updateNotVisitedCitiesButtonState();
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
        let usersWhoVisitedCity = this.getUsersWhoVisitedCity(year);

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
         * Если users не передан, получает список пользователей с учётом текущего фильтра по годам.
         *
         * Возвращает созданный маркер.
         */
        // Если users не передан, получаем список пользователей с учётом текущего фильтра по годам
        if (users === undefined) {
            const yearSelect = document.getElementById('id_year_filter');
            let selectedYear = undefined;
            if (yearSelect && yearSelect.value && yearSelect.value !== 'all') {
                selectedYear = parseInt(yearSelect.value, 10);
                if (isNaN(selectedYear)) {
                    selectedYear = undefined;
                }
            }
            const usersMap = this.getUsersWhoVisitedCity(selectedYear);
            users = usersMap.get(city.id) || [];
        }
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

        // Экранируем данные для безопасного использования в HTML
        const cityNameEscaped = city.name.replace(/'/g, "&#39;").replace(/"/g, "&quot;");
        const regionEscaped = city.region ? city.region.replace(/'/g, "&#39;").replace(/"/g, "&quot;") : '';
        
        const first_visit_date = city.first_visit_date ? new Date(city.first_visit_date).toLocaleDateString() : undefined;
        const last_visit_date = city.last_visit_date ? new Date(city.last_visit_date).toLocaleDateString() : undefined;
        const visit_years = city.visit_years ? city.visit_years : undefined;
        const number_of_visits = city.number_of_visits;

        // Получаем текущий выбранный год из фильтра для отображения в статусе
        const getSelectedYear = () => {
            const yearSelect = document.getElementById('id_year_filter');
            if (yearSelect && yearSelect.value && yearSelect.value !== 'all') {
                const year = parseInt(yearSelect.value, 10);
                if (!isNaN(year)) {
                    return year;
                }
            }
            return null;
        };

        // Вспомогательная функция для генерации контента информации о посещениях
        // Смешанный вариант: компактность и горизонтальное расположение (вариант 2) + иконки (вариант 3) + бейджики для дат (вариант 5)
        const generateVisitInfo = () => {
            let info = '';
            const selectedYear = getSelectedYear();
            const statusText = selectedYear 
                ? `Вы не были в этом городе в ${selectedYear} году`
                : 'Вы не были в этом городе';
            
            if (marker_style === MarkerStyle.SUBSCRIPTION) {
                info += `<div class="flex items-center justify-between gap-2 text-sm">`;
                info += `<div class="flex items-center gap-2">`;
                info += `<svg class="size-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>`;
                info += `<span class="text-gray-500 dark:text-neutral-400">Статус:</span>`;
                info += `</div>`;
                info += `<span class="text-gray-900 dark:text-white">${statusText}</span>`;
                info += `</div>`;
                
                info += `<div class="flex items-center justify-between gap-2 text-sm">`;
                info += `<div class="flex items-center gap-2">`;
                info += `<svg class="size-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/></svg>`;
                info += `<span class="text-gray-500 dark:text-neutral-400">Пользователи:</span>`;
                info += `</div>`;
                info += `<span class="text-gray-900 dark:text-white">${users.join(', ')}</span>`;
                info += `</div>`;
            } else if (marker_style === MarkerStyle.TOGETHER) {
                info += `<div class="flex items-center justify-between gap-2 text-sm">`;
                info += `<div class="flex items-center gap-2">`;
                info += `<svg class="size-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/></svg>`;
                info += `<span class="text-gray-500 dark:text-neutral-400">Пользователи:</span>`;
                info += `</div>`;
                info += `<span class="text-gray-900 dark:text-white">${users.join(', ')}</span>`;
                info += `</div>`;
                
                if (first_visit_date !== undefined && last_visit_date !== undefined && first_visit_date === last_visit_date) {
                    info += `<div class="flex items-center justify-between gap-2 text-sm">`;
                    info += `<div class="flex items-center gap-2">`;
                    info += `<svg class="size-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>`;
                    info += `<span class="text-gray-500 dark:text-neutral-400">Дата посещения:</span>`;
                    info += `</div>`;
                    info += `<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-500/10 dark:text-blue-400">${first_visit_date || 'Не указана'}</span>`;
                    info += `</div>`;
                } else if (first_visit_date !== undefined && last_visit_date !== undefined && first_visit_date !== last_visit_date) {
                    info += `<div class="flex items-center justify-between gap-2 text-sm">`;
                    info += `<div class="flex items-center gap-2">`;
                    info += `<svg class="size-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>`;
                    info += `<span class="text-gray-500 dark:text-neutral-400">Первое посещение:</span>`;
                    info += `</div>`;
                    info += `<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-500/10 dark:text-blue-400">${first_visit_date || 'Не указана'}</span>`;
                    info += `</div>`;
                    info += `<div class="flex items-center justify-between gap-2 text-sm">`;
                    info += `<div class="flex items-center gap-2">`;
                    info += `<svg class="size-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>`;
                    info += `<span class="text-gray-500 dark:text-neutral-400">Последнее посещение:</span>`;
                    info += `</div>`;
                    info += `<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-100 text-emerald-800 dark:bg-emerald-500/10 dark:text-emerald-400">${last_visit_date || 'Не указана'}</span>`;
                    info += `</div>`;
                }
                
                info += `<div class="flex items-center justify-between gap-2 text-sm">`;
                info += `<div class="flex items-center gap-2">`;
                info += `<svg class="size-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg>`;
                info += `<span class="text-gray-500 dark:text-neutral-400">Всего посещений:</span>`;
                info += `</div>`;
                info += `<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-500/10 dark:text-purple-400">${number_of_visits}</span>`;
                info += `</div>`;
            } else if (marker_style === MarkerStyle.NOT_VISITED) {
                const selectedYear = getSelectedYear();
                const statusText = selectedYear 
                    ? `Вы не были в этом городе в ${selectedYear} году`
                    : 'Вы не были в этом городе';
                info += `<div class="flex items-center justify-between gap-2 text-sm">`;
                info += `<div class="flex items-center gap-2">`;
                info += `<svg class="size-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>`;
                info += `<span class="text-gray-500 dark:text-neutral-400">Статус:</span>`;
                info += `</div>`;
                info += `<span class="text-gray-900 dark:text-white">${statusText}</span>`;
                info += `</div>`;
            } else {
                if (first_visit_date !== undefined && last_visit_date !== undefined && first_visit_date === last_visit_date) {
                    info += `<div class="flex items-center justify-between gap-2 text-sm">`;
                    info += `<div class="flex items-center gap-2">`;
                    info += `<svg class="size-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>`;
                    info += `<span class="text-gray-500 dark:text-neutral-400">Дата посещения:</span>`;
                    info += `</div>`;
                    info += `<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-500/10 dark:text-blue-400">${first_visit_date || 'Не указана'}</span>`;
                    info += `</div>`;
                } else if (first_visit_date !== undefined && last_visit_date !== undefined && first_visit_date !== last_visit_date) {
                    info += `<div class="flex items-center justify-between gap-2 text-sm">`;
                    info += `<div class="flex items-center gap-2">`;
                    info += `<svg class="size-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>`;
                    info += `<span class="text-gray-500 dark:text-neutral-400">Первое посещение:</span>`;
                    info += `</div>`;
                    info += `<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-500/10 dark:text-blue-400">${first_visit_date || 'Не указана'}</span>`;
                    info += `</div>`;
                    info += `<div class="flex items-center justify-between gap-2 text-sm">`;
                    info += `<div class="flex items-center gap-2">`;
                    info += `<svg class="size-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>`;
                    info += `<span class="text-gray-500 dark:text-neutral-400">Последнее посещение:</span>`;
                    info += `</div>`;
                    info += `<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-100 text-emerald-800 dark:bg-emerald-500/10 dark:text-emerald-400">${last_visit_date || 'Не указана'}</span>`;
                    info += `</div>`;
                }
                
                info += `<div class="flex items-center justify-between gap-2 text-sm">`;
                info += `<div class="flex items-center gap-2">`;
                info += `<svg class="size-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg>`;
                info += `<span class="text-gray-500 dark:text-neutral-400">Всего посещений:</span>`;
                info += `</div>`;
                info += `<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-500/10 dark:text-purple-400">${number_of_visits}</span>`;
                info += `</div>`;
            }
            return info;
        };

        // Генерируем ссылку действия
        const generateActionLink = () => {
            if (marker_style === MarkerStyle.SUBSCRIPTION || marker_style === MarkerStyle.NOT_VISITED) {
                return `<a href="#" 
                    class="text-sm text-emerald-600 hover:text-emerald-700 dark:text-emerald-400 dark:hover:text-emerald-300 transition-colors"
                    data-hs-overlay="#addCityModal" 
                    data-city-name="${cityNameEscaped}" 
                    data-city-id="${city.id}" 
                    data-city-region="${regionEscaped}">Отметить как посещённый</a>`;
            } else {
                return `<a href="#" 
                    class="text-sm text-emerald-600 hover:text-emerald-700 dark:text-emerald-400 dark:hover:text-emerald-300 transition-colors"
                    data-hs-overlay="#addCityModal" 
                    data-city-name="${cityNameEscaped}" 
                    data-city-id="${city.id}" 
                    data-city-region="${regionEscaped}">Добавить ещё одно посещение</a>`;
            }
        };

        let content = '<div class="px-1.5 py-1.5 min-w-[280px] max-w-[400px]">';
        
        // Заголовок (стиль варианта 2 - компактный, без серого блока)
        content += `<div class="mb-2 pb-1 border-b border-gray-200 dark:border-neutral-700">`;
        content += `<h3 class="text-base font-semibold text-gray-900 dark:text-white mb-0">`;
        content += `<a href="/city/${city.id}" target="_blank" rel="noopener noreferrer" class="text-gray-900 hover:text-blue-600 dark:text-white dark:hover:text-blue-400 transition-colors">${city.name}</a>`;
        content += `</h3>`;
        content += `<div class="text-xs text-gray-600 dark:text-neutral-400 mt-2">`;
        if (city.region) {
            content += `${city.region}, ${city.country}`;
        } else {
            content += `${city.country}`;
        }
        content += `</div>`;
        content += `</div>`;
        
        // Информация о посещениях (смешанный вариант: компактность + иконки + бейджики)
        content += '<div class="space-y-1.5 text-sm">';
        content += generateVisitInfo();
        content += '</div>';
        
        // Ссылки действий
        content += '<div class="mt-2 pt-2 border-t border-gray-200 dark:border-neutral-700">';
        content += generateActionLink();
        content += '</div>';
        
        content += '</div>'; // закрываем основной контейнер
        
        marker.bindPopup(content, {maxWidth: 400, minWidth: 280});
        
        // Инициализируем Preline UI для ссылок в popup после его открытия
        marker.on('popupopen', function() {
            // Инициализируем Preline UI для динамически созданных элементов
            if (window.HSStaticMethods && typeof window.HSStaticMethods.autoInit === 'function') {
                window.HSStaticMethods.autoInit();
            }
        });

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
            // Удаляем метку непосещённого города на карте и в глобальном состоянии
            let oldMarker = this.stateNotVisitedCities.get(id);
            this.stateNotVisitedCities.delete(id);
            this.myMap.removeLayer(oldMarker);

            // Добавляем новый маркер посещённого города на карту
            // Не используем старый маркер, создаём новый с правильным стилем
            const newMarker = this.addMarkerToMap(city, MarkerStyle.OWN);
            this.stateOwnCities.set(id, newMarker);
        } else if (this.stateSubscriptionCities.has(id)) {
            // Удаляем старую метку на карте и в глобальном состоянии
            let old_marker = this.stateSubscriptionCities.get(id);
            this.stateSubscriptionCities.delete(id);
            this.myMap.removeLayer(old_marker);

            // Добавляем новую метку на карту
            this.ownCities.push(city);
            // Получаем текущий выбранный год из фильтра
            const yearSelect = document.getElementById('id_year_filter');
            let selectedYear = undefined;
            if (yearSelect && yearSelect.value && yearSelect.value !== 'all') {
                selectedYear = parseInt(yearSelect.value, 10);
                if (isNaN(selectedYear)) {
                    selectedYear = undefined;
                }
            }
            let usersWhoVisitedCity = this.getUsersWhoVisitedCity(selectedYear);
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

    getUsersWhoVisitedCity(year) {
        /**
         * Возвращает Map, где ключ - ID города, значение - массив имён пользователей, которые посещали город.
         * Если указан year, возвращаются только те пользователи, которые посещали город в указанном году.
         * @param {number|undefined} year - Год для фильтрации (опционально)
         * @returns {Map<number, string[]>}
         */
        let usersWhoVisitedCity = new Map();

        // Получаем данные о своих городах для проверки, посещал ли пользователь город в выбранном году
        const ownCitiesMap = new Map();
        if (this.ownCities) {
            this.ownCities.forEach((city) => {
                ownCitiesMap.set(city.id, city);
            });
        }

        for (let i = 0; i < (this.subscriptionCities.length); i++) {
            let city = this.subscriptionCities[i];
            
            // Если указан год, проверяем, был ли этот город посещён в указанном году
            if (year !== undefined) {
                const cityVisitYears = city.visit_years || [];
                if (!cityVisitYears.includes(year)) {
                    continue; // Пропускаем, если город не был посещён в указанном году
                }
            }

            if (!usersWhoVisitedCity.has(city.id)) {
                usersWhoVisitedCity.set(city.id, []);
                
                // Добавляем "Вы" если пользователь посещал город
                // Если год указан, проверяем по visit_years, иначе просто проверяем наличие города в ownCities
                const ownCityData = ownCitiesMap.get(city.id);
                if (ownCityData) {
                    if (year !== undefined) {
                        // Если год указан, проверяем, был ли город посещён в этом году
                        if (ownCityData.visit_years && ownCityData.visit_years.includes(year)) {
                            usersWhoVisitedCity.get(city.id).push('Вы');
                        }
                    } else {
                        // Если год не указан, добавляем "Вы" если город есть в ownCities
                        usersWhoVisitedCity.get(city.id).push('Вы');
                    }
                }
            }
            usersWhoVisitedCity.get(city.id).push(city.username);
        }

        return usersWhoVisitedCity
    }
}
