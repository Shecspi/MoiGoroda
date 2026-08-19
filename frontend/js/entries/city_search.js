// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

export async function searchCities(query, country = null) {
    if (!query) return [];

    let url = `/api/city/search?query=${encodeURIComponent(query)}`;

    if (country) {
        url += `&country=${encodeURIComponent(country)}`;
    }

    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data
            .filter(item => item && item.title && item.id)
            .map(item => ({
                value: item.title,
                id: item.id,
                region: item.region,
                country: item.country
            }));
    } catch (error) {
        console.error('Ошибка при поиске городов:', error);
        return [];
    }
}

export function initializeCitySearchCombobox(root = document) {
    const comboboxRoot = root.querySelector?.('#city-search-combobox');
    if (!comboboxRoot) return;
    if (comboboxRoot.dataset.mgCitySearchBound) return;

    comboboxRoot.dataset.mgCitySearchBound = '1';
    comboboxRoot.addEventListener('mg:combobox:select', (event) => {
        const cityId = event?.detail?.value;
        if (!cityId) return;
        window.location.href = `/city/${cityId}`;
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeCitySearchCombobox);
} else {
    initializeCitySearchCombobox();
}

document.addEventListener('visited-city-list-refreshed', (event) => {
    initializeCitySearchCombobox(event.detail?.root);
});
