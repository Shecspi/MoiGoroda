import {create_map} from './map.js';
import {icon_blue_pin, icon_purple_pin} from "./icons.js";

window.add_place = add_place;

const map = create_map([55.7520251, 37.61841444746334], 15);

fetch('/api/place/')
    .then(response => {
        if (!response.ok) {
            throw new Error('Произошла ошибка при получении данных с сервера');
        }
        return response.json();
    })
    .then(places => {
        places.forEach(place => {
            console.log(place);
            const marker = L.marker(
                [place.latitude, place.longitude],
                {
                    icon: icon_blue_pin
                }).addTo(map);
            marker.bindTooltip(place.name, {direction: 'top'});
        })
    });

let marker = undefined;

map.addEventListener('click', function (ev) {
    const lat = ev.latlng.lat;
    const lon = ev.latlng.lng;

    let url = `https://nominatim.openstreetmap.org/reverse?email=shecspi@yandex.ru&format=jsonv2&lat=${lat}&lon=${lon}&addressdetails=0&zoom=18&layer=natural,poi`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (marker !== undefined) {
                map.removeLayer(marker);
            }

            let name;
            let lat_marker;
            let lon_marker;

            if (data.hasOwnProperty('error')) {
                name = 'Неизвестный объект';
                lat_marker = lat;
                lon_marker = lon;
            } else {
                if (data.name !== '') {
                    name = data.name;
                } else if (data.display_name !== '') {
                    name = data.display_name;
                } else {
                    name = 'Неизвестный объект';
                }
                lat_marker = data.lat;
                lon_marker = data.lon;
            }

            marker = L.marker(
                [lat_marker, lon_marker],
                {
                    icon: icon_purple_pin,
                    draggable: true,
                    bounceOnAdd: true
                }
            ).addTo(map);
            let content = `<h5>${name}</h5>`;

            content += '<p>'
            content += `<span class="fw-semibold">Широта:</span> ${lat_marker}<br>`;
            content += `<span class="fw-semibold">Долгота:</span> ${lon_marker}`;
            content += '</p>';

            content += '<p>';
            content += `<span class="fw-semibold">Категория:</span> ${data.type}`
            content += '</p>';

            content += '<p>';
            content += `<button class="btn btn-success btn-sm" id="btn-add-place" onclick="add_place('${name}', ${lat_marker}, ${lon_marker}, 2);">Добавить</button>'`;
            content += '</p>';

            marker.bindPopup(content);
            marker.openPopup();

            marker.on("dragend", function (e) {
                console.log(e.target.getLatLng().toString());
            });
        });
});

function add_place(name, latitude, longitude) {
    const data = {
        name: name,
        latitude: latitude,
        longitude: longitude,
        type_object: 2
    }
    fetch('/api/place/create/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json;charset=utf-8',
            'X-CSRFToken': getCookie("csrftoken")
        },
        body: JSON.stringify(data)
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Произошла ошибка при получении данных с сервера');
            }
            return response.json()
        })
        .then(data => {
            console.log(data);
        })
}
