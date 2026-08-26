// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import * as combobox from '@zag-js/combobox';
import {normalizeProps, spreadProps, VanillaMachine} from '@zag-js/vanilla';

const MINIMUM_QUERY_LENGTH = 1;
const SEARCH_DEBOUNCE_MS = 300;

export class CityCombobox {
    constructor(root, {onSelect = () => {}, onError = () => {}} = {}) {
        this.root = root.querySelector('[data-city-combobox]');
        this.onSelect = onSelect;
        this.onError = onError;
        this.input = this.root?.querySelector('[data-city-combobox-input]');
        this.control = this.root?.querySelector('[data-city-combobox-control]');
        this.positioner = this.root?.querySelector('[data-city-combobox-positioner]');
        this.results = this.root?.querySelector('[data-city-combobox-content]');
        this.clearButton = this.root?.querySelector('[data-city-combobox-clear]');
        this.loading = this.root?.querySelector('[data-city-combobox-loading]');
        this.controller = null;
        this.searchTimer = null;
        this.requestVersion = 0;
        this.items = [];
        this.hasEmptySearchResult = false;
        this.inputValue = '';
        this.collection = combobox.collection({items: []});
        this.machine = null;
        this.unsubscribe = null;
        this.propCleanups = [];
        this.boundInput = (event) => this.handleInput(event);
        this.boundClear = () => this.clearInput();
    }

    init() {
        if (!this.root || !this.input || !this.control || !this.positioner || !this.results) {
            return;
        }

        this.machine = new VanillaMachine(combobox.machine, {
            id: `${this.input.id}-combobox`,
            collection: this.collection,
            inputValue: this.inputValue,
            inputBehavior: 'none',
            openOnChange: false,
            positioning: {placement: 'bottom-start'},
            onValueChange: ({items}) => {
                const city = items[0] || null;
                if (city) {
                    this.inputValue = city.title;
                    this.machine.updateProps({inputValue: this.inputValue});
                }
                this.onSelect(city);
            },
        });
        this.unsubscribe = this.machine.subscribe(() => this.render());
        this.machine.start();
        this.render();
        this.input.addEventListener('input', this.boundInput);
        this.clearButton?.addEventListener('click', this.boundClear);
    }

    destroy() {
        this.cancelSearch();
        this.unsubscribe?.();
        this.unsubscribe = null;
        this.input?.removeEventListener('input', this.boundInput);
        this.clearButton?.removeEventListener('click', this.boundClear);
        this.clearProps();
        this.machine?.stop();
        this.machine = null;
        this.items = [];
        this.loading && (this.loading.hidden = true);
    }

    handleInput(event) {
        this.inputValue = event.currentTarget.value;
        this.machine.updateProps({inputValue: this.inputValue});
        const api = this.getApi();
        if (api.value.length > 0) {
            api.clearValue();
        }
        this.onSelect(null);
        this.search(this.inputValue);
    }

    clearInput() {
        this.cancelSearch();
        this.items = [];
        this.hasEmptySearchResult = false;
        this.inputValue = '';
        this.input.value = '';
        this.setCollection();
        const api = this.getApi();
        api.clearValue();
        api.setOpen(false);
        this.setLoading(false);
        this.onSelect(null);
        this.input.focus();
    }

    cancelSearch() {
        clearTimeout(this.searchTimer);
        this.searchTimer = null;
        this.controller?.abort();
        this.controller = null;
        this.requestVersion += 1;
        this.setLoading(false);
    }

    search(value) {
        const query = value.trim();
        this.cancelSearch();
        const requestVersion = this.requestVersion;
        this.items = [];
        this.hasEmptySearchResult = false;
        this.setCollection();

        if (query.length < MINIMUM_QUERY_LENGTH) {
            this.getApi().setOpen(false);
            return;
        }

        this.searchTimer = setTimeout(() => {
            this.searchTimer = null;
            this.performSearch(query, requestVersion);
        }, SEARCH_DEBOUNCE_MS);
    }

    async performSearch(query, requestVersion) {
        if (requestVersion !== this.requestVersion) {
            return;
        }
        const controller = new AbortController();
        this.controller = controller;
        this.setLoading(true);
        const params = new URLSearchParams({query});

        try {
            const response = await fetch(`/api/city/search?${params.toString()}`, {
                signal: controller.signal,
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const cities = await response.json();
            if (controller.signal.aborted || requestVersion !== this.requestVersion) {
                return;
            }
            this.items = cities.filter((city) => city?.id && city?.title);
            this.hasEmptySearchResult = this.items.length === 0;
            this.setCollection();
            this.openAndHighlightResults();
        } catch (error) {
            if (error.name !== 'AbortError' && requestVersion === this.requestVersion) {
                this.items = [];
                this.hasEmptySearchResult = false;
                this.setCollection();
                this.getApi().setOpen(false);
                this.onError(error);
            }
        } finally {
            if (requestVersion === this.requestVersion) {
                this.setLoading(false);
            }
        }
    }

    setCollection() {
        this.collection = combobox.collection({
            items: this.items,
            itemToString: (city) => city.title,
            itemToValue: (city) => String(city.id),
        });
        this.machine?.updateProps({
            collection: this.collection,
            inputValue: this.inputValue,
        });
    }

    openAndHighlightResults(api = this.getApi()) {
        api.setOpen(this.items.length > 0 || this.hasEmptySearchResult);
        if (this.items.length > 0) {
            this.machine.send({
                type: 'HIGHLIGHTED_VALUE.SET',
                value: String(this.items[0].id),
            });
        }
    }

    setLoading(isLoading) {
        if (this.loading) {
            this.loading.hidden = !isLoading;
        }
    }

    getApi() {
        return combobox.connect(this.machine.service, normalizeProps);
    }

    render() {
        if (!this.machine) {
            return;
        }

        this.clearProps();
        const api = this.getApi();
        this.clearButton && (this.clearButton.hidden = !this.inputValue);
        this.propCleanups = [
            spreadProps(this.root, api.getRootProps(), this.input.id),
            spreadProps(this.control, api.getControlProps(), this.input.id),
            spreadProps(this.input, api.getInputProps(), this.input.id),
            ...this.renderItems(api),
            spreadProps(this.results, api.getContentProps(), this.input.id),
        ];
    }

    renderItems(api) {
        this.results.replaceChildren();
        if (this.hasEmptySearchResult) {
            const emptyState = document.createElement('li');
            emptyState.className = 'cursor-default rounded-field px-3 py-2 text-sm text-base-content/70';
            emptyState.dataset.cityComboboxEmpty = '';
            emptyState.setAttribute('role', 'option');
            emptyState.setAttribute('aria-disabled', 'true');
            emptyState.textContent = 'Города не найдены';
            this.results.append(emptyState);
            return [];
        }
        return this.items.map((city) => {
            const item = document.createElement('li');
            const state = api.getItemState({item: city});
            item.className = 'cursor-pointer rounded-field px-3 py-2 text-sm text-base-content';
            item.classList.toggle('bg-base-300', state.highlighted);
            const cleanup = spreadProps(item, api.getItemProps({item: city}), this.input.id);

            const title = document.createElement('span');
            title.className = 'block font-medium';
            title.textContent = city.title;
            item.append(title);

            const meta = [city.region, city.country].filter(Boolean).join(', ');
            if (meta) {
                const details = document.createElement('span');
                details.className = 'block text-xs text-base-content/70';
                details.textContent = meta;
                item.append(details);
            }
            this.results.append(item);
            return cleanup;
        });
    }

    clearProps() {
        this.propCleanups.forEach((cleanup) => cleanup());
        this.propCleanups = [];
    }
}
