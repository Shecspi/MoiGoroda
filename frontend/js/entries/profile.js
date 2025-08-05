import {getCookie} from "../components/get_cookie";
import {showDangerToast, showSuccessToast} from "../components/toast";

window.USER_ID = USER_ID;

function removeUserRow(element) {
    const el = document.querySelector(element);
    if (el) {
        el.remove();
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const unsubscribeButtons = document.querySelectorAll(".unsubscribeButton");
    const deleteSubscriptionButton = document.querySelectorAll(".deleteSubscriptionButton");

    const unsubscribeModal = new bootstrap.Modal(document.getElementById("unsubscribeModal"));
    const deleteSubscriptionModal = new bootstrap.Modal(document.getElementById("deleteSubscriptionModal"));

    const confirmButton = document.getElementById("confirmUnsubscribeButton");
    const confirmDeleteSubscriptionButton = document.getElementById("confirmDeleteSubscriptionButton");

    const usernamePlaceholder = document.getElementById("unsubscribeUsername");
    const deleteSubscriptionUsername = document.getElementById("deleteSubscriptionUsername");

    // Обработка нажатия кнопок в списке подписок/подписчиков
    unsubscribeButtons.forEach(button => {
        button.addEventListener("click", function () {
            usernamePlaceholder.textContent = this.dataset.username;
            confirmButton.dataset.user_id = this.dataset.user_id;
            confirmButton.dataset.url = this.dataset.url;
            confirmButton.dataset.subscribe_type = this.dataset.subscribe_type;
            unsubscribeModal.show();
        });
    });
    deleteSubscriptionButton.forEach(button => {
        button.addEventListener("click", function () {
            deleteSubscriptionUsername.textContent = this.dataset.username;
            confirmDeleteSubscriptionButton.dataset.user_id = this.dataset.user_id;
            deleteSubscriptionModal.show();
        });
    });

    // Обработка нажатия кнопок подтверждения удаления подписки/подписчика
    confirmButton.addEventListener("click", async function () {
        const url = confirmButton.dataset.url;
        const subscribe_type = confirmButton.dataset.subscribe_type;
        const number_of_subscribed_users = document.getElementById('number_of_subscribed_users');
        const list_of_subscribed_users = document.getElementById('list_of_subscribed_users');

        const data = {
            'from_id': window.USER_ID,
            'to_id': this.dataset.user_id,
            'action': 'unsubscribe'
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
            if (json.status === 'unsubscribed') {
                removeUserRow(`div[data-subscribe_type="${subscribe_type}"][data-user_id="${this.dataset.user_id}"]`);
                showSuccessToast('Успешно', 'Подписка успешно удалена');
                number_of_subscribed_users.innerText = (Number(number_of_subscribed_users.textContent) - 1).toString();

                if (Number(number_of_subscribed_users.textContent) === 0) {
                    list_of_subscribed_users.innerText = "Вы ещё не подписались ни на одного пользователя"
                }
            } else {
                showDangerToast('Ошибка', 'Не удалось удалить подписку');
            }
        } else {
            showDangerToast('Ошибка', 'Не удалось удалить подписку');
        }

        unsubscribeModal.hide();
    });
    confirmDeleteSubscriptionButton.addEventListener("click", async function () {
        const number_of_subscriber_users = document.getElementById('number_of_subscriber_users');
        const list_of_subscriber_users = document.getElementById('list_of_subscriber_users');

        const data = {
            "user_id": this.dataset.user_id
        }

        const response = await fetch("/subscribe/subscriber/delete", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie("csrftoken")
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            removeUserRow(`div[data-user_id="${this.dataset.user_id}"]`);
            showSuccessToast('Успешно', 'Подписанный на Вас пользователь успешно удалён');
            number_of_subscriber_users.innerText = (Number(number_of_subscriber_users.textContent) - 1).toString();

            if (Number(number_of_subscriber_users.textContent) === 0) {
                list_of_subscriber_users.innerText = "На Вас ещё не подписался ни один пользователь"
            }
        } else {
            showDangerToast('Ошибка', 'Не удалось удалить подписку');
        }

        deleteSubscriptionModal.hide();
    });
});