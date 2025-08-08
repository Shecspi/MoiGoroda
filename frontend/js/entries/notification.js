import {getCookie} from '../components/get_cookie.js';

const notificationModal = new bootstrap.Modal(document.getElementById('notificationModal'));
const notificationButton = document.getElementById('notification_icon');
const notificationIcon = document.getElementById("bell");
const notificationsList = document.getElementById('notifications-list');

document.addEventListener("DOMContentLoaded", async function () {
    try {
        const response = await fetch('/subscribe/notification/');

        if (!response.ok) {
            throw new Error(response.statusText);
        }

        const json = await response.json();
        if (json.notifications.some(n => n.is_read === false)) {
            make_bell_red();
        }
        add_notifications_to_list(json.notifications);
    } catch (error) {
        console.log('Произошла ошибка при загрузке уведомлений:\n' + error);
    }
});

document.getElementById('notification_icon').addEventListener('click', function () {
    notificationModal.show();
});

function make_bell_red() {
    notificationButton.classList.remove('border-secondary-subtle');
    notificationButton.classList.remove('bg-secondary-subtle');
    notificationButton.classList.add('border-danger-subtle');
    notificationButton.classList.add('bg-danger-subtle');
    notificationIcon.classList.remove('text-secondary');
    notificationIcon.classList.add('text-danger');
}

function add_notifications_to_list(notifications) {
    notificationsList.innerHTML = '';

    if (!notifications.length) {
        notificationsList.innerHTML = '<p class="text-muted">У Вас нет непрочитанных уведомлений</p>';
    } else {
        notifications.forEach(notification => {
            const div = document.createElement('div');
            div.className = 'mb-2 p-2 rounded';

            // Выделяем непрочитанные уведомления
            div.classList.add(notification.is_read ? 'bg-light' : 'bg-warning-subtle', 'border');

            div.innerHTML = `
              <div class="d-flex flex-inline justify-content-between align-items-center">
                <div>${notification.message}</div>
                <div class="p-2 text-secondary" role="button"><i class="fa-solid fa-trash"></i></div>
              </div>
            `;
            notificationsList.appendChild(div);

            // Обработка наведения
            div.addEventListener('mouseenter', () => mark_notification_as_read(notification, div));
            div.addEventListener('touchstart', () => mark_notification_as_read(notification, div));
        });
    }
}

function mark_notification_as_read(notification, div) {
    if (notification.is_read) return;

    // Отправка PATCH-запроса
    fetch(`/subscribe/notification/${notification.id}/`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie("csrftoken"),
        },
        body: JSON.stringify({is_read: true})
    })
        .then(response => {
            if (response.ok) {
                // Обновляем UI
                notification.is_read = true;
                div.classList.remove('bg-warning-subtle');
                div.classList.add('bg-light');
            } else {
                console.error('Не удалось обновить уведомление', notification.id);
            }
        })
        .catch(err => {
            console.error('Ошибка при PATCH:', err);
        });
}