import {showDangerToast, showSuccessToast} from "../components/toast";

function disable_all_checkboxes() {
    /**
     * Изменяет состояние и активность чекбоксов в случае, когда нужно все их выключить.
     */
    document.getElementById('switch_share_general').checked = false;

    const switch_share_dashboard = document.getElementById('switch_share_dashboard');
    switch_share_dashboard.checked = false;
    switch_share_dashboard.disabled = true;

    const switch_share_city_map = document.getElementById('switch_share_city_map');
    switch_share_city_map.checked = false;
    switch_share_city_map.disabled = true;

    const switch_share_region_map = document.getElementById('switch_share_region_map')
    switch_share_region_map.checked = false;
    switch_share_region_map.disabled = true;

    const switch_subscribe = document.getElementById('switch_subscribe')
    switch_subscribe.checked = false;
    switch_subscribe.disabled = true;

    const input_with_share_link = document.getElementById('input_with_share_link')
    input_with_share_link.disabled = true;

    const button_make_a_copy = document.getElementById('button_make_a_copy')
    button_make_a_copy.disabled = true;
}

function enable_all_checkboxes() {
    /**
     * Изменяет состояние и активность чекбоксов в случае, когда нужно все их включить.
     */
    document.getElementById('switch_share_general').checked = true;

    const switch_share_dashboard = document.getElementById('switch_share_dashboard');
    switch_share_dashboard.checked = true;
    switch_share_dashboard.disabled = false;

    const switch_share_city_map = document.getElementById('switch_share_city_map');
    switch_share_city_map.checked = true;
    switch_share_city_map.disabled = false;

    const switch_share_region_map = document.getElementById('switch_share_region_map')
    switch_share_region_map.checked = true;
    switch_share_region_map.disabled = false;

    const switch_subscribe = document.getElementById('switch_subscribe')
    switch_subscribe.checked = true;
    switch_subscribe.disabled = false;

    const input_with_share_link = document.getElementById('input_with_share_link')
    input_with_share_link.disabled = false;

    const button_make_a_copy = document.getElementById('button_make_a_copy')
    button_make_a_copy.disabled = false;
}

const switch_share_general = document.getElementById('switch_share_general')
const switch_share_dashboard = document.getElementById('switch_share_dashboard')
const switch_share_city_map = document.getElementById('switch_share_city_map')
const switch_share_region_map = document.getElementById('switch_share_region_map')
const switch_subscribe = document.getElementById('switch_subscribe')
const input_with_share_link = document.getElementById('input_with_share_link')
const button_make_a_copy = document.getElementById('button_make_a_copy')
const button_send_to_server = document.getElementById('button_send_to_server')

// Количество включённых дополнительных чекбоксов.
// Когда доходит до 0 - все чекбоксы выключаются и становятся неактивными. Когда до 3 - включаются.
let number_of_active_checkboxes = 0
if (switch_share_dashboard.checked === true) { number_of_active_checkboxes++; }
if (switch_share_city_map.checked === true) { number_of_active_checkboxes++; }
if (switch_share_region_map.checked === true) { number_of_active_checkboxes++; }

// Переключение основного чекбокса с разрешением делиться статистикой
switch_share_general.addEventListener('change', (event) => {
    // Когда он включается, то все дополнительные чекбоксы должны стать активными и получить состояние checked.
    // Это необходимо для того, чтобы избежать ситуации, когда основной чекбокс включён,
    // а ни один из дополнительных - нет. В таком случае непонятно, что именно отображать.
    // Также становится активным поле ввода с сылкой и кнопка скопировать.
    if (event.currentTarget.checked) {
        enable_all_checkboxes();
        number_of_active_checkboxes = 3;
    } else {
        disable_all_checkboxes();
        number_of_active_checkboxes = 0;
    }
});

// При каждом переключени дополнительного чекбокса уменьшаем счётчик активных чекбоксов на 1
// и в случае, если он станет равен 0, выключаем основной чекбокс и делаем неактивными дополнительные.
switch_share_dashboard.addEventListener('change', (event) => {
    switch_share_dashboard.checked === true ? number_of_active_checkboxes++ : number_of_active_checkboxes--;
    if (number_of_active_checkboxes === 0) {
        disable_all_checkboxes()
    }
});
switch_share_city_map.addEventListener('change', (event) => {
    switch_share_city_map.checked === true ? number_of_active_checkboxes++ : number_of_active_checkboxes--;
    if (number_of_active_checkboxes === 0) {
        disable_all_checkboxes()
    }
});
switch_share_region_map.addEventListener('change', (event) => {
    switch_share_region_map.checked === true ? number_of_active_checkboxes++ : number_of_active_checkboxes--;
    if (number_of_active_checkboxes === 0) {
        disable_all_checkboxes()
    }
});

button_send_to_server.addEventListener('click', (event) => {
    const originalContent = button_send_to_server.innerHTML;
    button_send_to_server.innerHTML = '<svg class="size-4 shrink-0 animate-spin rounded-full border-2 border-solid border-current border-r-transparent" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg><span>Сохранить</span>';
    button_send_to_server.disabled = true;
    
    const formData = new FormData(document.getElementById('share_settings_form'));
    fetch('/account/stats/save_share_settings', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': formData.get('csrfmiddlewaretoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        button_send_to_server.innerHTML = originalContent;
        button_send_to_server.disabled = false;
        
        if (data.status === 'ok') {
            showSuccessToast('Успешно', 'Настройки успешно сохранены');
        } else {
            showDangerToast('Ошибка', 'Не удалось сохранить настройки. Попробуйте ещё раз.');
            console.log(data);
        }
    })
    .catch(error => {
        button_send_to_server.innerHTML = originalContent;
        button_send_to_server.disabled = false;
        showDangerToast('Ошибка', 'Произошла ошибка при сохранении настроек. Попробуйте ещё раз.');
        console.log('Ошибка при сохранении настроек.', error);
    });
});

input_with_share_link.addEventListener(`focus`, () => input_with_share_link.select());

// Копирование ссылки в буфер обмена
button_make_a_copy.addEventListener('click', () => {
    const inputValue = input_with_share_link.value.trim();
    if (inputValue) {
        console.log(navigator.clipboard);
        navigator.clipboard.writeText(inputValue)
        .then(() => {
            showSuccessToast('Скопировано', 'Ссылка на страницу со статистикой успешно скопирована.');
        })
        .catch(err => {
            showDangerToast('Ошибка', 'Что-то пошло не так. Попробуйте ещё раз.');
            console.log('Something went wrong', err);
        })
    }
});