const modal = new bootstrap.Modal(document.getElementById('modal_add_city'), {
    'backdrop': true
});
const form = document.getElementById('form-add-city');

form.addEventListener('submit', event => {
    event.preventDefault();

    const formData = new FormData(form);
    formData.set('has_magnet', formData.has('has_magnet') ? '1' : '0')

    fetch('/api/city/visited/add', {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie("csrftoken")
        },
        body: formData
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error(response.statusText)
            }
            return response.json()
        })
        .then((data) => {
            modal.toggle();

            const element = document.getElementById('toast-success');
            const toast = new bootstrap.Toast(element);
            document.getElementById('city-title-in-toast').innerText = data.city.city_title;
            toast.show();

            actions.updatePlacemark(data.city.city);
        })
        .catch((err) => {
            console.log(err);
        })
    });

function open_modal_for_add_city(city, city_id, region_title) {
    const el_city_title = document.getElementById('city-title-in-modal');
    const el_region_title = document.getElementById('region-title-in-modal');
    const el_city_id = document.getElementById('city-id');

    el_city_title.innerText = city;
    el_region_title.innerText = region_title;
    el_city_id.setAttribute('value', city_id);
    modal.toggle();
}
