const url = document.getElementById('url_dashboard_data').dataset.url;


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

        showSuccessToast('Успешно', `Город ${data.city.city_title} успешно добавлен как посещённый`);

        actions.updatePlacemark(data.city.city);
        change_qty_of_visited_cities_in_toolbar();
    })
    .catch((err) => {
        console.log(err);
        showDangerToast('Ошибка', 'Что-то пошло не так. Попробуйте ещё раз.');

        button.disabled = false;
        button.innerText = 'Добавить';
    })
