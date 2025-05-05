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
import {showSuccessToast, showDangerToast} from "../toast.js";

const fillOpacity = 0.1;
const fillColor = '#6382ff';
const strokeColor = '#0033ff';
const strokeOpacity = 0.3;
const strokeWidth = 2;

const myStyle = {
    fillOpacity: fillOpacity,
    fillColor: fillColor,
    weight: strokeWidth,
    color: strokeColor,
    opacity: strokeOpacity
};

let actions;
let map;
let externalBorder = undefined;
let internalBorder = [];
let downloadedExternalBorder = undefined;
let downloadedInternalBorder = undefined;

window.onload = () => {
    // Карта отображается после того, как загрузятся посещённые города.
    // Это сделано для того, чтобы карта сразу же отцентрировалась на основе посещённых городов.
    // Иначе после загрузки городов пришлось бы перемещать центр карты, что мне не нравится.
    getVisitedCities()
        .then(own_cities => {
            map = create_map();

            addExternalBorderControl(map);
            addInternalBorderControl(map);

            actions = new ToolbarActions(map, own_cities);
            const allMarkers = actions.addOwnCitiesOnMap();
            const group = new L.featureGroup([...allMarkers]);
            map.fitBounds(group.getBounds());
        });
}

function addExternalBorderControl(map) {
    const external_border = new L.Control({
                position: 'topright'
            });
            external_border.onAdd = function (map) {
                let container = L.DomUtil.create('div', 'custom-control-for-map')

                container.title = 'Отобразить внешние границы России';
                container.innerHTML = '<i class="fa-regular fa-square"></i>';
                container.addEventListener('click', () => {
                    if (downloadedExternalBorder === undefined) {
                        fetch('https://geo-polygons.ru/country/hq/RU')
                            .then(response => {
                                if (!response.ok) {
                                    throw new Error('Ошибка при получении полигонов страны')
                                }
                                return response.json();
                            })
                            .then(polygon => {
                                removeBorderFromMap(externalBorder, internalBorder);

                                externalBorder = L.geoJSON(polygon, {
                                    style: myStyle,
                                });
                                externalBorder.addTo(map);
                                downloadedExternalBorder = polygon;
                            })
                    } else {
                        removeBorderFromMap(externalBorder, internalBorder);

                        externalBorder = L.geoJSON(downloadedExternalBorder, {
                            style: myStyle,
                        });
                        externalBorder.addTo(map);
                    }
                });
	            return container;
            }
            external_border.addTo(map);
}

function addInternalBorderControl(map) {
    const external_border = new L.Control({
                position: 'topright'
            });
            external_border.onAdd = function (map) {
                let container = L.DomUtil.create('div', 'custom-control-for-map')

                container.title = 'Отобразить границы регионов России';
                container.innerHTML = '<i class="fa-regular fa-square-plus"></i>';
                container.addEventListener('click', () => {
                    if (downloadedInternalBorder === undefined) {
                        fetch('https://geo-polygons.ru/region/lq/RU/all')
                            .then(response => {
                                if (!response.ok) {
                                    throw new Error('Ошибка при получении полигонов страны')
                                }
                                return response.json();
                            })
                            .then(polygons => {
                                removeBorderFromMap(externalBorder, internalBorder);

                                polygons.forEach(polygon => {
                                    const layer = L.geoJSON(polygon, {
                                        style: myStyle,
                                    }).addTo(map);
                                    internalBorder.push(layer);
                                });
                                downloadedInternalBorder = polygons;
                            })
                    } else {
                        removeBorderFromMap(externalBorder, internalBorder);

                        downloadedInternalBorder.forEach(polygon => {
                            const layer = L.geoJSON(polygon, {
                                style: myStyle,
                            }).addTo(map);
                            internalBorder.push(layer);
                        });
                    }
                });
	            return container;
            }
            external_border.addTo(map);
}

function removeBorderFromMap(externalBorder, internalBorder) {
    if (externalBorder !== undefined) {
        externalBorder.clearLayers();
    }
    if (internalBorder !== undefined) {
        internalBorder.forEach(layer => {
            layer.clearLayers();
        });
    }
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
