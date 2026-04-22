import autoComplete from "@tarekraafat/autocomplete.js";
import { pluralize } from "../components/search_services.js";

/**
 * Экранирует строку для безопасной вставки в HTML (защита от XSS).
 * @param {string|number|null|undefined} text - значение для экранирования
 * @returns {string}
 */
function escapeHtml(text) {
    if (text == null || text === undefined) return '';
    const s = String(text);
    return s
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

/**
 * Санитизирует HTML с подсветкой: экранирует всё, кроме тегов <mark> (защита от XSS).
 * @param {string} html - строка с возможными тегами <mark> от autocomplete
 * @returns {string}
 */
function sanitizeMatchHtml(html) {
    if (html == null || html === undefined) return '';
    const s = String(html);
    return escapeHtml(s)
        .replace(/&lt;mark&gt;/g, '<mark>')
        .replace(/&lt;\/mark&gt;/g, '</mark>');
}

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

export function getCountryFromUrl() {
    const params = new URLSearchParams(window.location.search);
    return params.get("country");
}

export function createResultsListElement(data) {
    const info = document.createElement("p");
    info.className = "city-search-list-caption";

    const count = data.results.length;
    const word = pluralize(count, "совпадение", "совпадения", "совпадений");
    info.innerHTML = `Найдено <strong>${count}</strong> ${word} для <strong>"${escapeHtml(data.query)}"</strong>`;
    
    return info;
}

export function createResultItemElement(data) {
    const item = document.createElement("div");
    item.className = "city-search-result-inner";
    
    // Основная строка с названием города (сохраняем подсветку)
    const cityName = document.createElement("span");
    cityName.className = "city-search-result-title";
    cityName.innerHTML = sanitizeMatchHtml(data.match); // Экранируем, сохраняя только <mark> для подсветки
    
    // Вторая строка с регионом и страной
    const locationInfo = document.createElement("span");
    locationInfo.className = "city-search-result-meta";
    
    const locationParts = [];
    if (data.value.region) {
        locationParts.push(data.value.region);
    }
    if (data.value.country) {
        locationParts.push(data.value.country);
    }
    
    locationInfo.textContent = locationParts.join(', ');
    
    item.appendChild(cityName);
    if (locationParts.length > 0) {
        item.appendChild(locationInfo);
    }
    
    return item;
}

export function handleCitySelection(selection, inputEl) {
    const value = selection.value.value; // Получаем название города из объекта
    inputEl.value = value;
    window.location.href = `/city/${selection.value.id}`;
}

export function createAutoCompleteConfig(inputEl) {
    return {
        selector: () => inputEl,
        debounce: 300,
        data: {
            src: async () => {
                const query = inputEl.value;
                const country = getCountryFromUrl();
                return await searchCities(query, country);
            },
            keys: ["value"]
        },
        resultsList: {
            render: true,
            element: (list, data) => {
                const info = createResultsListElement(data);
                list.prepend(info);
            },
            maxResults: undefined,
            noResults: true,
            destination: () => inputEl,
            position: "afterend",
        },
        resultItem: {
            highlight: true,
            element: (item, data) => {
                const styledItem = createResultItemElement(data);
                item.style = styledItem.style;
                item.innerHTML = styledItem.innerHTML;
            },
        },
        events: {
            input: {
                selection: event => {
                    const selection = event.detail.selection;
                    handleCitySelection(selection, inputEl);
                }
            }
        }
    };
}

export function initializeCitySearch() {
    const inputEl = document.querySelector("#city-search");
    if (!inputEl) {
        console.error('Элемент #city-search не найден');
        return null;
    }

    const config = createAutoCompleteConfig(inputEl);
    return new autoComplete(config);
}

// Основная функция инициализации
window.onload = async () => {
    initializeCitySearch();
};
