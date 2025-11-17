import autoComplete from "@tarekraafat/autocomplete.js";
import { pluralize } from "../components/search_services.js";

window.onload = async () => {
    const inputEl = document.querySelector("#collection-search");
    const clearBtn = document.getElementById("collection-search-clear");
    const overlay = document.querySelector("#search-overlay");

    if (!inputEl || !clearBtn || !overlay) {
        return;
    }
    
    // Показать/скрыть кнопку очистки
    const toggleClearButton = () => {
        if (inputEl.value.length > 0) {
            clearBtn.classList.remove("hidden");
        } else {
            clearBtn.classList.add("hidden");
        }
    };
    
    // Обработчик ввода текста
    inputEl.addEventListener("input", toggleClearButton);
    
    // Обработчик клика на кнопку очистки
    clearBtn.addEventListener("click", () => {
        inputEl.value = "";
        toggleClearButton();
        inputEl.focus();
    });

    // Показать/скрыть overlay при фокусе
    inputEl.addEventListener("focus", () => {
        overlay.classList.add("active");
    });

    inputEl.addEventListener("blur", () => {
        // Небольшая задержка, чтобы пользователь мог кликнуть по результатам
        setTimeout(() => {
            overlay.classList.remove("active");
        }, 150);
    });

    // Скрыть overlay при клике на него
    overlay.addEventListener("click", () => {
        inputEl.blur();
        overlay.classList.remove("active");
    });

    // Снять фокус при нажатии Esc
    inputEl.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            inputEl.blur();
            overlay.classList.remove("active");
        }
    });
    
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
                const info = document.createElement("div");
                info.className = "autoComplete-info";
                if (data.results.length) {
                    const word = pluralize(data.results.length, "совпадение", "совпадения", "совпадений");
                    info.innerHTML = `Найдено <strong>${data.results.length}</strong> ${word} для <strong>«${data.query}»</strong>`;
                } else {
                    info.innerHTML = `Нет точных совпадений для <strong>«${data.query}»</strong>`;
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
                item.classList.add("autoComplete-entry");
                item.innerHTML = `<span>${data.match}</span>`;
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