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
    const number_of_visited_cities = document.getElementById('number_of_visited_cities');

    const oldQty = number_of_visited_cities.textContent;
    const newQty = is_added_new_city === true ? Number(oldQty) + 1 : oldQty;
    number_of_visited_cities.innerText = newQty.toString();
}