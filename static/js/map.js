export function create_map(center, zoom) {
    const map = L.map('map', {
        attributionControl: false,
        zoomControl: false
    }).setView(center, zoom);

    add_attribution(map);
    add_zoom_control(map);
    add_fullscreen_control(map);

    return map
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