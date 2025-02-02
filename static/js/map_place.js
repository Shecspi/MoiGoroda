import {create_map} from './map.js';
import {icon_blue_pin, icon_purple_pin} from "./icons.js";
import {showDangerToast, showSuccessToast} from './toast.js';

window.add_place = add_place;
window.delete_place = delete_place;
window.switch_place_to_edit = switch_place_to_edit;

// Карта, на которой будут отображаться все объекты
// const [center_lat, center_lon, zoom] = calculate_center_of_coordinates()
let map = create_map([55, 37], 5);

// Массив, хранящий в себе промисы, в которых загружаются необходимые данные с сервера
const allPromises = [];

// Массив, хранящий в себе информацию обо всех местах.
// Может динамически меняться и хранит в себе всю самую актуальную информацию.
// На основе этого массива можно отрисовывать маркера на карте.
const allPlaces = new Map();

// Массив, хранящий в себе все добавленные на карту маркеры.
const allMarkers = [];
const allCategories = [];

let moved_lat = undefined;
let moved_lon = undefined;

// Словарь, хранящий в себе все известные OSM теги и типы объектов, которые ссылаются на указанные теги
const tags = new Map();
let marker = undefined;

allPromises.push(loadPlacesFromServer());
allPromises.push(loadCategoriesFromServer());
Promise.all([...allPromises]).then(([places, categories]) => {
    places.forEach(place => {
        allPlaces.set(place.id, place);
    });
    addMarkers();

    if (places.length === 0) {
        map.setView([55.751426, 37.618879], 12);
    } else {
        const group = new L.featureGroup([...allMarkers]);
        map.fitBounds(group.getBounds());
    }

    const button = document.getElementById('btn-filter-category');
    const select_filter_by_category = document.getElementById('dropdown-menu-filter-category')

    button.disabled = false;
    button.innerHTML = '<i class="fa-solid fa-layer-group"></i>';

    categories.forEach(category => {
        allCategories.push(category);
        category.tags_detail.forEach(tag => {
            tags.set(tag.name, category.name);
        });

        const filter_by_category_item = document.createElement('a');
        filter_by_category_item.classList.add('dropdown-item');
        filter_by_category_item.innerHTML = category.name;
        filter_by_category_item.style.cursor = 'pointer';
        filter_by_category_item.addEventListener('click', () => {
            updateMarkers(category.name);
            updateBlockQtyPlaces(allMarkers.length);
        });
        select_filter_by_category.appendChild(document.createElement('li').appendChild(filter_by_category_item))
    });

    // Добавляем пункт "Все категории"
    const divider = document.createElement('hr');
    divider.classList.add('dropdown-divider')
    select_filter_by_category.appendChild(document.createElement('li').appendChild(divider));

    const all_categories = document.createElement('a');
    all_categories.classList.add('dropdown-item');
    all_categories.innerHTML = 'Показать все категории';
    all_categories.style.cursor = 'pointer';
    select_filter_by_category.appendChild(document.createElement('li').appendChild(all_categories));
    all_categories.addEventListener('click', () => {
        updateMarkers('__all__');
        updateBlockQtyPlaces(allMarkers.length);
    });

    handleClickOnMap(map);
});

function updateBlockQtyPlaces(qty_places) {
    const block_qty_places = document.getElementById('block-qty_places');

    block_qty_places.classList.remove('placeholder');
    block_qty_places.classList.remove('placeholder-lg');
    block_qty_places.classList.remove('bg-secondary');
    block_qty_places.innerHTML = `Отмечено мест: <span class="fs-4 fw-medium">${qty_places}</span>`;
}

function loadCategoriesFromServer() {
    return fetch('/api/place/category/')
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
        moved_lon = undefined;
        moved_lat = undefined;

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

                allMarkers.push(marker);

                let content = '<form>';
                content += '<h5 id="place_name_text" class="d-flex justify-content-between gap-3" onclick="switch_place_to_edit()">';
                content += `${name}`;
                content += ` <a href="#" class="link-offset-2 link-underline-dark link-dark link-underline-opacity-100-hover link-opacity-50 link-opacity-100-hover"><i class="fa-solid fa-pencil"></i></a>`;
                content += '</h5>';

                content += '<h5 id="place_name_input_form" style="display: flex; justify-content: space-between;" hidden>';
                content += `<input type="text" id="form-name" name="name" value="${name_escaped}" class="form-control-sm" style="width: 100%; box-sizing: border-box">`;
                content += '</h5>';

                content += '<p>'
                content += `<span class="fw-semibold">Широта:</span> ${lat_marker}<br>`;
                content += `<input type="text" id="form-latitude" name="latitude" value="${lat_marker}" hidden>`;

                content += `<span class="fw-semibold">Долгота:</span> ${lon_marker}`;
                content += `<input type="text" id="form-longitude" name="longitude" value="${lon_marker}" hidden>`;
                content += '</p>';

                content += '<p id="category_place">';
                content += '<span class="fw-semibold">Категория:</span> ';
                content += ` ${type_marker !== undefined ? type_marker : 'Не известно'}`
                content += '</p>';

                content += '<p id="category_select_form" hidden>'
                content += '<span class="fw-semibold">Категория:</span> ';
                content += '<select name="category" id="form-type-object" class="form-select form-select-sm">';
                if (type_marker === undefined) {
                    content += `<option value="" selected disabled>Выберите категорию...</option>`;
                }
                allCategories.forEach(category => {
                    if (category.name === type_marker) {
                        content += `<option value="${category.id}" selected>${category.name}</option>`;
                    } else {
                        content += `<option value="${category.id}">${category.name}</option>`;
                    }
                })
                content += '</select>';
                content += '</p>';

                content += '<p>';
                content += `<button class="btn btn-success btn-sm" id="btn-add-place" onclick="add_place(event);">Добавить</button>`;
                content += '</p>';

                content += '</form>'

                marker.bindPopup(content);
                marker.openPopup();

                marker.on("dragend", function (e) {
                    moved_lat = e.target.getLatLng().lat;
                    moved_lon = e.target.getLatLng().lng;
                });
            });
    });
}

function generatePopupContent(id, name, latitide, longitude, category) {
    let content = '';
    content += '<div class="d-flex justify-content-between">';
    content += `<h5 id="place_name_text">${name}</h5>`;
    content += '<a href="#" onclick="switch_place_to_edit();"><i class="fa-solid fa-pencil"></i></a>';
    content += '</div>';

    content += '<h5 id="place_name_input_form" style="display: flex; justify-content: space-between;" hidden>';
    content += `<input type="text" id="form-name" name="name" value="${name_escaped}" class="form-control-sm" style="width: 100%; box-sizing: border-box">`;
    content += '</h5>';

    content += '<p>'
    content += `<span class="fw-semibold">Широта:</span> ${latitide}<br>`;

    content += `<span class="fw-semibold">Долгота:</span> ${longitude}`;
    content += '</p>';

    content += '<p id="category_place">';
    content += '</p>';

    content += '<p id="category_select_form" hidden>'
    content += '<span class="fw-semibold">Категория:</span> ';
    content += '<select name="category" id="form-type-object" class="form-select form-select-sm">';
    if (type_marker === undefined) {
        content += `<option value="" selected disabled>Выберите категорию...</option>`;
    }
    allCategories.forEach(category => {
        if (category.name === type_marker) {
            content += `<option value="${category.id}" selected>${category.name}</option>`;
        } else {
            content += `<option value="${category.id}">${category.name}</option>`;
        }
    })
    content += '</select>';
    content += '</p>';

    content += '<p>';
    content += `<button class="btn btn-danger btn-sm" id="btn-add-place" onclick="delete_place(${id})">Удалить</button>`;
    content += '</p>';

    return content;
}

function delete_place(id) {
    fetch(`/api/place/delete/${id}`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': getCookie("csrftoken")
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Произошла ошибка при удалении');
            }
            if (response.status === 204) {
                allPlaces.delete(id);
                updateMarkers();
                showSuccessToast('Удалено', 'Указанное Вами место успешно удалено')
            } else {
                showDangerToast('Ошибка', 'Произошла неизвестная ошибка и удалить место не получилось. Пожалуйста, обновите страницу и попробуйте ещё раз');
                console.log(response);
                throw new Error('Произошла неизвестная ошибка и удалить место не получилось');
            }
        })
}

function add_place(event) {
    event.preventDefault();

    const data = {
        name: document.getElementById('form-name').value,
        category: document.getElementById('form-type-object').value
    };

    // В зависимости от того, был перемещён маркер или нет, используются разные источники для координат
    if (moved_lat === undefined) {
        data.latitude = document.getElementById('form-latitude').value;
        data.longitude = document.getElementById('form-longitude').value;
    } else {
        data.latitude = moved_lat;
        data.longitude = moved_lon;
    }

    if (data.latitude === "" || data.longitude === "") {
        showDangerToast('Ошибка', 'Не указаны <strong>координаты</strong> объекта.<br>Странно, это поле не доступно для редактирования пользователям. Признавайтесь, вы что-то замышляете? 🧐');
        return false;
    }

    if (data.name === "" || data.category === "") {
        showDangerToast('Ошибка', 'Для добавления места необходимо указать его <strong>имя</strong> и <strong>категорию</strong>.<br>Пожалуйста, заполните соответствующие поля перед добавлением.');
        return false;
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
            allPlaces.set(data.id, data);
            updateMarkers();
            showSuccessToast('Добавлено', 'Указанное Вами место успешно добавлено.')
        })
}

/**
 * Удаляет все маркеры с карты и добавляет их заного.
 */
function updateMarkers(categoryName) {
    allMarkers.forEach(marker => {
        map.removeLayer(marker);
    });
    addMarkers(categoryName);
}

/**
 * Добавляет маркеры на карту.
 */
function addMarkers(categoryName) {
    allMarkers.length = 0;
    allPlaces.forEach(place => {
        if (categoryName === undefined || categoryName === '__all__' || categoryName === place.category_detail.name) {
            const marker = L.marker(
                [place.latitude, place.longitude],
                {
                    icon: icon_blue_pin
                }).addTo(map);
            marker.bindTooltip(place.name, {direction: 'top'});
            marker.bindPopup(generatePopupContent(place.id, place.name, place.latitude, place.longitude, place.category_detail.name));

            allMarkers.push(marker);
        }
    });

    updateBlockQtyPlaces(allPlaces.size);
}

function switch_place_to_edit() {
    document.getElementById('place_name_text').hidden = true;
    document.getElementById('place_name_input_form').hidden = false;

    document.getElementById('category_place').hidden = true;
    document.getElementById('category_select_form').hidden = false;
}
