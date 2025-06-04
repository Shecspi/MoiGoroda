import {showDangerToast} from "../components/toast";

document.getElementById('register-form').addEventListener('submit', (e) => {
    const checkbox = document.getElementById('agree-personal-data');

    if (!checkbox.checked) {
        e.preventDefault();
        showDangerToast('Ошибка', 'Для регистрации необходимо дать согласие на обработку персональных данных.');
    }
});