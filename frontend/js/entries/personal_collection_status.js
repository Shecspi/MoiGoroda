/**
 * Обработка изменения статуса публичности персональной коллекции.
 *
 * ----------------------------------------------
 *
 * Copyright © Egor Vavilov (Shecspi)
 * Licensed under the Apache License, Version 2.0
 *
 * ----------------------------------------------
 */

import {showSuccessToast, showDangerToast} from '../components/toast.js';
import {getCookie} from '../components/get_cookie.js';

window.addEventListener('load', () => {
    const switchElement = document.getElementById('collection-public-status-switch');
    if (!switchElement) {
        return;
    }

    const collectionId = switchElement.dataset.collectionId;
    if (!collectionId) {
        console.error('Collection ID not found');
        return;
    }

    const apiUrl = `/api/collection/personal/${collectionId}/update-public-status`;

    switchElement.addEventListener('change', async (event) => {
        const isPublic = event.target.checked;

        // Отключаем switch на время отправки запроса
        switchElement.disabled = true;

        try {
            const response = await fetch(apiUrl, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({is_public: isPublic}),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({detail: 'Неизвестная ошибка'}));
                throw new Error(errorData.detail || 'Не удалось изменить статус коллекции');
            }

            const data = await response.json();

            // Обновляем tooltip
            const tooltip = switchElement.closest('.hs-tooltip')?.querySelector('.hs-tooltip-content');
            if (tooltip) {
                if (data.is_public) {
                    tooltip.textContent = 'Коллекция публичная. Любой пользователь может просматривать её.';
                } else {
                    tooltip.textContent = 'Коллекция приватная. Только вы можете просматривать её.';
                }
            }

            showSuccessToast(
                'Успешно',
                data.is_public
                    ? 'Коллекция теперь публичная. Любой пользователь может просматривать её.'
                    : 'Коллекция теперь приватная. Только вы можете просматривать её.'
            );
        } catch (error) {
            console.error('Ошибка при изменении статуса коллекции:', error);
            showDangerToast('Ошибка', error.message || 'Не удалось изменить статус коллекции. Попробуйте ещё раз.');

            // Возвращаем switch в исходное состояние
            switchElement.checked = !isPublic;
        } finally {
            // Включаем switch обратно
            switchElement.disabled = false;
        }
    });
});

