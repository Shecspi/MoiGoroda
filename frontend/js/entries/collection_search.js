// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

export function initializeCollectionSearchCombobox(root = document) {
    const comboboxRoot = root.querySelector('#collection-search-combobox');
    const inputEl = root.querySelector('#collection-search');
    const overlay = root.querySelector('#search-overlay');

    if (!comboboxRoot || !inputEl || !overlay || comboboxRoot.dataset.mgCollectionSearchBound) {
        return;
    }

    comboboxRoot.dataset.mgCollectionSearchBound = '1';
    comboboxRoot.addEventListener('mg:combobox:select', (event) => {
        const collectionId = event?.detail?.value;
        if (collectionId) {
            window.location.href = `/collection/${collectionId}/list`;
        }
    });

    inputEl.addEventListener('focus', () => overlay.classList.add('active'));
    inputEl.addEventListener('blur', () => {
        setTimeout(() => overlay.classList.remove('active'), 150);
    });
    overlay.addEventListener('click', () => {
        inputEl.blur();
        overlay.classList.remove('active');
    });
    inputEl.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            inputEl.blur();
            overlay.classList.remove('active');
        }
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => initializeCollectionSearchCombobox());
} else {
    initializeCollectionSearchCombobox();
}

document.addEventListener('visited-city-list-refreshed', (event) => {
    initializeCollectionSearchCombobox(event.detail?.root);
});
