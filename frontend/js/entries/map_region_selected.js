/**
 * Реализует отображение карты региона с метками городов и границами региона.
 *
 * ----------------------------------------------
 *
 * Copyright © Egor Vavilov (Shecspi)
 * Licensed under the Apache License, Version 2.0
 *
 * ----------------------------------------------
 */

import L from "leaflet";
import {
    create_map,
    addLoadControl,
    addErrorControl,
} from "../components/map.js";
import { initAddCityForm } from "../components/add_city_modal.js";
import { icon_visited_pin, icon_not_visited_pin } from "../components/icons.js";
import { bindPopupToMarker } from "../components/city_popup.js";
import { pluralize } from "../components/search_services.js";
import { addRegionCityDisplayControl, syncRegionCityDisplayControl } from "../components/region_city_display_control.js";
import {
    loadCityPolygonLayers,
    updateCityPolygonLayer,
} from "../components/region_city_polygons.js";

// Стили для полигона региона
const fillOpacity = 0.1;
const fillColor = "#6382ff";
const strokeColor = "#0033ff";
const strokeOpacity = 0.3;
const strokeWidth = 2;

// Получаем код региона из DOM
const iso3166_code =
    document.getElementById("iso3166_code").dataset.iso3166_code;
const region_code = iso3166_code.split("-")[1];
const country_code = iso3166_code.split("-")[0];

// Массив с городами региона
// ['latitude', 'longitude', 'city name', 'is_visited']
const all_cities = window.ALL_CITIES || [];

const regionName = window.REGION_NAME || "";
const countryName = window.COUNTRY_NAME || "";

const regionLink = window.REGION_LIST_URL || "";
const countryCitiesBaseUrl = window.COUNTRY_CITIES_BASE_URL || "";
const isAuthenticated =
    typeof window.IS_AUTHENTICATED !== "undefined" &&
    window.IS_AUTHENTICATED === true;

const popupOptions = {
    regionName: regionName,
    countryName: countryName,
    regionLink: regionLink,
    countryLink: countryCitiesBaseUrl
        ? `${countryCitiesBaseUrl}?country=${encodeURIComponent(country_code)}`
        : "",
    isAuthenticated: isAuthenticated,
    canMarkVisited: isAuthenticated,
};

/** @type {import('../components/region_city_polygons.js').RegionCityDisplayMode} */
let displayMode = "markers";
let polygonsLoaded = false;
let polygonsLoading = false;
let polygonsUnavailable = false;
/** @type {L.LayerGroup | null} */
let cityPolygonsGroup = null;
/** @type {Map<number, { layer: L.GeoJSON, cityData: Object }>} */
let cityPolygonLayersById = new Map();

const markersByCityId = new Map();
const markersGroup = L.featureGroup();

// Создаём карту используя общий компонент
const map = create_map();
window.MG_MAIN_MAP = map;

for (let i = 0; i < all_cities.length; i++) {
    const city = all_cities[i];
    const icon = city.isVisited ? icon_visited_pin : icon_not_visited_pin;
    const marker = L.marker([city.lat, city.lon], { icon: icon });
    bindPopupToMarker(marker, city, popupOptions);
    markersGroup.addLayer(marker);
    markersByCityId.set(city.id, { marker, cityData: city });
}

markersGroup.addTo(map);

const cityDisplayControl = addRegionCityDisplayControl(map, {
    getMode: () => displayMode,
    onToggle: () => toggleCityDisplayMode(),
    getDisabled: () => polygonsUnavailable,
});

async function toggleCityDisplayMode() {
    if (polygonsLoading || polygonsUnavailable) {
        return;
    }

    if (displayMode === "markers") {
        await showCityPolygons();
    } else {
        showCityMarkers();
    }
}

function showCityMarkers() {
    if (cityPolygonsGroup && map.hasLayer(cityPolygonsGroup)) {
        map.removeLayer(cityPolygonsGroup);
    }
    if (!map.hasLayer(markersGroup)) {
        markersGroup.addTo(map);
    }
    displayMode = "markers";
}

async function showCityPolygons() {
    if (!polygonsLoaded) {
        polygonsLoading = true;
        const load = addLoadControl(map, "Загружаю границы городов...");
        try {
            const { group, layersByCityId } = await loadCityPolygonLayers(
                all_cities,
                country_code,
                region_code,
                popupOptions,
            );
            cityPolygonsGroup = group;
            cityPolygonLayersById = layersByCityId;
            polygonsLoaded = true;

            if (cityPolygonLayersById.size === 0) {
                addErrorControl(map, "Не удалось загрузить границы городов");
                polygonsUnavailable = true;
                polygonsLoaded = false;
                syncRegionCityDisplayControl(cityDisplayControl);
                return;
            }
        } catch (error) {
            console.log(
                "Произошла ошибка при загрузке границ городов:\n" + error,
            );
            addErrorControl(
                map,
                "Произошла ошибка при загрузке границ городов",
            );
            polygonsUnavailable = true;
            polygonsLoaded = false;
            syncRegionCityDisplayControl(cityDisplayControl);
            return;
        } finally {
            map.removeControl(load);
            polygonsLoading = false;
        }
    }

    if (map.hasLayer(markersGroup)) {
        map.removeLayer(markersGroup);
    }
    if (cityPolygonsGroup && !map.hasLayer(cityPolygonsGroup)) {
        cityPolygonsGroup.addTo(map);
    }
    displayMode = "polygons";
}

// Загружаем полигон региона
const url = `${window.URL_GEO_POLYGONS}/region/hq/${country_code}/${region_code}`;
fetch(url)
    .then((response) => {
        if (!response.ok) {
            throw new Error(response.statusText);
        }
        return response.json();
    })
    .then((geoJson) => {
        const myStyle = {
            fillOpacity: fillOpacity,
            fillColor: fillColor,
            weight: strokeWidth,
            color: strokeColor,
            opacity: strokeOpacity,
        };
        const geojson = L.geoJSON(geoJson, {
            style: myStyle,
        }).addTo(map);

        if (markersGroup.getLayers().length === 0) {
            map.fitBounds(geojson.getBounds());
        }
    })
    .catch((error) => {
        console.log("Произошла ошибка при загрузке границ региона:\n" + error);
    });

if (markersGroup.getLayers().length > 0) {
    map.fitBounds(markersGroup.getBounds());
}

/**
 * Обновляет бейджик с количеством посещённых городов в тулбаре
 */
const updateVisitedCitiesBadge = () => {
    const statBadge = document.querySelector(".js-visited-cities-stat");
    if (!statBadge) {
        return;
    }

    const strongElement = statBadge.querySelector("strong");
    const cityWordElement = document.getElementById("visited-cities-word");
    const visitedWordElement = document.getElementById("visited-word");

    if (!strongElement) {
        return;
    }

    const currentValue = parseInt(strongElement.textContent, 10);
    if (!isNaN(currentValue)) {
        const newValue = currentValue + 1;
        strongElement.textContent = newValue.toString();

        if (cityWordElement) {
            cityWordElement.textContent = pluralize(
                newValue,
                "город",
                "города",
                "городов",
            );
        }

        if (visitedWordElement) {
            visitedWordElement.textContent = pluralize(
                newValue,
                "Посещён",
                "Посещено",
                "Посещено",
            );
        }
    }
};

function applyVisitedCityUpdate(updatedCity) {
    const stored = markersByCityId.get(updatedCity.id);
    if (!stored) {
        return;
    }

    const { marker, cityData } = stored;

    const newCityData = {
        ...cityData,
        isVisited: true,
        numberOfVisits: updatedCity.number_of_visits,
        firstVisitDate: updatedCity.first_visit_date,
        lastVisitDate: updatedCity.last_visit_date,
        numberOfUsersWhoVisitCity:
            updatedCity.number_of_users_who_visit_city ?? null,
        numberOfVisitsAllUsers: updatedCity.number_of_visits_all_users ?? null,
    };

    marker.setIcon(icon_visited_pin);
    marker.unbindPopup();
    marker.unbindTooltip();
    marker.off();
    bindPopupToMarker(marker, newCityData, popupOptions);
    markersByCityId.set(updatedCity.id, { marker, cityData: newCityData });

    const polygonStored = cityPolygonLayersById.get(updatedCity.id);
    if (polygonStored) {
        updateCityPolygonLayer(polygonStored, newCityData, popupOptions);
    }

    const isFirstVisit = !cityData.isVisited;
    if (isFirstVisit) {
        updateVisitedCitiesBadge();
    }
}

if (document.getElementById("form-add-city")) {
    initAddCityForm(null, applyVisitedCityUpdate);
}
