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

export function initializeCitySearchCombobox() {
    const comboboxRoot = document.getElementById('city-search-combobox');
    if (!comboboxRoot) return;

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
