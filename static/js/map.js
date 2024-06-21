function createMap(center_y, center_x, zoom) {
    var myMap = new ymaps.Map("map", {
        center: [center_y, center_x],
        zoom: zoom,
        controls: ['fullscreenControl', 'zoomControl', 'rulerControl']
    }, {
        searchControlProvider: 'yandex#search'
    });

    return myMap;
}

function addCitiesOnMap(visited_cities, myMap) {
    for (let i = 0; i < (visited_cities.length); i++) {
        let lat = visited_cities[i][0];
        let lon = visited_cities[i][1];
        let city = visited_cities[i][2]
        myMap.geoObjects.add(
            new ymaps.Placemark(
                [lat, lon], {
                balloonContent: city }, {
                preset: 'islands#dotIcon', iconColor: '#009d31'
            }));
    }
}

function calculateCenterCoordinates(visited_cities) {
    if (visited_cities.length > 0) {
        // Высчитываем центральную точку карты.
        // Ей является средняя координата всех городов, отображённых на карте.
        let array_x = Array();
        let array_y = Array();
        let zoom = 0;

        // Добавляем все координаты в один массив и находим большее и меньшее значения из них,
        // а затем вычисляем среднее, это и будет являться центром карты.
        for (let i = 0; i < visited_cities.length; i++) {
            array_y.push(parseFloat(visited_cities[i][0]));
            array_x.push(parseFloat(visited_cities[i][1]));
        }
        let max_x = Math.max(...array_x);
        let min_x = Math.min(...array_x);
        let max_y = Math.max(...array_y);
        let min_y = Math.min(...array_y);
        average_x = (max_x + min_x) / 2;
        average_y = (max_y + min_y) / 2;

        // Меняем масштаб карты в зависимости от расположения городов
        let diff = max_y - min_y;
        if (diff <= 1) {
            zoom = 8;
        } else if (diff > 1 && diff <= 2) {
            zoom = 7;
        } else if (diff > 2 && diff <= 4) {
            zoom = 6
        } else if (diff > 4 && diff <= 6) {
            zoom = 5;
        } else {
            zoom = 4;
        }

        return [average_x, average_y, zoom];
    }
    else {
        return [37.588144, 55.733842, 7];
    }
}

function showMap() {
    const [center_x, center_y, zoom] = calculateCenterCoordinates(visited_cities);
    myMap = createMap(center_x, center_y, zoom);
    addCitiesOnMap(visited_cities, myMap);
}


ymaps.ready(showMap);
