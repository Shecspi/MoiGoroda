import {getCookie} from "../components/get_cookie";
import {showSuccessToast, showDangerToast} from "../components/toast.js";

function updateButtonState(isSubscribed) {
    const button = document.getElementById('subscribe_button');
    const icon = button.querySelector('.subscribe-icon');
    const text = button.querySelector('.subscribe-text');
    
    if (isSubscribed) {
        // Меняем на состояние "Отписаться"
        button.dataset.action = 'unsubscribe';
        button.className = button.className.replace(/border border-emerald-500 text-emerald-600 hover:bg-emerald-50 dark:border-emerald-400 dark:text-emerald-300 dark:hover:bg-emerald-500\/10/g, 'border border-transparent bg-emerald-600 text-white hover:bg-emerald-700');
        icon.innerHTML = '<path d="M8 16a2 2 0 0 0 2-2H6a2 2 0 0 0 2 2M8 1.918l-.797.161A4 4 0 0 0 4 6c0 .628-.134 2.197-.459 3.742-.16.767-.376 1.566-.663 2.258h10.244c-.287-.692-.502-1.49-.663-2.258C12.134 8.197 12 6.628 12 6a4 4 0 0 0-3.203-3.92L8 1.917zM14.22 12c.223.447.481.801.78 1H1c.299-.199.557-.553.78-1C2.68 10.2 3 6.88 3 6c0-2.42 1.72-4.44 4.005-4.901a1 1 0 1 1 1.99 0A5 5 0 0 1 13 6c0 .88.32 4.2 1.22 6"/><path d="M5 8a1 1 0 0 1 1-1h4a1 1 0 1 1 0 2H6a1 1 0 0 1-1-1m0 3a1 1 0 0 1 1-1h4a1 1 0 1 1 0 2H6a1 1 0 0 1-1-1"/>';
        text.textContent = 'Отписаться';
        button.title = 'Нажмите, чтобы убрать пользователя из своих подписок';
    } else {
        // Меняем на состояние "Подписаться"
        button.dataset.action = 'subscribe';
        button.className = button.className.replace(/border border-transparent bg-emerald-600 text-white hover:bg-emerald-700/g, 'border border-emerald-500 text-emerald-600 hover:bg-emerald-50 dark:border-emerald-400 dark:text-emerald-300 dark:hover:bg-emerald-500/10');
        icon.innerHTML = '<path d="M8 16a2 2 0 0 0 2-2H6a2 2 0 0 0 2 2M8 1.918l-.797.161A4 4 0 0 0 4 6c0 .628-.134 2.197-.459 3.742-.16.767-.376 1.566-.663 2.258h10.244c-.287-.692-.502-1.49-.663-2.258C12.134 8.197 12 6.628 12 6a4 4 0 0 0-3.203-3.92L8 1.917zM14.22 12c.223.447.481.801.78 1H1c.299-.199.557-.553.78-1C2.68 10.2 3 6.88 3 6c0-2.42 1.72-4.44 4.005-4.901a1 1 0 1 1 1.99 0A5 5 0 0 1 13 6c0 .88.32 4.2 1.22 6"/>';
        text.textContent = 'Подписаться';
        button.title = 'После подписки на пользователя Вы сможете сравнивать его посещённые города со своими на одной карте';
    }
}

async function send_to_server() {
    const button = document.getElementById('subscribe_button');
    
    const url = button.dataset.url;
    const action = button.dataset.action;
    const from_id = button.dataset.from_id;
    const to_id = button.dataset.to_id;

    const data = {
        'from_id': from_id,
        'to_id': to_id,
        'action': action
    }

    let response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie("csrftoken")
        },
        body: JSON.stringify(data)
    });

    if (response.ok) {
        let json = await response.json();
        if (json.status == 'subscribed') {
            updateButtonState(true);
            showSuccessToast('', 'Вы подписались на пользователя.');
        } else if (json.status == 'unsubscribed') {
            updateButtonState(false);
            showSuccessToast('', 'Вы отписались от пользователя.');
        } else {
            showDangerToast('', 'Во время отправки запроса произошла ошибка. Попробуйте, пожалуйста, ещё раз.');
        }
    } else {
        let json = await response.json()
        const errorMessage = json.message || 'Во время отправки запроса произошла ошибка. Попробуйте, пожалуйста, ещё раз.';
        showDangerToast('', errorMessage);
    }

    return false;
}

document.getElementById('subscribe_button').addEventListener('click', () => send_to_server());