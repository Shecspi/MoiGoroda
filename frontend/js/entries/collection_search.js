import autoComplete from "@tarekraafat/autocomplete.js";
import { pluralize } from "../components/search_services.js";

window.onload = async () => {
    const inputEl = document.querySelector("#collection-search");
    const config = {
        selector: () => inputEl,
        placeHolder: "Начните вводить название коллекции...",
        debounce: 300,
        data: {
            src: async () => {
                const query = inputEl.value;

                if (!query) return [];

                let url = `/api/collection/search?query=${encodeURIComponent(query)}`;

                const response = await fetch(url);
                const data = await response.json();
                return data.map(item => ({ value: item.title, id: item.id }));
            },
            keys: ["value"]
        },
        resultsList: {
            render: true,
            element: (list, data) => {
                const info = document.createElement("p");
                info.classList.add("dropdown-item", "my-2", "px-2", "small", "text-secondary");
                if (data.results.length) {
                    const word = pluralize(data.results.length, "совпадение", "совпадения", "совпадений");
                    info.innerHTML = `Найдено <strong>${data.results.length}</strong> ${word} для <strong>"${data.query}"</strong>`;
                } else {
                    info.innerHTML = `Найдено <strong>${data.matches.length}</strong> совпадений для <strong>"${data.query}"</strong>`;
                }
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
                // Modify Results Item Style
                item.style = "display: flex; justify-content: space-between;";
                // Modify Results Item Content
                item.innerHTML = `<span style="text-overflow: ellipsis; white-space: nowrap; overflow: hidden;">${data.match}</span>`;
            },
        },
        events: {
            input: {
                selection: event => {
                    const selection = event.detail.selection.value;
                    inputEl.value = selection.value;
                    window.location.href = `/collection/${selection.id}/list`;
                }
            }
        }
    }

    new autoComplete(config);
}