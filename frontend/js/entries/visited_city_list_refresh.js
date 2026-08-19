// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import {showDangerToast, showSuccessToast} from '../components/toast.js';

const REFRESH_SELECTOR = '[data-visited-city-refresh]';

function getSuccessMessage(cityName) {
    return cityName
        ? `Город ${cityName} успешно добавлен как посещённый`
        : 'Город успешно добавлен как посещённый';
}

async function refreshList(container) {
    const fragmentUrl = new URL(container.dataset.fragmentUrl, window.location.origin);
    fragmentUrl.search = window.location.search;

    const response = await fetch(fragmentUrl.toString());
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const updatedDocument = new DOMParser().parseFromString(await response.text(), 'text/html');
    const updatedContainer = updatedDocument.querySelector(REFRESH_SELECTOR);
    if (!updatedContainer) {
        throw new Error('List refresh fragment is incomplete');
    }

    container.replaceWith(updatedContainer);
}

document.addEventListener('city-added', async (event) => {
    const container = document.querySelector(REFRESH_SELECTOR);
    if (!container?.dataset.fragmentUrl) {
        return;
    }

    event.preventDefault();
    showSuccessToast('Успешно', getSuccessMessage(event.detail?.city?.name));

    try {
        await refreshList(container);
    } catch (error) {
        console.error('Ошибка при обновлении списка:', error);
        showDangerToast('Ошибка', 'Не удалось обновить список. Обновите страницу вручную.');
    }
});
