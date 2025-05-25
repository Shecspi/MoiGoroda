export const modal = new bootstrap.Modal(document.getElementById('modal_add_city'), {
    'backdrop': true
});

export function open_modal_for_add_city(city, city_id, region_title) {
    const el_city_title = document.getElementById('city-title-in-modal');
    const el_region_title = document.getElementById('region-title-in-modal');
    const el_city_id = document.getElementById('city-id');

    el_city_title.innerText = city;
    el_region_title.innerText = region_title;
    el_city_id.setAttribute('value', city_id);
    modal.toggle();
}

export function change_qty_of_visited_cities_in_toolbar(is_added_new_city) {
    /**
     * Производит замену текста, сообщающего о количестве посещённых городов, в информационной карточке тулбара.
     */
    const declensionVisitedElement = document.getElementById('declension-visited');
    const declensionQtyVisitedElement = document.getElementById('declension-qty-visited');
    const declensionVisitedCityElement = document.getElementById('declension-visited-city');

    const oldQty = declensionQtyVisitedElement.textContent;
    const newQty = is_added_new_city === true ? Number(oldQty) + 1 : oldQty;
    declensionQtyVisitedElement.innerText = newQty.toString();

    declensionVisitedElement.innerText = toTitleCase(declensionVisited(newQty))
    declensionVisitedCityElement.innerText = declensionVisitedCity(newQty);
}

function declensionVisited(newQty) {
    /**
     * Возвращает слово 'посещён', корректно склонённое для использования с числом newQty.
     */
    if (newQty.toString().endsWith('1') && !newQty.toString().endsWith('11')) {
        return 'посещён'
    } else {
        return 'посещено'
    }
}

function declensionVisitedCity(newQty) {
        /**
         * Возвращает слово "город", корректно склонённое для использования с числом newQty.
         */
    const newQtyStr = newQty.toString();
    if (
        ((10 <= Number(newQtyStr.slice(-2))) && (Number(newQtyStr.slice(-2)) <= 20))
        || (['5', '6', '7', '8', '9', '0'].includes(newQtyStr.slice(-1)))
    ) {
        return 'городов';
    } else if (['2', '3', '4'].includes(newQtyStr.slice(-1))) {
        return 'города'
    } else if (newQtyStr.slice(-1) === '1') {
        return 'город';
    } else {
        // Это блок кода никогда не должен выполняться, так как выше все условия обработаны
        return 'город';
    }
}

function toTitleCase(word) {
    /**
     * Возвращает полученное слово в нижнем регистре с первой заглавной буквой.
     */
    return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
}