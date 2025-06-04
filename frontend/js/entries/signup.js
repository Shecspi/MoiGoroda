import {showDangerToast} from "../components/toast";

document.getElementById('register-form').addEventListener('submit', (e) => {
    const checkbox = document.getElementById('personal-data-consent');

    if (!checkbox.checked) {
        e.preventDefault();
        showDangerToast('Ошибка', 'Для регистрации необходимо дать согласие на обработку персональных данных.');
    }
});