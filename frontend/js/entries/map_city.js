/**
 * Реализует отображение карты и меток на ней, запрос посещённых
 * и не посещённых городов с сервера и обновление меток на карте.
 *
 * ----------------------------------------------
 *
 * Copyright © Egor Vavilov (Shecspi)
 * Licensed under the Apache License, Version 2.0
 *
 * ----------------------------------------------
 */
import L from 'leaflet';

import {addExternalBorderControl, addInternalBorderControl, create_map} from "../components/map.js";
import {ToolbarActions} from "../components/toolbar_actions.js";
import {City} from "../components/schemas.js";
import {change_qty_of_visited_cities_in_toolbar, modal} from '../components/services.js';
import {showDangerToast, showSuccessToast} from "../components/toast.js";
import {getCookie} from '../components/get_cookie.js';
import {initCountrySelect} from "../components/initCountrySelect";

let actions;
let map;

const urlParams = new URLSearchParams(window.location.search);
const selectedCountryCode = urlParams.get('country');

window.onload = async () => {
    map = create_map();
    addExternalBorderControl(map, selectedCountryCode);
    addInternalBorderControl(map, selectedCountryCode);

    getVisitedCities()
        .then(own_cities => {
                actions = new ToolbarActions(map, own_cities);

                if (own_cities.length === 0) {
                    map.setView([55.7522, 37.6156], 6);

                    const btn = document.getElementById('btn_show-not-visited-cities');
                    if (!btn) {
                        console.error('Кнопка не найдена!');
                    } else if (own_cities.length === 0) {
                        btn.click();
                        const checkInterval = setInterval(() => {
                          if (actions.stateNotVisitedCities.size > 0) {
                            const group = new L.featureGroup(Array.from(actions.stateNotVisitedCities.values()));
                            map.fitBounds(group.getBounds());
                            clearInterval(checkInterval);
                          }
                        }, 200); // проверяем каждые 200 мс
                    }
                } else {
                    const allMarkers = actions.addOwnCitiesOnMap();
                    const group = new L.featureGroup([...allMarkers]);
                    map.fitBounds(group.getBounds());
                }
            }
        )
    await initCountrySelect();
}

/**
 * Делает запрос на сервер и возвращает список городов, посещённых пользователем.
 */
async function getVisitedCities() {
    let baseUrl = window.URL_GET_VISITED_CITIES;
    let queryParams = window.location.search;

    let url = baseUrl + queryParams;

    return fetch(url, {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCookie("csrftoken")
        }
    })
        .then(response => {
            return response.json();
        })
        .then(data => {
            return data;
        });
}

// -------------------------------------------------- //
//                                                    //
// Обработчик отправки формы добавления нового города //
//                                                    //
// -------------------------------------------------- //
const form = document.getElementById('form-add-city');

form.addEventListener('submit', event => {
    event.preventDefault();

    const formData = new FormData(form);
    formData.set('has_magnet', formData.has('has_magnet') ? '1' : '0')

    let button = document.getElementById('btn_add-visited-city');
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm" aria-hidden="true"></span>&nbsp;&nbsp;&nbsp;<span role="status">Загрузка...</span>';

    const url = button.dataset.url;

    fetch(url, {
        method: 'POST', headers: {
            'X-CSRFToken': getCookie("csrftoken")
        }, body: formData
    })
        .then((response) => {
            if (!response.ok) {
                const error = new Error(`HTTP error! status: ${response.status}`);
                error.status = response.status;
                throw error;
            }
            return response.json()
        })
        .then((data) => {
            modal.hide();

            button.disabled = false;
            button.innerText = 'Добавить';

            form.reset();

            showSuccessToast('Успешно', `Город ${data.city.city_title} успешно добавлен как посещённый`);

            const city = new City();

            city.id = data.city.city;
            city.name = data.city.city_title;
            city.region = data.city.region_title;
            city.country = data.city.country;
            city.lat = data.city.lat;
            city.lon = data.city.lon;
            city.number_of_visits = data.city.number_of_visits;
            city.first_visit_date = data.city.first_visit_date;
            city.last_visit_date = data.city.last_visit_date;

            const is_added_new_city = city.number_of_visits === 1;

            actions.updateMarker(city);
            change_qty_of_visited_cities_in_toolbar(is_added_new_city);
        })
        .catch((err) => {
            console.log(err);
            if (err.status === 409) {
                showDangerToast('Ошибка', 'Вы уже посещали город в указанную дату');
            } else {
                showDangerToast('Ошибка', 'Что-то пошло не так. Попробуйте ещё раз.');
            }

            button.disabled = false;
            button.innerText = 'Добавить';
        })
});
