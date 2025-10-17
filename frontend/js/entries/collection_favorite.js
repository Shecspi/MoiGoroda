import { getCookie } from "../components/get_cookie.js";
import { showSuccessToast, showDangerToast } from "../components/toast.js";

/**
 * Создает анимацию разлетающихся звездочек от позиции мыши
 */
function createStarBurst(mouseX, mouseY) {
    // Получаем позицию скролла страницы
    const scrollX = window.pageXOffset || document.documentElement.scrollLeft;
    const scrollY = window.pageYOffset || document.documentElement.scrollTop;
    
    // Создаем 8 звездочек в разных направлениях
    const angles = [0, 45, 90, 135, 180, 225, 270, 315];
    
    angles.forEach((angle, index) => {
        const star = document.createElement('div');
        star.className = 'star-burst';
        star.innerHTML = '<i class="fas fa-star"></i>';
        
        // Позиционируем звездочку немного выше указателя мыши
        star.style.left = (mouseX + scrollX) + 'px';
        star.style.top = (mouseY + scrollY - 50) + 'px';
        
        // Устанавливаем CSS переменную для поворота звездочки
        star.style.setProperty('--star-rotation', `${angle}deg`);
        
        // Добавляем небольшую задержку для каждой звездочки
        star.style.animationDelay = (index * 0.05) + 's';
        
        document.body.appendChild(star);
        
        // Удаляем звездочку после завершения анимации
        setTimeout(() => {
            if (star.parentNode) {
                star.parentNode.removeChild(star);
            }
        }, 800);
    });
}

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
            const textSpan = button.querySelector('.favorite-text');
            const card = button.closest('.collection-card');

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
                    
                    // Переключаем иконку, текст, цвет и стиль карточки
                    if (data.is_favorite) {
                        icon.classList.remove('far');
                        icon.classList.add('fas');
                        textSpan.textContent = 'Удалить из избранного';
                        button.style.color = '#dc3545'; // красный для удаления
                        card.classList.add('is-favorite'); // добавляем золотой фон
                        
                        // Создаем анимацию разлетающихся звездочек от позиции мыши
                        createStarBurst(event.clientX, event.clientY);
                        
                        showSuccessToast('Успешно', 'Коллекция добавлена в избранное');
                    } else {
                        icon.classList.remove('fas');
                        icon.classList.add('far');
                        textSpan.textContent = 'Добавить в избранное';
                        button.style.color = '#6c757d'; // серый для добавления
                        card.classList.remove('is-favorite'); // убираем золотой фон
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

