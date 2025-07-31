import * as L from "leaflet";
import {create_map} from "../components/map";

(async function initMap() {
    const map = create_map();
    const url = `${URL_GEO_POLYGONS}/region/hq/RU/${window.REGION_CODE}`;

    const polygonStyle = {
        fillOpacity: 0.1,
        fillColor: '#6382ff',
        weight: 2,
        color: '#0033ff',
        opacity: 0.3
    };

    try {
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(response.statusText);
        }

        const geoJson = await response.json();

        const polygon = L.geoJSON(geoJson, {style: polygonStyle}).addTo(map);
        const group = new L.featureGroup([polygon]);
        map.fitBounds(group.getBounds());
    } catch (error) {
        console.log('Произошла ошибка при загрузке границ региона:\n' + error);
    }
})();