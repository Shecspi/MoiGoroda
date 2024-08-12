const modal = new bootstrap.Modal(document.getElementById('modal_add_city'), {
    'backdrop': true
});
const form = document.getElementById('form-add-city');

form.addEventListener('submit', event => {
    event.preventDefault();

    const formData = new FormData(form);
    formData.set('has_magnet', formData.has('has_magnet') ? '1' : '0')

    let button = document.getElementById('btn_add-visited-city');
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm" aria-hidden="true"></span>&nbsp;&nbsp;&nbsp;<span role="status">Загрузка...</span>';

    const url = button.dataset.url;

    fetch(url, {
        method: 'POST', headers: {
            'X-CSRFToken': getCookie("csrftoken")
        }, body: formData
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error(response.statusText)
            }
            return response.json()
        })
        .then((data) => {
            modal.toggle();

            button.disabled = false;
            button.innerText = 'Добавить';

            form.reset();

            const element = document.getElementById('toast-success');
            const toast = new bootstrap.Toast(element);
            document.getElementById('city-title-in-toast').innerText = data.city.city_title;
            toast.show();

            actions.updatePlacemark(data.city.city);
            change_qty_of_visited_cities_in_toolbar();
        })
        .catch((err) => {
            console.log(err);

            button.disabled = false;
            button.innerText = 'Добавить';
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

function change_qty_of_visited_cities_in_toolbar() {
    const declensionVisitedElement = document.getElementById('declension-visited');
    const declensionQtyVisitedElement = document.getElementById('declension-qty-visited');
    const declensionVisitedCityElement = document.getElementById('declension-visited-city');

    const oldQty = declensionQtyVisitedElement.textContent;
    const newQty = Number(oldQty) + 1;
    declensionQtyVisitedElement.innerText = newQty.toString();

    declensionVisitedElement.innerText = toTitleCase(declensionVisited(newQty))
    declensionVisitedCityElement.innerText =
        declensionVisitedCity(newQty);
}

function declensionVisited(newQty) {
    if (newQty.toString().endsWith('1') && !newQty.toString().endsWith('11')) {
        return 'посещён'
    } else {
        return 'посещено'
    }
}

function declensionVisitedCity(newQty) {
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
    }
}

function toTitleCase(word) {
    return word.charAt(0).toUpperCase() + word.slice(1);
}
