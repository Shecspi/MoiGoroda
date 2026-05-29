/**
 * Entry point для страницы просмотра OSM объектов.
 * Инициализирует карту с боковой панелью для загрузки полигонов GeoJSON.
 */
import { initOSMViewer } from '../components/geo_polygons/main.js';

window.onload = () => {
    initOSMViewer('map', 'sidebar');
};
