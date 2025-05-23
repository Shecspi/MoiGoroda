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
    button_send_to_server.innerHTML = '<i class="fa-solid fa-spin fa-spinner"></i>&nbsp;&nbsp;&nbsp;Сохранить'
    let form = $('#share_settings_form').serialize();
    $.ajax({
        type: 'POST',
        url: '/account/stats/save_share_settings',
        data: form,
        success: function(data) {
            if (data.status === 'ok') {
                button_send_to_server.innerHTML = '<i class="fa-regular fa-floppy-disk"></i>&nbsp;&nbsp;&nbsp;Сохранить'
                $("#save_success").show('fast');
                setTimeout(function() { $("#save_success").hide('fast'); }, 2000);
            } else {
                button_send_to_server.innerHTML = '<i class="fa-regular fa-floppy-disk"></i>&nbsp;&nbsp;&nbsp;Сохранить'
                $("#save_error").show('fast');
                setTimeout(function() { $("#save_error").hide('fast'); }, 2000);
                console.log(data);
            }
        },
        error:  function(){
            console.log('Ошибка при сохранении настроек. ' + data)
        }
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