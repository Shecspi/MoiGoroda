import {create_map} from './map.js';

const map = create_map([55, 55], 6);

map.addEventListener('click', function(ev) {
    const lat = ev.latlng.lat;
    const lng = ev.latlng.lng
   console.log(lat, lng);
});