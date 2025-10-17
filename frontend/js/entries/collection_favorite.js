import { getCookie } from "../components/get_cookie.js";
import { showSuccessToast, showDangerToast } from "../components/toast.js";

/**
 * Обработчик для добавления/удаления коллекции из избранного
 */
document.addEventListener('DOMContentLoaded', () => {
    const favoriteButtons = document.querySelectorAll('.favorite-star');

    favoriteButtons.forEach(button => {
        button.addEventListener('click', async (event) => {
            event.preventDefault();
            event.stopPropagation();

            const collectionId = button.dataset.collectionId;
            const isFavorite = button.dataset.isFavorite === 'true';
            const icon = button.querySelector('i');

            // Определяем метод запроса
            const method = isFavorite ? 'DELETE' : 'POST';
            const url = `/api/collection/favorite/${collectionId}`;

            try {
                const response = await fetch(url, {
                    method: method,
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json',
                    },
                });

                if (response.ok) {
                    const data = await response.json();
                    
                    // Обновляем состояние кнопки
                    button.dataset.isFavorite = data.is_favorite ? 'true' : 'false';
                    
                    // Переключаем иконку
                    if (data.is_favorite) {
                        icon.classList.remove('far');
                        icon.classList.add('fas');
                        button.setAttribute('title', 'Удалить из избранного');
                        showSuccessToast('Успешно', 'Коллекция добавлена в избранное');
                    } else {
                        icon.classList.remove('fas');
                        icon.classList.add('far');
                        button.setAttribute('title', 'Добавить в избранное');
                        showSuccessToast('Успешно', 'Коллекция удалена из избранного');
                    }
                } else {
                    const errorData = await response.json();
                    showDangerToast('Ошибка', errorData.detail || 'Не удалось выполнить операцию');
                }
            } catch (error) {
                console.error('Error toggling favorite:', error);
                showDangerToast('Ошибка', 'Произошла ошибка при выполнении запроса');
            }
        });
    });
});

