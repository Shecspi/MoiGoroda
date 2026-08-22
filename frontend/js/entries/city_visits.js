/*
 * ---------------------------------------------
 *
 * Copyright © Egor Vavilov (Shecspi)
 * Licensed under the Apache License, Version 2.0
 *
 * ----------------------------------------------
 */

import {showDaisyToast} from '../components/daisyui_toast.js';

const VISITS_SELECTOR = '#user-visits';

async function refreshVisits(visit) {
    const root = document.querySelector('#user-visits');
    if (!root || String(visit.city) !== root.dataset.cityId || !root.dataset.fragmentUrl) {
        return;
    }

    try {
        const fragmentUrl = new URL(root.dataset.fragmentUrl, window.location.origin);
        const response = await fetch(fragmentUrl.toString());
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const updatedRoot = new DOMParser()
            .parseFromString(await response.text(), 'text/html')
            .querySelector(VISITS_SELECTOR);
        if (
            !updatedRoot
            || updatedRoot.dataset.cityId !== root.dataset.cityId
            || !updatedRoot.querySelector('#user-visits-count')
            || !updatedRoot.querySelector('#user-visits-list')
            || !updatedRoot.querySelector('[data-action="add-city"]')
        ) {
            throw new Error('Visits refresh fragment is incomplete');
        }

        window.MGUi?.destroyAll(root);
        root.replaceWith(updatedRoot);
        window.MGUi?.initAll(updatedRoot);
    } catch (error) {
        console.error('Ошибка при обновлении посещений:', error);
        showDaisyToast('error', 'Не удалось обновить посещения. Обновите страницу вручную.');
    }
}

document.addEventListener('visited-city-created', (event) => {
    if (event.detail.visit) {
        refreshVisits(event.detail.visit);
    }
});

document.addEventListener('visited-city-updated', (event) => {
    if (event.detail.visit) {
        refreshVisits(event.detail.visit);
    }
});
