/**
 * Обработка изменения статуса публичности персональной коллекции и копирования ссылки.
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
    // Обработка изменения статуса публичности коллекции
    const switchElement = document.getElementById('collection-public-status-switch');
    if (switchElement) {
        const collectionId = switchElement.dataset.collectionId;
        if (!collectionId) {
            console.error('Collection ID not found');
        } else {
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

                    // Обновляем tooltip для switch
                    const switchTooltip = switchElement.closest('.hs-tooltip')?.querySelector('.hs-tooltip-content');
                    if (switchTooltip) {
                        if (data.is_public) {
                            switchTooltip.textContent = 'Коллекция публичная. Любой пользователь может просматривать её.';
                        } else {
                            switchTooltip.textContent = 'Коллекция приватная. Только вы можете просматривать её.';
                        }
                    }

                    // Обновляем состояние кнопки копирования ссылки
                    const copyButton = document.getElementById('copy-collection-link-button');
                    if (copyButton) {
                        copyButton.disabled = !data.is_public;
                        const copyTooltip = copyButton.closest('.hs-tooltip')?.querySelector('.hs-tooltip-content');
                        if (copyTooltip) {
                            if (data.is_public) {
                                copyTooltip.textContent = 'Скопировать ссылку на коллекцию';
                            } else {
                                copyTooltip.textContent = 'Сделайте коллекцию публичной, чтобы поделиться ссылкой';
                            }
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
        }
    }

    // Обработка копирования/поделиться ссылкой на коллекцию
    const copyButton = document.getElementById('copy-collection-link-button');
    if (copyButton) {
        // Изменяем текст кнопки, иконку и tooltip в зависимости от поддержки Web Share API
        if (navigator.share) {
            const buttonText = copyButton.querySelector('span');
            if (buttonText) {
                buttonText.textContent = 'Поделиться ссылкой';
            }
            // Заменяем иконку на иконку "Поделиться"
            const icon = document.getElementById('copy-collection-link-icon');
            if (icon) {
                icon.innerHTML = '<path d="M307 34.8c-11.5 5.1-19 16.6-19 29.2v64H176C78.3 128 0 206.3 0 304C0 417.3 81.5 467.9 100.2 478.1c2.5 1.4 5.3 1.9 8.1 1.9c10.9 0 19.7-8.9 19.7-19.7c0-7.5-4.3-14.4-9.8-19.5C108.8 431.9 96 414.4 96 384c0-53 43-96 96-96h96v64c0 12.6 7.4 24.1 19 29.2s25 3 34.4-5.4l160-144c6.7-6.1 10.6-14.7 10.6-23.8s-3.8-17.7-10.6-23.8l-160-144c-9.4-8.5-22.9-10.6-34.4-5.4z"/>';
                icon.setAttribute('viewBox', '0 0 512 512');
                icon.setAttribute('fill', 'currentColor');
                icon.removeAttribute('stroke');
            }
            // Обновляем tooltip
            const tooltip = copyButton.parentElement?.querySelector('.hs-tooltip-content');
            if (tooltip && copyButton.dataset.collectionUrl) {
                const isPublic = !copyButton.disabled;
                if (isPublic) {
                    tooltip.textContent = 'Поделиться ссылкой на коллекцию';
                }
            }
        }

        copyButton.addEventListener('click', async () => {
            const collectionUrl = copyButton.dataset.collectionUrl;
            const collectionTitle = copyButton.dataset.collectionTitle || 'Персональная коллекция городов';
            if (!collectionUrl) {
                showDangerToast('Ошибка', 'Не удалось получить ссылку на коллекцию');
                return;
            }

            // Формируем абсолютный URL
            const absoluteUrl = window.location.origin + collectionUrl;

            // Проверяем поддержку Web Share API (доступно на мобильных устройствах)
            if (navigator.share) {
                try {
                    await navigator.share({
                        title: collectionTitle,
                        text: `Посмотрите мою коллекцию городов «${collectionTitle}»`,
                        url: absoluteUrl,
                    });
                    // Web Share API не требует дополнительного уведомления, так как показывает нативное окно
                } catch (error) {
                    // Пользователь отменил шаринг или произошла ошибка
                    // Если ошибка не связана с отменой, пробуем скопировать в буфер обмена
                    if (error.name !== 'AbortError') {
                        try {
                            await navigator.clipboard.writeText(absoluteUrl);
                            showSuccessToast('Скопировано', 'Ссылка на коллекцию успешно скопирована в буфер обмена.');
                        } catch (clipboardError) {
                            console.error('Ошибка при копировании ссылки:', clipboardError);
                            showDangerToast('Ошибка', 'Не удалось поделиться ссылкой. Попробуйте ещё раз.');
                        }
                    }
                }
            } else {
                // Fallback для устройств без поддержки Web Share API
                try {
                    await navigator.clipboard.writeText(absoluteUrl);
                    showSuccessToast('Скопировано', 'Ссылка на коллекцию успешно скопирована в буфер обмена.');
                } catch (error) {
                    console.error('Ошибка при копировании ссылки:', error);
                    showDangerToast('Ошибка', 'Не удалось скопировать ссылку. Попробуйте ещё раз.');
                }
            }
        });
    }
});

