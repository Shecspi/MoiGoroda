import autoComplete from "@tarekraafat/autocomplete.js";
import { pluralize } from "../components/search_services.js";

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
    info.classList.add("dropdown-item", "my-2", "px-2", "small", "text-secondary");

    const count = data.results.length;
    const word = pluralize(count, "совпадение", "совпадения", "совпадений");
    info.innerHTML = `Найдено <strong>${count}</strong> ${word} для <strong>"${data.query}"</strong>`;
    
    return info;
}

export function createResultItemElement(data) {
    const item = document.createElement("div");
    item.style.cssText = "display: flex !important; flex-direction: column !important; width: 100%;";
    
    // Основная строка с названием города (сохраняем подсветку)
    const cityName = document.createElement("span");
    cityName.style.cssText = "display: block; text-overflow: ellipsis; white-space: nowrap; overflow: hidden; font-weight: 500; width: 100%;";
    cityName.innerHTML = data.match; // Используем innerHTML для сохранения <mark> тегов
    
    // Вторая строка с регионом и страной
    const locationInfo = document.createElement("span");
    locationInfo.style.cssText = "display: block; font-size: 0.85em; color: #6c757d; text-overflow: ellipsis; white-space: nowrap; overflow: hidden; width: 100%; margin-top: 2px;";
    
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
        placeHolder: "Начните вводить название города...",
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
