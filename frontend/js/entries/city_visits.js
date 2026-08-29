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

function isCompleteVisitsRoot(root, cityId) {
    const countElement = root?.querySelector('#user-visits-count');
    const list = root?.querySelector('#user-visits-list');
    const count = Number(countElement?.textContent.trim());
    if (
        !root
        || root.dataset.cityId !== cityId
        || !list
        || !root.querySelector('[data-action="add-city"]')
        || !Number.isInteger(count)
        || count < 0
    ) {
        return false;
    }
    if (count === 0) {
        return Boolean(root.querySelector('#user-visits-empty-state'));
    }

    const cards = Array.from(list.querySelectorAll('[data-visit-id]'));
    return cards.length === count && cards.every((card) => (
        card.querySelector('.delete_city') && card.querySelector('[data-action="edit-visited-city"]')
    ));
}

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
        if (!isCompleteVisitsRoot(updatedRoot, root.dataset.cityId)) {
            throw new Error('Visits refresh fragment is incomplete');
        }

        window.MGUi?.destroyAll(root);
        root.replaceWith(updatedRoot);
        window.MGUi?.initAll(updatedRoot);
    } catch (error) {
        console.error('Ошибка при обновлении посещений:', error);
        showDaisyToast({
            type: 'error',
            content: 'Не удалось обновить посещения. Обновите страницу вручную.',
            duration: 5000,
            dismissible: true,
            pauseOnInteraction: true,
        });
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
