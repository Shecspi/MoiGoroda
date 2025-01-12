import {create_map} from './map.js';
import {icon_blue_pin, icon_purple_pin} from "./icons.js";

window.add_place = add_place;
window.switch_place_to_edit = switch_place_to_edit;

const map = create_map([55.7520251, 37.61841444746334], 15);
const allPromises = [];
const typePlaces = [];

// Словарь, хранящий в себе все известные OSM теги и типы объектов, которые ссылаются на указанные теги
const tags = new Map();
let marker = undefined;

allPromises.push(loadPlacesFromServer());
allPromises.push(loadTypePlacesFromServer());
Promise.all([...allPromises]).then(([places, types]) => {
    places.forEach(place => {
        const marker = L.marker(
            [place.latitude, place.longitude],
            {
                icon: icon_blue_pin
            }).addTo(map);
        marker.bindTooltip(place.name, {direction: 'top'});
    });

    types.forEach(type_place => {
        typePlaces.push(type_place);
        type_place.tags_detail.forEach(tag => {
            tags.set(tag.name, type_place.name);
        })
    });

    handleClickOnMap(map);
});

function loadTypePlacesFromServer() {
    return fetch('/api/place/type_place/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Произошла ошибка при получении данных с сервера');
            }
            return response.json();
        })
        .then(data => {
            return data;
        });
}

function loadPlacesFromServer() {
    return fetch('/api/place/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Произошла ошибка при получении данных с сервера');
            }
            return response.json();
        })
        .then(places => {
            return places;
        });
}

function handleClickOnMap(map) {
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
                let type_marker;

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
                let name_escaped = name.replaceAll('"', "'");

                if (data.type !== undefined) {
                    if (tags.has(data.type)) {
                        type_marker = tags.get(data.type);
                    }
                }

                marker = L.marker(
                    [lat_marker, lon_marker],
                    {
                        icon: icon_purple_pin,
                        draggable: true,
                        bounceOnAdd: true
                    }
                ).addTo(map);
                let content = '<form>';
                content += '<h5 id="place_name_from_osm" style="display: flex; justify-content: space-between;" onclick="switch_place_to_edit()">';
                content += `${name}`;
                content += ` <a href="#"><i class="fa-solid fa-pencil"></i></a>`;
                content += '</h5>';

                content += '<h5 id="place_name_input_form" style="display: flex; justify-content: space-between;" hidden>';
                content += `<input type="text" value="${name_escaped}" class="form-control-sm" style="width: 100%; box-sizing: border-box"">`;
                content += '</h5>';

                content += '<p>'
                content += `<span class="fw-semibold">Широта:</span> ${lat_marker}<br>`;
                content += `<span class="fw-semibold">Долгота:</span> ${lon_marker}`;
                content += '</p>';

                content += '<p id="type_place_from_osm">';
                content += '<span class="fw-semibold">Категория:</span> ';
                content += ` ${type_marker !== undefined ? type_marker : 'Не известно'}`
                content += '</p>';

                content += '<p id="type_place_select_form" hidden>'
                content += '<span class="fw-semibold">Категория:</span> ';
                content += '<select name="type_place" id="type_place" class="form-select form-select-sm">';
                if (type_marker === undefined) {
                    content += `<option value="" selected>----</option>`;
                }
                typePlaces.forEach(type_place => {
                    if (type_place.name === type_marker) {
                        content += `<option value="petersburg" selected>${type_place.name}</option>`;
                    } else {
                        content += `<option value="petersburg">${type_place.name}</option>`;
                    }
                })
                content += `<option value="other">Другое</option>`;
                content += '</select>';
                content += '</p>';

                content += '<p>';
                content += `<button class="btn btn-success btn-sm" id="btn-add-place" onclick="add_place('${name}', ${lat_marker}, ${lon_marker}, 2);">Добавить</button>`;
                content += '</p>';

                content += '</form>'

                marker.bindPopup(content);
                marker.openPopup();

                marker.on("dragend", function (e) {
                    console.log(e.target.getLatLng().toString());
                });
            });
    });
}

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

function switch_place_to_edit() {
    document.getElementById('place_name_from_osm').hidden = true;
    document.getElementById('place_name_input_form').hidden = false;

    document.getElementById('type_place_from_osm').hidden = true;
    document.getElementById('type_place_select_form').hidden = false;
}
