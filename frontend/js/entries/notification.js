import {getCookie} from '../components/get_cookie.js';

const notifications = [];
const POLL_INTERVAL = 10000;

const notificationModal = new bootstrap.Modal(document.getElementById('notificationModal'));
const notificationButton = document.getElementById('notification_icon');
const notificationsList = document.getElementById('notifications-list');

document.addEventListener("DOMContentLoaded", async function () {
    const fetchNotifications = async () => {
        try {
            await get_notifications();
        } catch (err) {
            console.error("Ошибка при получении уведомлений:", err);
        } finally {
            // Запускаем следующий вызов через 5 секунд после завершения текущего
            setTimeout(fetchNotifications, POLL_INTERVAL);
        }
    };

    // Вызов сразу при загрузке страницы
    await fetchNotifications();
});

if (notificationButton) {
    notificationButton.addEventListener('click', function () {
        notificationModal.show();
    });
}

async function get_notifications() {
    try {
        const response = await fetch('/subscribe/notification/');

        if (!response.ok) {
            throw new Error(response.statusText);
        }

        const json = await response.json();
        if (json.notifications.some(n => n.is_read === false)) {
            make_bell_red();
        }
        notifications.length = 0;
        notifications.push(...json.notifications);
        add_notifications_to_list();
    } catch (error) {
        console.log('Произошла ошибка при загрузке уведомлений:\n' + error);
    }
}

/**
 * Делает иконку с колокольчиком красной
 */
function make_bell_red() {
    if (notificationButton) {
        notificationButton.classList.remove('mg-btn-outline-secondary');
        notificationButton.classList.add('mg-btn-outline-danger');
    }
}

/**
 * Делает иконку с колокольчиком серой
 */
function make_bell_gray() {
    if (notificationButton) {
        notificationButton.classList.remove('mg-btn-outline-danger');
        notificationButton.classList.add('mg-btn-outline-secondary');
    }
}

function add_notifications_to_list() {
    notificationsList.innerHTML = '';

    if (!notifications.length) {
        notificationsList.innerHTML = '<p class="text-muted">У Вас нет непрочитанных уведомлений</p>';
    } else {
        notifications.forEach(notification => {
            const div = document.createElement('div');
            div.className = 'mb-2 p-2 rounded notificationItem';
            div.dataset.id = notification.id;

            // Выделяем непрочитанные уведомления
            div.classList.add(notification.is_read ? 'bg-light' : 'bg-warning-subtle', 'border');

            // Формируем текст сообщения
            let message = `<a href="/share/${notification.sender_id}" class="link-offset-2 link-underline-dark link-dark link-opacity-75 link-underline-opacity-75 link-opacity-100-hover fw-bold">${notification.sender_username}</a>`;
            message += ` посетил город <a href="/city/${notification.city_id}" class="link-offset-2 link-underline-dark link-dark link-opacity-75 link-underline-opacity-75 link-opacity-100-hover fw-bolder">${notification.city_title}</a>`;
            if (notification.region_title) {
                message += `, <a href="/region/${notification.region_id}/list" class="link-offset-2 link-underline-dark link-dark link-opacity-75 link-underline-opacity-75 link-opacity-100-hover fw-bolder">${notification.region_title}</a>`;
            }
            message += `, <a href="/city/all/list?country=${notification.country_code}" class="link-offset-2 link-underline-dark link-dark link-opacity-75 link-underline-opacity-75 link-opacity-100-hover fw-bolder">${notification.country_title}</a>`;

            div.innerHTML = `
              <div class="d-flex flex-inline justify-content-between align-items-center">
                <div>${message}</div>
                <div class="p-2 text-secondary deleteNotificationButton" role="button"><i class="fa-solid fa-trash"></i></div>
              </div>
            `;
            notificationsList.appendChild(div);

            // Обработка наведения
            div.addEventListener('mouseenter', () => mark_notification_as_read(notification, div, notifications));
            div.addEventListener('touchstart', () => mark_notification_as_read(notification, div, notifications));

            const deleteBtn = div.querySelector('.deleteNotificationButton');
            deleteBtn.addEventListener('click', (event) => {
                delete_notification(event);
            });
        });
    }
}

function delete_notification(event) {
    const notificationItem = event.target.closest('.notificationItem');
    const id = notificationItem.dataset.id;

    // Отправка DELETE-запроса
    fetch(`/subscribe/notification/${id}/`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie("csrftoken"),
        },
        body: JSON.stringify({is_read: true})
    })
        .then(response => {
            if (response.ok) {
                remove_notification_item(notificationItem);

                // Сравниваем с 1, так как notifications обновляется только при загрузке данных с сервера,
                // но не при удалении уведомления.
                if (notifications.length === 1) {
                    notificationsList.innerHTML = '<p class="text-muted">У Вас нет непрочитанных уведомлений</p>';
                }

                if (!exists_not_read_notifications()) {
                    make_bell_gray();
                }
            } else {
                console.error('Не удалось удалить уведомление', id);
            }
        })
        .catch(err => {
            console.error('Ошибка при DELETE:', err);
        });
}

function remove_notification_item(notificationItem) {
    if (!notificationItem) return;

    notificationItem.remove()
}

function mark_notification_as_read(notification, div) {
    if (notification.is_read) return;

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
                if (!exists_not_read_notifications()) {
                    make_bell_gray();
                }
            } else {
                console.error('Не удалось обновить уведомление', notification.id);
            }
        })
        .catch(err => {
            console.error('Ошибка при PATCH:', err);
        });
}

/**
 * Проверяет, остались ли ещё непрочитанные уведомления
 */
function exists_not_read_notifications() {
    return notifications.some(n => n.is_read === false);
}