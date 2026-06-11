import * as L from "leaflet";
import {create_map} from "../components/map";
import { buildRegionPolygonUrl } from "../components/region_city_polygons";

(async function initMap() {
    const map = create_map();
    
    const countryCode = window.REGION_CODE.includes('-') ? window.REGION_CODE.split('-')[0] : 'RU';
    const regionCode = window.REGION_CODE.includes('-') ? window.REGION_CODE.split('-')[1] : window.REGION_CODE;
    const url = buildRegionPolygonUrl(countryCode, regionCode, window.QUALITY);

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