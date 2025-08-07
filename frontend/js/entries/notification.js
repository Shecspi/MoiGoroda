document.addEventListener("DOMContentLoaded", function () {
    setTimeout(() => {
        const div_icon = document.getElementById("notification_icon");
        const bell = document.getElementById("bell");

        div_icon.classList.remove('border-secondary-subtle');
        div_icon.classList.remove('bg-secondary-subtle');
        div_icon.classList.add('border-danger-subtle');
        div_icon.classList.add('bg-danger-subtle');
        bell.classList.remove('text-secondary');
        bell.classList.add('text-danger');
    }, 1000)
});