/**
 * Список всех регионов: переход в список выбранного региона после выбора в mg-combobox-remote.
 */
function initializeRegionSearchCombobox() {
    const comboboxRoot = document.getElementById('region-search-combobox');
    if (!comboboxRoot) {
        return;
    }

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
