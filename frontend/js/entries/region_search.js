// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

/**
 * Список всех регионов: переход в список выбранного региона после выбора в mg-combobox-remote.
 */
export function initializeRegionSearchCombobox(root = document) {
    const comboboxRoot = root.querySelector?.('#region-search-combobox');
    if (!comboboxRoot) {
        return;
    }

    if (comboboxRoot.dataset.mgRegionSearchBound) {
        return;
    }

    comboboxRoot.dataset.mgRegionSearchBound = '1';
    comboboxRoot.addEventListener('mg:combobox:select', (event) => {
        const regionId = event?.detail?.value;
        if (!regionId) {
            return;
        }
        window.location.href = `/region/${regionId}/list`;
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeRegionSearchCombobox);
} else {
    initializeRegionSearchCombobox();
}

document.addEventListener('visited-city-list-refreshed', (event) => {
    initializeRegionSearchCombobox(event.detail?.root);
});
