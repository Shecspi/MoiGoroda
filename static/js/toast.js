export function showSuccessToast(title, message) {
    const toast_element = document.getElementById('toast-success');
    const toast = new bootstrap.Toast(toast_element);
    const title_element = document.getElementById('toast-success-title');
    const message_element = document.getElementById('toast-success-message');

    title_element.innerHTML = title;
    message_element.innerHTML = message;

    toast.show();
}

export function showDangerToast(title, message) {
    const toast_element = document.getElementById('toast-danger');
    const toast = new bootstrap.Toast(toast_element);
    const title_element = document.getElementById('toast-danger-title');
    const message_element = document.getElementById('toast-danger-message');

    title_element.innerHTML = title;
    message_element.innerHTML = message;

    toast.show();
}
