/**
 * Загрузка и стилизация полигонов границ городов региона.
 *
 * ----------------------------------------------
 *
 * Copyright © Egor Vavilov (Shecspi)
 * Licensed under the Apache License, Version 2.0
 *
 * ----------------------------------------------
 */

import L from "leaflet";
import { bindPopupToLayer } from "./city_popup.js";

/** @typedef {'markers' | 'polygons'} RegionCityDisplayMode */

/**
 * @param {Object} city
 * @returns {L.PathOptions}
 */
export function getCityPolygonStyle(city) {
    if (city.isVisited) {
        return {
            fillColor: "rgb(66, 178, 66)",
            fillOpacity: 0.35,
            color: "rgb(46, 125, 50)",
            weight: 2,
            opacity: 0.9,
        };
    }
    return {
        fillColor: "rgb(210, 90, 90)",
        fillOpacity: 0.35,
        color: "rgb(180, 60, 60)",
        weight: 2,
        opacity: 0.9,
    };
}

/**
 * @param {string} cityName
 * @param {string} countryCode
 * @param {string} regionCode
 * @returns {string}
 */
export function buildCityPolygonUrl(cityName, countryCode, regionCode) {
    const base = (window.URL_S3_GEO_POLYGONS || "").replace(/\/$/, "");
    const fileName = `${encodeURIComponent(cityName)}.geojson`;
    return `${base}/cities/${countryCode}/${regionCode}/${fileName}`;
}

/**
 * @param {Array<Object>} cities
 * @param {string} countryCode
 * @param {string} regionCode
 * @param {Object} popupOptions
 * @returns {Promise<{ group: L.LayerGroup, layersByCityId: Map<number, { layer: L.GeoJSON, cityData: Object }> }>}
 */
export async function loadCityPolygonLayers(
    cities,
    countryCode,
    regionCode,
    popupOptions,
) {
    const group = L.layerGroup();
    const layersByCityId = new Map();

    const settled = await Promise.allSettled(
        cities.map(async (city) => {
            const url = buildCityPolygonUrl(city.name, countryCode, regionCode);
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`${response.status} ${city.name}`);
            }
            const geoJson = await response.json();
            return { city, geoJson };
        }),
    );

    for (const result of settled) {
        if (result.status !== "fulfilled") {
            continue;
        }
        const { city, geoJson } = result.value;
        const layer = L.geoJSON(geoJson, {
            style: getCityPolygonStyle(city),
            onEachFeature(_feature, pathLayer) {
                bindPopupToLayer(pathLayer, city, popupOptions);
            },
        });
        group.addLayer(layer);
        layersByCityId.set(city.id, { layer, cityData: city });
    }

    return { group, layersByCityId };
}

/**
 * @param {{ layer: L.GeoJSON, cityData: Object }} stored
 * @param {Object} cityData
 * @param {Object} popupOptions
 */
export function updateCityPolygonLayer(stored, cityData, popupOptions) {
    stored.cityData = cityData;
    const style = getCityPolygonStyle(cityData);
    stored.layer.setStyle(style);
    stored.layer.eachLayer((pathLayer) => {
        pathLayer.unbindPopup();
        pathLayer.unbindTooltip();
        pathLayer.off();
        bindPopupToLayer(pathLayer, cityData, popupOptions);
    });
}
