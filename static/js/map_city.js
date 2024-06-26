let placemarks = Array();
let myMap;

function createMap(center_lat, center_lon, zoom) {
    let myMap = new ymaps.Map("map", {
        center: [center_lat, center_lon],
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
        let placemark = new ymaps.Placemark(
            [lat, lon], {
            balloonContent: city }, {
            preset: 'islands#dotIcon', iconColor: '#009d31'
        });
        placemarks.push(placemark);
        myMap.geoObjects.add(placemark);
    }
    console.log(placemarks);
}

function calculateCenterCoordinates(visited_cities) {
    if (visited_cities.length > 0) {
        // Высчитываем центральную точку карты.
        // Ей является средняя координата всех городов, отображённых на карте.
        let array_lon = Array();
        let array_lat = Array();
        let zoom = 0;

        // Добавляем все координаты в один массив и находим большее и меньшее значения из них,
        // а затем вычисляем среднее, это и будет являться центром карты.
        for (let i = 0; i < visited_cities.length; i++) {
            array_lat.push(parseFloat(visited_cities[i][0]));
            array_lon.push(parseFloat(visited_cities[i][1]));
        }
        let max_lon = Math.max(...array_lon);
        let min_lon = Math.min(...array_lon);
        let max_lat = Math.max(...array_lat);
        let min_lat = Math.min(...array_lat);
        average_lon = (max_lon + min_lon) / 2;
        average_lat = (max_lat + min_lat) / 2;

        // Меняем масштаб карты в зависимости от расположения городов
        let diff = max_lat - min_lat;
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
        return [average_lat, average_lon, zoom];
    }
    else {
        return [56.831534, 50.987919, 5];
    }
}


function getCookie(c_name)
    {
        if (document.cookie.length > 0)
        {
            c_start = document.cookie.indexOf(c_name + "=");
            if (c_start != -1)
            {
                c_start = c_start + c_name.length + 1;
                c_end = document.cookie.indexOf(";", c_start);
                if (c_end == -1) c_end = document.cookie.length;
                return unescape(document.cookie.substring(c_start,c_end));
            }
        }
        return "";
    }

    async function send_to_server() {
        const button = document.getElementById("button_send_to_server");
        const url = button.dataset.url
        const data = [1, 2, 3]

        let response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie("csrftoken")
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            var myModalEl = document.getElementById('subscriptions_modal_window');
            var modal = bootstrap.Modal.getInstance(myModalEl)
            modal.hide();

            // Удаление отметок, которые сейчас  существуют на карте
            for (let placemark of placemarks) {
                myMap.geoObjects.remove(placemark);
            }
            placemarks.length = 0;

            const json_source = await response.json();
            const json = JSON.parse(json_source);
            console.log(json);
            for(let i = 0; i < json.length; i++) {
                let obj = json[i];
                // console.log(obj);
            }
        }

        return false;
    }

function init() {
    const [center_lat, center_lon, zoom] = calculateCenterCoordinates(visited_cities);
    myMap = createMap(center_lat, center_lon, zoom);
    addCitiesOnMap(visited_cities, myMap);
}

ymaps.ready(init);

const button = document.getElementById('button_send_to_server');
button.addEventListener('click', function () {
    send_to_server();
});
