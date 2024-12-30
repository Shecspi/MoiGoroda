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
import {create_map} from "../map.js";
import {ToolbarActions} from "./toolbar_actions.js";
import {City} from "./schemas.js";
import {change_qty_of_visited_cities_in_toolbar, modal} from './services.js';

let actions;

window.onload = () => {
    // Карта отображается после того, как загрузятся посещённые города.
    // Это сделано для того, чтобы карта сразу же отцентрировалась на основе посещённых городов.
    // Иначе после загрузки городов пришлось бы перемещать центр карты, что мне не нравится.
    getVisitedCities()
        .then(own_cities => {
            const [center_lat, center_lon, zoom] = calculateCenterCoordinates(own_cities);
            const map = create_map([center_lat, center_lon], zoom);
            actions = new ToolbarActions(map, own_cities);
            actions.addOwnCitiesOnMap();
        });
}

/**
 * Делает запрос на сервер, получает список городов, посещённых пользователем,
 * и помещает его в глобальную переменную usersVisitedCities, откуда можно получить
 * данные из любого места скрипта.
 */
async function getVisitedCities() {
    let url = document.getElementById('url-api__get_visited_cities').dataset.url;

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
        const average_lon = (max_lon + min_lon) / 2;
        const average_lat = (max_lat + min_lat) / 2;

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
                throw new Error(response.statusText)
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

            city.id = data.city.id;
            city.name = data.city.city_title;
            city.region = data.city.region_title;
            city.lat = data.city.lat;
            city.lon = data.city.lon;

            actions.updateMarker(data.city.city);
            change_qty_of_visited_cities_in_toolbar();
        })
        .catch((err) => {
            console.log(err);
            showDangerToast('Ошибка', 'Что-то пошло не так. Попробуйте ещё раз.');

            button.disabled = false;
            button.innerText = 'Добавить';
        })
});
