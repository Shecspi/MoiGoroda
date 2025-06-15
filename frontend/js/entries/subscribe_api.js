import {getCookie} from "../components/get_cookie";

async function send_to_server() {
    const subscribe_button = document.getElementById('subscribe_button')
    const unsubscribe_button = document.getElementById('unsubscribe_button')

    const url = subscribe_button.hasAttribute('hidden') ? unsubscribe_button.dataset.url : subscribe_button.dataset.url;
    const action = subscribe_button.hasAttribute('hidden') ? unsubscribe_button.dataset.action : subscribe_button.dataset.action
    const from_id = subscribe_button.hasAttribute('hidden') ? unsubscribe_button.dataset.from_id : subscribe_button.dataset.from_id
    const to_id = subscribe_button.hasAttribute('hidden') ? unsubscribe_button.dataset.to_id : subscribe_button.dataset.to_id

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
        const subscribe_button = document.getElementById('subscribe_button')
        const unsubscribe_button = document.getElementById('unsubscribe_button')

        let json = await response.json();
        if (json.status == 'subscribed') {
            subscribe_button.hidden = true;
            unsubscribe_button.hidden = false;

            const element = document.getElementById('toast_subscribe_api_ok');
            const toast = new bootstrap.Toast(element)
            toast.show()
        } else if (json.status == 'unsubscribed') {
            subscribe_button.hidden = false;
            unsubscribe_button.hidden = true;

            const element = document.getElementById('toast_unsubscribe_api_ok');
            const toast = new bootstrap.Toast(element)
            toast.show()
        } else {
            const element = document.getElementById('toast_error');
            const toast = new bootstrap.Toast(element)
            toast.show()
        }
    } else {
        let json = await response.json()

        const error_message = document.getElementById('error-message');
        const element = document.getElementById('toast_error');
        const toast = new bootstrap.Toast(element)

        error_message.innerText = json.message
        toast.show()
    }

    return false;
}

document.getElementById('unsubscribe_button').addEventListener('click', () => send_to_server());
document.getElementById('subscribe_button').addEventListener('click', () => send_to_server());