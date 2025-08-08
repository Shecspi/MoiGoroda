document.addEventListener("DOMContentLoaded", async function () {
    try {
        const response = await fetch('/subscribe/notification');

        if (!response.ok) {
            throw new Error(response.statusText);
        }

        const json = await response.json();
        if (json.notifications.length > 0) {
            make_bell_red();
        }
    } catch (error) {
        console.log('Произошла ошибка при загрузке уведомлений:\n' + error);
    }
});

function make_bell_red() {
    const div_icon = document.getElementById("notification_icon");
    const bell = document.getElementById("bell");

    div_icon.classList.remove('border-secondary-subtle');
    div_icon.classList.remove('bg-secondary-subtle');
    div_icon.classList.add('border-danger-subtle');
    div_icon.classList.add('bg-danger-subtle');
    bell.classList.remove('text-secondary');
    bell.classList.add('text-danger');
}