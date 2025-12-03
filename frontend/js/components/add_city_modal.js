/**
 * ----------------------------------------------
 *
 * Copyright © Egor Vavilov (Shecspi)
 * Licensed under the Apache License, Version 2.0
 *
 * ----------------------------------------------
 */

import {City} from "./schemas.js";
import {
    change_qty_of_visited_cities_in_toolbar,
    close_modal_for_add_city,
    open_modal_for_add_city
} from "./services.js";
import {showDangerToast, showSuccessToast} from "./toast.js";
import {getCookie} from "./get_cookie.js";

// Делаем функции открытия/закрытия модалки глобальными,
// чтобы их мог вызывать шаблон модального окна через data-hs-overlay
// даже на страницах, где не используется ToolbarActions.
window.open_modal_for_add_city = open_modal_for_add_city;
window.close_modal_for_add_city = close_modal_for_add_city;

export function initAddCityForm(actions, onSuccess) {
    const form = document.getElementById('form-add-city');
    if (!form) {
        return;
    }

    form.addEventListener('submit', event => {
        event.preventDefault();

        const formData = new FormData(form);
        formData.set('has_magnet', formData.has('has_magnet') ? '1' : '0');

        const button = document.getElementById('btn_add-visited-city');
        if (!button) {
            return;
        }

        button.disabled = true;
        button.innerHTML = '<span class="animate-spin inline-block size-4 border-[3px] border-current border-t-transparent text-white rounded-full" role="status" aria-label="loading"></span><span>Загрузка...</span>';

        const url = button.dataset.url;

        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie("csrftoken")
            },
            body: formData
        })
            .then((response) => {
                if (!response.ok) {
                    const error = new Error(`HTTP error! status: ${response.status}`);
                    error.status = response.status;
                    throw error;
                }
                return response.json();
            })
            .then((data) => {
                close_modal_for_add_city();

                button.disabled = false;
                button.innerHTML = '<span>Добавить</span>';

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

                if (actions && typeof actions.updateMarker === 'function') {
                    actions.updateMarker(city);
                }
                if (typeof onSuccess === 'function') {
                    onSuccess(city);
                }
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
                button.innerHTML = '<span>Добавить</span>';
            });
    });
}


