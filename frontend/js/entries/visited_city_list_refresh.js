// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import {showDangerToast} from '../components/toast.js';
import {showVisitedCityCreatedToast} from '../components/visited_city_created_toast.js';

const REFRESH_SELECTOR = '[data-visited-city-refresh]';

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

    window.MGUi?.destroyAll(container);
    container.replaceWith(updatedContainer);
    try {
        window.MGUi?.initAll(updatedContainer);
    } catch (error) {
        updatedContainer.replaceWith(container);
        window.MGUi?.initAll(container);
        throw error;
    }
    document.dispatchEvent(new CustomEvent('visited-city-list-refreshed', {
        detail: {root: updatedContainer},
    }));
}

document.addEventListener('city-added', async (event) => {
    const container = document.querySelector(REFRESH_SELECTOR);
    if (!container?.dataset.fragmentUrl) {
        return;
    }

    event.preventDefault();
    showVisitedCityCreatedToast(event.detail?.collectionContext);

    try {
        await refreshList(container);
    } catch (error) {
        console.error('Ошибка при обновлении списка:', error);
        showDangerToast('Ошибка', 'Не удалось обновить список. Обновите страницу вручную.');
    }
});
