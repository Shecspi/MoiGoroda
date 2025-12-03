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
import {initCountrySelect} from "../components/initCountrySelect";
import {initAddCityForm} from "../components/add_city_modal.js";

let actions;
let map;

const urlParams = new URLSearchParams(window.location.search);
const selectedCountryCode = urlParams.get('country');

window.onload = async () => {
    map = create_map();
    window.MG_MAIN_MAP = map;
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
        })
        .then(() => {
            initAddCityForm(actions);
        });

    await initCountrySelect();
}

/**
 * Делает запрос на сервер и возвращает список городов, посещённых пользователем.
 */
async function getVisitedCities() {
    const baseUrl = window.URL_GET_VISITED_CITIES;
    const queryParams = window.location.search;

    const url = baseUrl + queryParams;

    return fetch(url, {
        method: 'GET'
    })
        .then(response => response.json());
}
