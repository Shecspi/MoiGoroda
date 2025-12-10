/**
 * Обработка вкладок на странице списка коллекций.
 * Поддерживает прямую ссылку на вкладку через URL параметр ?tab=personal
 *
 * ----------------------------------------------
 *
 * Copyright © Egor Vavilov (Shecspi)
 * Licensed under the Apache License, Version 2.0
 *
 * ----------------------------------------------
 */

document.addEventListener('DOMContentLoaded', () => {
    // Проверяем URL параметр для выбора активной вкладки
    const urlParams = new URLSearchParams(window.location.search);
    const tabParam = urlParams.get('tab');

    if (tabParam === 'personal') {
        // Ждем инициализации Preline UI
        const initTab = () => {
            const personalTabButton = document.getElementById('collection-tab-personal');
            
            if (personalTabButton) {
                // Используем Preline UI API для активации вкладки
                if (window.HSTab && typeof window.HSTab.getInstance === 'function') {
                    const tabInstance = window.HSTab.getInstance(personalTabButton);
                    if (tabInstance) {
                        tabInstance.show();
                    } else {
                        // Если экземпляр еще не создан, пробуем программно кликнуть
                        setTimeout(() => {
                            personalTabButton.click();
                        }, 100);
                    }
                } else {
                    // Fallback: программно кликаем на кнопку вкладки
                    setTimeout(() => {
                        personalTabButton.click();
                    }, 100);
                }
            }
        };

        // Пробуем инициализировать сразу
        initTab();

        // Если Preline UI еще не загружен, ждем немного и пробуем снова
        if (!window.HSTab) {
            setTimeout(initTab, 200);
        }
    }
});

