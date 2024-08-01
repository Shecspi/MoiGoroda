function open_modal_for_add_city(city, region_id, region_title) {
    const modal = new bootstrap.Modal(document.getElementById('modal_add_city'), {
        'backdrop': true
    });
    const el_city_title = document.getElementById('city-title-in-modal');
    const el_region_title = document.getElementById('region-title-in-modal');
    const el_region_id = document.getElementById('region-id');

    el_city_title.innerText = city;
    el_region_title.innerText = region_title;
    el_region_id.setAttribute('value', region_id);
    modal.toggle();
}