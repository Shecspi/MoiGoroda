import * as L from 'leaflet';

import {create_map} from '../components/map';
import {icon_blue_pin, icon_purple_pin} from "../components/icons";
import {showDangerToast, showSuccessToast} from '../components/toast';
import {getCookie} from '../components/get_cookie.js';

window.add_place = add_place;
window.delete_place = delete_place;
window.update_place = update_place;
window.switch_popup_elements = switch_popup_elements;

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
    // Получаем все категории и заполняем фильтр по ним
    const button = document.getElementById('btn-filter-category');
    const select_filter_by_category = document.getElementById('dropdown-menu-filter-category')

    button.disabled = false;
    // Убираем спиннер
    const spinner = button.querySelector('span[role="status"]');
    if (spinner) {
        spinner.remove();
    }
    // Показываем иконку
    const iconContainer = document.getElementById('btn-filter-category-icon');
    if (iconContainer) {
        iconContainer.classList.remove('hidden');
    }
    // Показываем текст на кнопке
    const buttonText = document.getElementById('btn-filter-category-text');
    if (buttonText) {
        buttonText.classList.remove('hidden');
    }

    categories.forEach(category => {
        allCategories.push(category);
        category.tags_detail.forEach(tag => {
            tags.set(tag.name, category.name);
        });

        const filter_by_category_item = document.createElement('a');
        filter_by_category_item.classList.add('flex', 'items-center', 'gap-x-2', 'rounded-lg', 'px-3', 'py-2', 'text-sm', 'text-gray-800', 'hover:bg-gray-100', 'dark:text-neutral-200', 'dark:hover:bg-neutral-700');
        filter_by_category_item.innerHTML = category.name;
        filter_by_category_item.style.cursor = 'pointer';
        filter_by_category_item.addEventListener('click', () => {
            updateMarkers(category.name);
            updateBlockQtyPlaces(allMarkers.length);
        });
        const li = document.createElement('li');
        li.appendChild(filter_by_category_item);
        select_filter_by_category.appendChild(li);
    });

    // Добавляем пункт "Все категории"
    const divider = document.createElement('hr');
    divider.classList.add('my-2', 'border-gray-200', 'dark:border-neutral-700');
    const dividerLi = document.createElement('li');
    dividerLi.appendChild(divider);
    select_filter_by_category.appendChild(dividerLi);

    const all_categories = document.createElement('a');
    all_categories.classList.add('flex', 'items-center', 'gap-x-2', 'rounded-lg', 'px-3', 'py-2', 'text-sm', 'text-gray-800', 'hover:bg-gray-100', 'dark:text-neutral-200', 'dark:hover:bg-neutral-700');
    all_categories.innerHTML = 'Показать все категории';
    all_categories.style.cursor = 'pointer';
    const allCategoriesLi = document.createElement('li');
    allCategoriesLi.appendChild(all_categories);
    select_filter_by_category.appendChild(allCategoriesLi);
    all_categories.addEventListener('click', () => {
        updateMarkers('__all__');
        updateBlockQtyPlaces(allMarkers.length);
    });

    // Инициализируем Preline UI dropdown после добавления элементов
    const dropdownElement = button.closest('.hs-dropdown');
    const dropdownMenu = select_filter_by_category;
    
    // Убираем класс hidden и используем opacity для анимации
    dropdownMenu.classList.remove('hidden');
    dropdownMenu.classList.add('opacity-0', 'pointer-events-none');
    
    // Добавляем обработчик клика для открытия/закрытия dropdown
    button.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        // Переключаем видимость меню
        const isHidden = dropdownMenu.classList.contains('opacity-0');
        if (isHidden) {
            dropdownMenu.classList.remove('opacity-0', 'pointer-events-none');
            dropdownMenu.classList.add('opacity-100');
            button.setAttribute('aria-expanded', 'true');
        } else {
            dropdownMenu.classList.remove('opacity-100');
            dropdownMenu.classList.add('opacity-0', 'pointer-events-none');
            button.setAttribute('aria-expanded', 'false');
        }
    });
    
    // Закрываем dropdown при клике вне его
    document.addEventListener('click', function(e) {
        if (!dropdownElement.contains(e.target)) {
            dropdownMenu.classList.remove('opacity-100');
            dropdownMenu.classList.add('opacity-0', 'pointer-events-none');
            button.setAttribute('aria-expanded', 'false');
        }
    });
    
    // Инициализируем Preline UI dropdown для правильной работы
    if (window.HSStaticMethods && typeof window.HSStaticMethods.autoInit === 'function') {
        window.HSStaticMethods.autoInit();
    }

    // Расставляем метки
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

    handleClickOnMap(map);
});

function updateBlockQtyPlaces(qty_places) {
    const block_qty_places_text = document.getElementById('block-qty_places-text');

    block_qty_places_text.innerHTML = `Отмечено мест: <strong>${qty_places}</strong>`;
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

                let content = '<form id="place-form">';
                content += generatePopupContentForNewPlace(name, lat_marker, lon_marker, type_marker);
                content += '<p class="mt-3 flex gap-2">';
                content += `<button class="py-2 px-4 inline-flex items-center justify-center gap-x-2 text-sm font-semibold rounded-lg border border-transparent bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-50 disabled:pointer-events-none focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 dark:focus:ring-offset-neutral-800" id="btn-add-place" onclick="add_place();">Добавить</button>`;
                content += '</p>';
                content += '</form>';

                marker.bindPopup(content, {minWidth: 250});
                marker.openPopup();

                marker.on("dragend", function (e) {
                    moved_lat = e.target.getLatLng().lat;
                    moved_lon = e.target.getLatLng().lng;
                });
            });
    });
}

function generatePopupContentForNewPlace(name, latitude, longitude, place_category) {
    let content = '<div style="min-width: 250px;">';
    content += '<p class="text-sm">';
    content += '<span class="font-semibold text-gray-900 dark:text-white">Название:</span> ';
    content += `<input type="text" id="form-name" name="name" value="${name.replace(/"/g, '&quot;')}" class="mt-1 w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-800 focus:border-blue-500 focus:ring-blue-500 dark:border-neutral-700 dark:bg-neutral-900 dark:text-white dark:focus:border-blue-500 dark:focus:ring-blue-500">`;
    content += '</p>';

    content += '<p class="text-sm mt-2">';
    content += '<span class="font-semibold text-gray-900 dark:text-white">Широта:</span> ';
    content += `${latitude}<br>`;
    content += `<input type="text" id="form-latitude" name="latitude" value="${latitude}" hidden>`;
    content += `<span class="font-semibold text-gray-900 dark:text-white">Долгота:</span> ${longitude}`;
    content += `<input type="text" id="form-longitude" name="longitude" value="${longitude}" hidden>`;
    content += '</p>';

    content += '<p id="category_select_form" class="text-sm mt-2">';
    content += '<span class="font-semibold text-gray-900 dark:text-white">Категория:</span> ';
    content += '<select name="category" id="form-type-object" class="mt-1 w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-800 focus:border-blue-500 focus:ring-blue-500 dark:border-neutral-700 dark:bg-neutral-900 dark:text-white dark:focus:border-blue-500 dark:focus:ring-blue-500">';
    content += '<option value="" selected disabled>Выберите категорию...</option>';
    allCategories.forEach(category => {
        if (category.name === place_category) {
            content += `<option value="${category.id}" selected>${category.name}</option>`;
        } else {
            content += `<option value="${category.id}">${category.name}</option>`;
        }
    });
    content += '</select>';
    content += '</p>';
    content += '</div>';

    return content;
}

function generatePopupContent(name, latitide, longitude, place_category, id) {
    let name_escaped = name.replaceAll('"', "'");

    let content = '';
                content += '<div class="flex items-center justify-between gap-3 text-lg">';
        content += `<div id="place_name_text">${name}</div>`;
        content += '<div id="place_name_input_form" hidden>';
            content += `<input type="text" id="form-name" name="name" value="${name_escaped}" class="w-full rounded-lg border border-gray-200 bg-white px-3 py-1.5 text-sm text-gray-800 focus:border-blue-500 focus:ring-blue-500 dark:border-neutral-700 dark:bg-neutral-900 dark:text-white dark:placeholder-neutral-400 dark:focus:border-blue-500 dark:focus:ring-blue-500">`;
        content += '</div>';
        content += '<div class="flex items-center gap-2">';
            content += '<a href="#" id="link_to_edit_place" onclick="switch_popup_elements()" class="inline-flex items-center gap-x-1.5 rounded-lg border border-transparent px-2 py-1 text-sm text-gray-500 hover:text-gray-600 hover:bg-gray-100 dark:text-neutral-400 dark:hover:text-neutral-300 dark:hover:bg-neutral-800" title="Изменить место"><i class="fa-solid fa-pencil"></i></a>';
            content += '<a href="#" id="lint_to_cancel_edit_place" onclick="switch_popup_elements()" class="inline-flex items-center gap-x-1.5 rounded-lg border border-transparent px-2 py-1 text-sm text-red-500 hover:text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:text-red-300 dark:hover:bg-red-500/10" title="Отменить изменения" hidden><i class="fa-solid fa-ban"></i></a>';
        content += '</div>';
    content += '</div>';

    content += '<p class="text-sm text-gray-600 dark:text-neutral-400">'
        content += `<span class="font-semibold text-gray-900 dark:text-white">Широта:</span> ${latitide}<br>`
        content += `<input type="text" id="form-latitude" name="name" value="${latitide}" hidden>`;
        content += `<span class="font-semibold text-gray-900 dark:text-white">Долгота:</span> ${longitude}`;
        content += `<input type="text" id="form-longitude" name="name" value="${longitude}" hidden>`;
    content += '</p>';

    content += '<p id="category_select_form" hidden class="text-sm">'
        content += '<span class="font-semibold text-gray-900 dark:text-white">Категория:</span> ';
        content += '<select name="category" id="form-type-object" class="mt-1 w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-800 focus:border-blue-500 focus:ring-blue-500 dark:border-neutral-700 dark:bg-neutral-900 dark:text-white dark:focus:border-blue-500 dark:focus:ring-blue-500">';
        if (place_category === undefined) {
            content += `<option value="" selected disabled>Выберите категорию...</option>`;
        }
        allCategories.forEach(category => {
            if (category.name === place_category) {
                content += `<option value="${category.id}" selected>${category.name}</option>`;
            } else {
                content += `<option value="${category.id}">${category.name}</option>`;
            }
        })
        content += '</select>';
    content += '</p>';

    content += '<p id="category_place" class="text-sm text-gray-600 dark:text-neutral-400">';
    content += '<span class="font-semibold text-gray-900 dark:text-white">Категория:</span> ';
    content += ` ${place_category !== undefined ? place_category : 'Не известно'}`;
    content += '</p>';

    return content;
}

function update_place(id) {
    document.querySelector('form').addEventListener('submit', function(event) {
        event.preventDefault();
    });

    const formData = new FormData();
    let name = document.getElementById('form-name').value
    let category_el = document.getElementById('form-type-object');
    let category_id = category_el.value;
    let category_name = category_el.options[category_el.selectedIndex].text;

    formData.set('name', name);
    formData.set('category', category_id)

    fetch(`/api/place/update/${id}`, {
        method: 'PATCH',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie("csrftoken")
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Произошла ошибка при редактировании места');
            }
            if (response.status === 200) {
                let old_place = allPlaces.get(id);
                old_place.name = name;
                old_place.category_detail.id = category_id;
                old_place.category_detail.name = category_name;

                updateMarkers();
                showSuccessToast('Изменено', 'Указанное Вами место успешно отредактировано')

                return false;
            } else {
                showDangerToast('Ошибка', 'Произошла неизвестная ошибка и отредактировать место не получилось. Пожалуйста, обновите страницу и попробуйте ещё раз');
                throw new Error('Произошла неизвестная ошибка и отредактировать место не получилось');
            }
        })
}

function delete_place(id) {
    document.querySelector('form').addEventListener('submit', function(event) {
        event.preventDefault();
    });

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
                throw new Error('Произошла неизвестная ошибка и удалить место не получилось');
            }
        })
}

function add_place() {
    document.querySelector('form').addEventListener('submit', function(event) {
        event.preventDefault();
    });

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

            let content = '<form id="place-form">';
            content += generatePopupContent(place.name, place.latitude, place.longitude, place.category_detail.name, place.id);
            content += '<p class="mt-3 flex gap-2">';
            content += `<button class="py-2 px-4 inline-flex items-center justify-center gap-x-2 text-sm font-semibold rounded-lg border border-transparent bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-50 disabled:pointer-events-none focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 dark:focus:ring-offset-neutral-800" id="btn-update-place" onclick="update_place(${place.id});" hidden>Изменить</button>`;
            content += `<button class="py-2 px-4 inline-flex items-center justify-center gap-x-2 text-sm font-semibold rounded-lg border border-transparent bg-red-600 text-white hover:bg-red-700 disabled:opacity-50 disabled:pointer-events-none focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 dark:focus:ring-offset-neutral-800" id="btn-delete-place" onclick="delete_place(${place.id});">Удалить</button>`;
            content += '</p>';
            content += '</form>';

            marker.bindPopup(content, {maxWidth: 800});

            allMarkers.push(marker);
        }
    });

    updateBlockQtyPlaces(allPlaces.size);
}

function switch_popup_elements() {
    const link_to_edit_place = document.getElementById('link_to_edit_place');
    if (link_to_edit_place) {
        link_to_edit_place.hidden = !link_to_edit_place.hidden;
    }

    const link_to_cancel_edit_place = document.getElementById('lint_to_cancel_edit_place');
    if (link_to_cancel_edit_place) {
        link_to_cancel_edit_place.hidden = !link_to_cancel_edit_place.hidden;
    }

    const place_name_text = document.getElementById('place_name_text');
    if (place_name_text) {
        place_name_text.hidden = !place_name_text.hidden;
    }

    const place_name_input_form = document.getElementById('place_name_input_form');
    if (place_name_input_form) {
        place_name_input_form.hidden = !place_name_input_form.hidden
    }

    const category_place = document.getElementById('category_place');
    if (category_place) {
        category_place.hidden = !category_place.hidden;
    }

    const category_select_form = document.getElementById('category_select_form');
    if (category_select_form) {
        category_select_form.hidden = !category_select_form.hidden;
    }

    const btn_delete_place = document.getElementById('btn-delete-place');
    if (btn_delete_place && btn_delete_place) {
        btn_delete_place.hidden = !btn_delete_place.hidden;
    }

    const btn_update_place = document.getElementById('btn-update-place');
    if (btn_update_place) {
        btn_update_place.hidden = !btn_update_place.hidden;
    }
}