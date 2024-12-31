import {create_map} from './map.js';
import {icon_place_pin} from "./icons.js";

const map = create_map([55.7520251, 37.61841444746334], 15);

map.addEventListener('click', function(ev) {
    const lat = ev.latlng.lat;
    const lon = ev.latlng.lng;

    ['administrative', 'poi', 'natural'].forEach((item) => {
        console.log(item);
        let url = `https://nominatim.openstreetmap.org/reverse?email=shecspi@yandex.ru&format=jsonv2&lat=${lat}&lon=${lon}&addressdetails=0`;
        if (item === 'administrative') {
            url += '&zoom=14'
        } else if (item === 'poi') {
            url += '&zoom=18&layer=poi'
        } else if (item === 'natural') {
            url += '&zoom=18&layer=natural';
        }

        fetch(url)
            .then(response => response.json())
            .then(data => {
                let marker;
                if (data.hasOwnProperty('error')) {
                    marker = L.marker(
                        [lat, lon],
                        {
                            icon: icon_place_pin,
                            draggable: true,
                            bounceOnAdd: true
                        }
                    ).addTo(map);
                    marker.bindTooltip('Неизвестный объект', {permanent: true, direction: 'top'});
                } else {
                    marker = L.marker(
                        [data.lat, data.lon],
                        {
                            icon: icon_place_pin,
                            draggable: true,
                            bounceOnAdd: true
                        }
                    ).addTo(map);
                    // marker.bindTooltip(data.name, {permanent: true, direction: 'top'});
                    let content = `<h5>${data.name}</h5>`;
                    content += '<button class="btn btn-success btn-sm">Добавить</button>'
                    marker.bindPopup(content);
                    marker.openPopup();

                    marker.on("dragend", function(e){
                        console.log(e.target.getLatLng().toString());
                    });
                }
            });
    });
});