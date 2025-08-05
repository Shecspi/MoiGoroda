import {getCookie} from "../components/get_cookie";
import {showDangerToast, showSuccessToast} from "../components/toast";

window.USER_ID = USER_ID;

function removeUserRow(userId, subscribe_type) {
    const element = document.querySelector(`div[data-subscribe_type="${subscribe_type}"][data-user_id="${userId}"]`);
    if (element) {
        element.remove();
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const unsubscribeButtons = document.querySelectorAll(".unsubscribeButton");
    const deleteSubscriptionButton = document.querySelectorAll(".deleteSubscriptionButton");

    const unsubscribeModal = new bootstrap.Modal(document.getElementById("unsubscribeModal"));
    const deleteSubscriptionModal = new bootstrap.Modal(document.getElementById("deleteSubscriptionModal"));

    const confirmButton = document.getElementById("confirmUnsubscribeButton");
    const confirmDeleteSubscriptionButton = document.getElementById("confirmDeleteSubscriptionButton");

    const usernamePlaceholder = document.getElementById("usernamePlaceholder");
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
        const number_of_subscribed_users = document.getElementById('number_of_subscribed_users')

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
                removeUserRow(this.dataset.user_id, subscribe_type);
                showSuccessToast('Успешно', 'Подписка успешно удалена');
                number_of_subscribed_users.innerText = (Number(number_of_subscribed_users.text) - 1).toString();
            } else {
                showDangerToast('Ошибка', 'Не удалось удалить подписку');
            }
        } else {
            showDangerToast('Ошибка', 'Не удалось удалить подписку');
        }

        unsubscribeModal.hide();
    });
    confirmDeleteSubscriptionButton.addEventListener("click", async function () {
        const data = {
            "user_id": this.dataset.user_id
        }

        const response = await fetch("", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie("csrftoken")
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            showDangerToast('Ошибка', 'Не удалось удалить подписку');
        } else {
            showDangerToast('Ошибка', 'Не удалось удалить подписку');
        }

        deleteSubscriptionModal.hide();
    });
});