import {getCookie} from '../components/get_cookie.js';

const notifications = [];
const POLL_INTERVAL = 10000;

// Находим кнопку уведомлений (может быть в мобильной версии или в версии для больших экранов)
// Ищем все кнопки уведомлений с data-hs-overlay="#notificationModal"
function getVisibleNotificationButton() {
  const buttons = document.querySelectorAll('button[data-hs-overlay="#notificationModal"]');
  for (const button of buttons) {
    const style = window.getComputedStyle(button);
    if (style.display !== 'none' && style.visibility !== 'hidden') {
      return button;
    }
  }
  // Если не нашли видимую кнопку, возвращаем первую с ID notification_icon
  return document.getElementById('notification_icon') || buttons[0];
}
const notificationButton = getVisibleNotificationButton();
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
 * Делает кнопку уведомлений красной (при наличии непрочитанных уведомлений)
 */
function make_bell_red() {
    // Обновляем все кнопки уведомлений
    const buttons = document.querySelectorAll('button[data-hs-overlay="#notificationModal"]');
    buttons.forEach(button => {
        // Убираем серые классы
        button.classList.remove('text-gray-600', 'border-gray-200', 'hover:bg-gray-100', 'hover:text-gray-900', 'hover:border-gray-300', 'dark:text-neutral-400', 'dark:border-neutral-700', 'dark:hover:bg-neutral-800', 'dark:hover:text-neutral-200', 'dark:hover:border-neutral-600');
        // Добавляем красные классы (фон, текст, граница)
        button.classList.add('text-red-700', 'bg-red-50', 'border-red-200', 'hover:bg-red-100', 'hover:text-red-800', 'hover:border-red-300', 'dark:text-red-400', 'dark:bg-red-500/10', 'dark:border-red-500/20', 'dark:hover:bg-red-500/20', 'dark:hover:text-red-300', 'dark:hover:border-red-500/30');
    });
}

/**
 * Делает кнопку уведомлений серой (когда нет непрочитанных уведомлений)
 */
function make_bell_gray() {
    // Обновляем все кнопки уведомлений
    const buttons = document.querySelectorAll('button[data-hs-overlay="#notificationModal"]');
    buttons.forEach(button => {
        // Убираем красные классы
        button.classList.remove('text-red-700', 'bg-red-50', 'border-red-200', 'hover:bg-red-100', 'hover:text-red-800', 'hover:border-red-300', 'dark:text-red-400', 'dark:bg-red-500/10', 'dark:border-red-500/20', 'dark:hover:bg-red-500/20', 'dark:hover:text-red-300', 'dark:hover:border-red-500/30');
        // Добавляем серые классы (прозрачный фон, серый текст и граница)
        button.classList.add('text-gray-600', 'border-gray-200', 'hover:bg-gray-100', 'hover:text-gray-900', 'hover:border-gray-300', 'dark:text-neutral-400', 'dark:border-neutral-700', 'dark:hover:bg-neutral-800', 'dark:hover:text-neutral-200', 'dark:hover:border-neutral-600');
    });
}

function add_notifications_to_list() {
    notificationsList.innerHTML = '';

    if (!notifications.length) {
        notificationsList.innerHTML = '<p class="text-sm text-gray-500 dark:text-neutral-400 text-center py-4">У Вас нет непрочитанных уведомлений</p>';
    } else {
        notifications.forEach(notification => {
            const div = document.createElement('div');
            div.className = 'mb-3 p-4 rounded-lg border notificationItem transition-colors';
            div.dataset.id = notification.id;

            // Выделяем непрочитанные уведомления
            if (notification.is_read) {
                div.classList.add('bg-gray-50', 'border-gray-200', 'dark:bg-neutral-800/50', 'dark:border-neutral-700');
            } else {
                div.classList.add('bg-amber-50', 'border-amber-200', 'dark:bg-amber-900/20', 'dark:border-amber-800');
            }

            // Формируем текст сообщения
            let message = `<a href="/share/${notification.sender_id}" class="font-semibold text-gray-900 hover:text-blue-600 dark:text-white dark:hover:text-blue-400 transition-colors">${notification.sender_username}</a>`;
            message += ` <span class="text-gray-700 dark:text-neutral-300">посетил город</span> <a href="/city/${notification.city_id}" class="font-bold text-gray-900 hover:text-blue-600 dark:text-white dark:hover:text-blue-400 transition-colors">${notification.city_title}</a>`;
            if (notification.region_title) {
                message += `, <a href="/region/${notification.region_id}/list" class="font-bold text-gray-900 hover:text-blue-600 dark:text-white dark:hover:text-blue-400 transition-colors">${notification.region_title}</a>`;
            }
            message += `, <a href="/city/all/list?country=${notification.country_code}" class="font-bold text-gray-900 hover:text-blue-600 dark:text-white dark:hover:text-blue-400 transition-colors">${notification.country_title}</a>`;

            // SVG иконка корзины
            const trashIcon = `
                <svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
                </svg>
            `;

            div.innerHTML = `
              <div class="flex items-start justify-between gap-3">
                <div class="flex-1 text-sm leading-relaxed">${message}</div>
                <button type="button" class="deleteNotificationButton flex-shrink-0 p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors dark:text-neutral-500 dark:hover:text-red-400 dark:hover:bg-red-500/10" role="button" aria-label="Удалить уведомление">
                    ${trashIcon}
                </button>
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
                    notificationsList.innerHTML = '<p class="text-sm text-gray-500 dark:text-neutral-400 text-center py-4">У Вас нет непрочитанных уведомлений</p>';
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
                div.classList.remove('bg-amber-50', 'border-amber-200', 'dark:bg-amber-900/20', 'dark:border-amber-800');
                div.classList.add('bg-gray-50', 'border-gray-200', 'dark:bg-neutral-800/50', 'dark:border-neutral-700');
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