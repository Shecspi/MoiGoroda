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
import {addExternalBorderControl, addInternalBorderControl, create_map} from "../components/map.js";
import {ToolbarActions} from "../components/toolbar_actions.js";
import {City} from "../components/schemas.js";
import {change_qty_of_visited_cities_in_toolbar, modal} from '../components/services.js';
import {showSuccessToast, showDangerToast} from "../components/toast.js";

let actions;
let map;

window.onload = () => {
    map = create_map();
    addExternalBorderControl(map);
    addInternalBorderControl(map);

    getVisitedCities()
        .then(own_cities => {
            actions = new ToolbarActions(map, own_cities);
            const allMarkers = actions.addOwnCitiesOnMap();
            const group = new L.featureGroup([...allMarkers]);
            map.fitBounds(group.getBounds());
        });
}



/**
 * Делает запрос на сервер и возвращает список городов, посещённых пользователем.
 */
async function getVisitedCities() {
    let url = window.URL_GET_VISITED_CITIES;

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
