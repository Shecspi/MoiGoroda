/**
 * Обработка кнопки копирования публичных коллекций.
 *
 * ----------------------------------------------
 *
 * Copyright © Egor Vavilov (Shecspi)
 * Licensed under the Apache License, Version 2.0
 *
 * ----------------------------------------------
 */

import {getCookie} from '../components/get_cookie.js';
import {showSuccessToast, showDangerToast} from '../components/toast';

document.addEventListener('DOMContentLoaded', () => {
    // Обработчик клика на кнопки копирования коллекций
    document.addEventListener('click', async (event) => {
        const button = event.target.closest('.copy-collection-btn');
        if (!button) {
            return;
        }

        event.preventDefault();
        event.stopPropagation();

        const collectionId = button.getAttribute('data-collection-id');
        if (!collectionId) {
            showDangerToast('Ошибка', 'Не указан ID коллекции');
            return;
        }

        // Отключаем кнопку на время выполнения запроса
        button.disabled = true;
        const originalHTML = button.innerHTML;
        button.innerHTML = '<span class="inline-block animate-spin rounded-full border-2 border-solid border-current border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]"></span>';

        try {
            const response = await fetch(`/api/collection/personal/${collectionId}/copy`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Неизвестная ошибка' }));
                throw new Error(errorData.detail || 'Не удалось скопировать коллекцию');
            }

            const data = await response.json();

            // Показываем сообщение об успехе
            showSuccessToast('Успешно', 'Коллекция успешно скопирована');

            // Перенаправляем на страницу городов коллекции
            window.location.href = `/collection/personal/${data.id}/list`;

        } catch (error) {
            console.error('Ошибка при копировании коллекции:', error);
            showDangerToast('Ошибка', error.message || 'Не удалось скопировать коллекцию. Попробуйте ещё раз.');
            // Восстанавливаем кнопку
            button.disabled = false;
            button.innerHTML = originalHTML;
        }
    });
});

