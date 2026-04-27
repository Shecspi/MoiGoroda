import L from 'leaflet';

import {create_map} from '../components/map.js';
import {icon_visited_pin} from '../components/icons.js';
import {bindPopupToMarker} from '../components/city_popup.js';

const map = create_map();
window.MG_MAIN_MAP = map;

const demoCity = {
    id: 524901,
    name: 'Москва',
    isVisited: true,
    firstVisitDate: '2024-03-12',
    lastVisitDate: '2025-02-21',
    numberOfVisits: 4,
    numberOfUsersWhoVisitCity: 1575,
    numberOfVisitsAllUsers: 9342
};

const marker = L.marker([55.7558, 37.6176], {icon: icon_visited_pin}).addTo(map);

bindPopupToMarker(marker, demoCity, {
    regionName: 'Москва',
    countryName: 'Россия',
    regionLink: '/region/1/list',
    countryLink: '/city/all/list?country=RU',
    isAuthenticated: true,
    canMarkVisited: true,
    addButtonText: 'Добавить ещё одно посещение'
});

map.setView([55.7558, 37.6176], 9);
marker.openPopup();
