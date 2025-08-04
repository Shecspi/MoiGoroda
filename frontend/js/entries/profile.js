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
    const unsubscribeModal = new bootstrap.Modal(document.getElementById("unsubscribeModal"));
    const confirmButton = document.getElementById("confirmUnsubscribeButton");
    const usernamePlaceholder = document.getElementById("unsubscribeUsername");

    unsubscribeButtons.forEach(button => {
        button.addEventListener("click", function () {
            usernamePlaceholder.textContent = this.dataset.username;
            confirmButton.dataset.user_id = this.dataset.user_id;
            confirmButton.dataset.url = this.dataset.url;
            confirmButton.dataset.subscribe_type = this.dataset.subscribe_type;
            unsubscribeModal.show();
        });
    });

    confirmButton.addEventListener("click", async function () {
        const url = confirmButton.dataset.url;
        const subscribe_type = confirmButton.dataset.subscribe_type;

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
                showSuccessToast('Успешно', 'Подписка успешно удалена')
            } else {
                showDangerToast('Ошибка', 'Не удалось удалить подписку')
            }
        } else {
            showDangerToast('Ошибка', 'Не удалось удалить подписку')
        }

        unsubscribeModal.hide();
    });
});