/**
 * Реализует функции для создания объекта карты.
 *
 * ----------------------------------------------
 *
 * Copyright © Egor Vavilov (Shecspi)
 * Licensed under the Apache License, Version 2.0
 *
 * ----------------------------------------------
 */

/**
 * Создаёт и возвращает объект карты с подложкой в виде карты OpenStreetMap
 * и кнопками увеличения/уменьшения масштаба, полноэкранного режима и создания скриншота.
 * @param center Координаты центра карты в виде массива из двух цифр с плавающей запятой
 * @param zoom Масштаб карты (от 1 до 19)
 * @returns Объект карты
 */
export function create_map(center, zoom) {
    const map = L.map('map', {
        attributionControl: false,
        zoomControl: false
        }).setView(center, zoom);

    add_attribution(map);
    add_zoom_control(map);
    add_fullscreen_control(map);
    add_screenshot_control(map);

    return map
}

/**
 * Рассчитывает координаты и зум карты в зависимости от набора координат, переданных в coordinates.
 * @param coordinates {[[number, number]]} Массив массивов с координатами (широта и долгота)
 * @returns {[number, number, number]} Широта, долгота и масштаб карты
 */
export function calculate_center_of_coordinates(coordinates) {
    if (coordinates.length > 0) {
        // Высчитываем центральную точку карты.
        // Ей является средняя координата всех переданных координат.
        let array_lon = Array();
        let array_lat = Array();
        let zoom = 0;

        // Добавляем все координаты в один массив и находим большее и меньшее значения из них,
        // а затем вычисляем среднее, это и будет являться центром карты.
        for (let i = 0; i < coordinates.length; i++) {
            array_lat.push(parseFloat(coordinates[i][0]));
            array_lon.push(parseFloat(coordinates[i][1]));
        }
        let max_lon = Math.max(...array_lon);
        let min_lon = Math.min(...array_lon);
        let max_lat = Math.max(...array_lat);
        let min_lat = Math.min(...array_lat);
        const average_lon = (max_lon + min_lon) / 2;
        const average_lat = (max_lat + min_lat) / 2;

        // Меняем масштаб карты в зависимости от расположения городов
        const diff_lat = max_lat - min_lat;
        const diff_lon = max_lon - min_lon;
        const diff = diff_lat > diff_lon ? diff_lat : diff_lon;

        if (diff_lat > diff_lon) {
            if (diff <= 0.01) {
                zoom = 15;
            } else if (diff <= 0.04) {
                zoom = 14;
            } else if (diff <= 0.05) {
                zoom = 13;
            } else if (diff <= 0.1) {
                zoom = 12;
            } else if (diff <= 0.25) {
                zoom = 11;
            } else if (diff <= 0.5) {
                zoom = 10;
            } else if (diff <= 1) {
                zoom = 9;
            } else if (diff <= 2) {
                zoom = 8;
            } else if (diff <= 3) {
                zoom = 7;
            } else if (diff <= 7) {
                zoom = 6
            } else if (diff <= 15) {
                zoom = 5;
            } else {
                zoom = 4;
            }
        } else {
            if (diff <= 0.05) {
                zoom = 15;
            } else if (diff <= 0.1) {
                zoom = 14;
            } else if (diff <= 0.2) {
                zoom = 13;
            } else if (diff <= 0.5) {
                zoom = 12;
            } else if (diff <= 1) {
                zoom = 11;
            } else if (diff <= 1.5) {
                zoom = 10;
            } else if (diff <= 3) {
                zoom = 9;
            } else if (diff <= 6) {
                zoom = 8;
            } else if (diff <= 15) {
                zoom = 7;
            } else if (diff <= 30) {
                zoom = 6
            } else if (diff <= 50) {
                zoom = 5;
            } else {
                zoom = 4;
            }
        }

        return [average_lat, average_lon, zoom];
    } else {
        // Стандартное значение - центр Москвы
        return [55.751427, 37.618878, 12];
    }
}

/**
 * Добавляет кнопку полноэкранного просмотра.
 * @param map Объект карты, на которую нужно добавить кнопки.
 */
function add_fullscreen_control(map) {
    map.addControl(new L.Control.Fullscreen({
        title: {
            'false': 'Полноэкранный режим',
            'true': 'Выйти из полноэкранного режима'
        }
    }));
}


/**
 * Добавляет кнопки приближения и отдаления карты.
 * @param map Объект карты, на которую нужно добавить кнопки.
 */
function add_zoom_control(map) {
    const zoomControl = L.control.zoom({
        zoomInTitle: 'Нажмите, чтобы приблизить карту',
        zoomOutTitle: 'Нажмите, чтобы отдалить карту'
    });
    zoomControl.addTo(map);
}

/**
 * Добавляет в правый нижний угол указание об использовании карт OopenStreetMap и их лицензии.
 * @param map Объект карты, на который нужно добавить информацию.
 */
function add_attribution(map) {
    const myAttrControl = L.control.attribution().addTo(map);
    myAttrControl.setPrefix('');
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: 'Используются карты &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> под лицензией <a href="https://opendatacommons.org/licenses/odbl/">ODbL.</a>'
    }).addTo(map);
}

/**
 * Добавляет кнопку создания скриншота карты.
 * @param map Объект карты, на которую нужно добавить кнопку.
 */
function add_screenshot_control(map) {
    L.simpleMapScreenshoter().addTo(map);
}