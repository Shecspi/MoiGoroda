/**
 * Entry point для страницы просмотра OSM объектов.
 * Инициализирует карту с боковой панелью для загрузки полигонов GeoJSON.
 */
import { initGeoPolygonsAnalytics } from '../components/geo_polygons/analytics.js';
import { initOSMViewer } from '../components/geo_polygons/main.js';

window.onload = () => {
    initGeoPolygonsAnalytics();
    initOSMViewer('map', 'geo-sidebar');
};
