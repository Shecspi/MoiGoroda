function showSuccessToast(title, message) {
    const container = document.getElementById('toast-container');
    const template = document.getElementById('toast-success-template');
    
    if (!container || !template) {
        console.error('Toast container or template not found');
        return;
    }

    // Клонируем шаблон
    const toast = template.content.cloneNode(true).querySelector('div');
    
    // Заполняем данными
    const titleElement = toast.querySelector('.toast-title');
    const messageElement = toast.querySelector('.toast-message');
    
    if (titleElement) {
        titleElement.textContent = title;
    }
    if (messageElement) {
        messageElement.innerHTML = message;
    }

    // Добавляем обработчик закрытия для кнопки
    const closeButton = toast.querySelector('button[aria-label="Закрыть"]');
    if (closeButton) {
        closeButton.addEventListener('click', function() {
            toast.remove();
        });
    }

    // Добавляем toast в верх стека (в начало контейнера)
    if (container.firstChild) {
        container.insertBefore(toast, container.firstChild);
    } else {
        container.appendChild(toast);
    }

    // Автоматически удаляем через 5 секунд
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, 5000);
}

function showDangerToast(title, message) {
    const container = document.getElementById('toast-container');
    const template = document.getElementById('toast-danger-template');
    
    if (!container || !template) {
        console.error('Toast container or template not found');
        return;
    }

    // Клонируем шаблон
    const toast = template.content.cloneNode(true).querySelector('div');
    
    // Заполняем данными
    const titleElement = toast.querySelector('.toast-title');
    const messageElement = toast.querySelector('.toast-message');
    
    if (titleElement) {
        titleElement.textContent = title;
    }
    if (messageElement) {
        messageElement.innerHTML = message;
    }

    // Добавляем обработчик закрытия для кнопки
    const closeButton = toast.querySelector('button[aria-label="Закрыть"]');
    if (closeButton) {
        closeButton.addEventListener('click', function() {
            toast.remove();
        });
    }

    // Добавляем toast в верх стека (в начало контейнера)
    if (container.firstChild) {
        container.insertBefore(toast, container.firstChild);
    } else {
        container.appendChild(toast);
    }

    // Автоматически удаляем через 5 секунд
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, 5000);
}

// Экспортируем функции для использования в других модулях
export { showSuccessToast, showDangerToast };

// Делаем функции доступными глобально для использования в onclick
window.showSuccessToast = showSuccessToast;
window.showDangerToast = showDangerToast;
