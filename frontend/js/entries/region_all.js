import {initCountrySelect} from "../components/initCountrySelect";

function updateURLParameter(key, value) {
    const url = new URL(window.location);
    if (!url.searchParams.has(key)) {  // Проверяем, есть ли уже параметр
        url.searchParams.set(key, value);
        window.history.replaceState({}, '', url);
    }
}


document.addEventListener('DOMContentLoaded', async (event) => {
    updateURLParameter('country', 171);

    await initCountrySelect({showAllOption: false});
});