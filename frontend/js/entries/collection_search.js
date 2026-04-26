function initializeCollectionSearchCombobox() {
    const comboboxRoot = document.getElementById("collection-search-combobox");
    const inputEl = document.getElementById("collection-search");
    const overlay = document.getElementById("search-overlay");

    if (!comboboxRoot || !inputEl || !overlay) {
        return;
    }

    comboboxRoot.addEventListener("mg:combobox:select", (event) => {
        const collectionId = event?.detail?.value;
        if (!collectionId) {
            return;
        }
        window.location.href = `/collection/${collectionId}/list`;
    });

    inputEl.addEventListener("focus", () => {
        overlay.classList.add("active");
    });

    inputEl.addEventListener("blur", () => {
        setTimeout(() => {
            overlay.classList.remove("active");
        }, 150);
    });

    overlay.addEventListener("click", () => {
        inputEl.blur();
        overlay.classList.remove("active");
    });

    inputEl.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            inputEl.blur();
            overlay.classList.remove("active");
        }
    });
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeCollectionSearchCombobox);
} else {
    initializeCollectionSearchCombobox();
}