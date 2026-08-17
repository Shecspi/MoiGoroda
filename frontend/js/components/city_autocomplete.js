/**
 * ---------------------------------------------
 *
 * Copyright © Egor Vavilov (Shecspi)
 * Licensed under the Apache License, Version 2.0
 *
 * ----------------------------------------------
 */

const MINIMUM_QUERY_LENGTH = 3;

export class CityAutocomplete {
    constructor(root, {onSelect = () => {}, onError = () => {}} = {}) {
        this.root = root;
        this.onSelect = onSelect;
        this.onError = onError;
        this.input = root.querySelector('[data-city-autocomplete-input]');
        this.results = root.querySelector('[data-city-autocomplete-results]');
        this.loading = root.querySelector('[data-city-autocomplete-loading]');
        this.country = '';
        this.region = '';
        this.controller = null;
        this.requestVersion = 0;
        this.activeIndex = -1;
        this.items = [];
        this.boundInput = () => this.search();
        this.boundKeyDown = (event) => this.handleKeyDown(event);
    }

    init() {
        if (!this.input || !this.results) {
            return;
        }

        this.input.addEventListener('input', this.boundInput);
        this.input.addEventListener('keydown', this.boundKeyDown);
    }

    destroy() {
        this.controller?.abort();
        this.controller = null;
        this.input?.removeEventListener('input', this.boundInput);
        this.input?.removeEventListener('keydown', this.boundKeyDown);
    }

    setFilters({country = '', region = ''}) {
        this.country = country;
        this.region = region;
        this.controller?.abort();
        this.controller = null;
        this.requestVersion += 1;
        this.input.value = '';
        this.clearResults();
        this.onSelect(null);
    }

    async search() {
        const query = this.input.value.trim();
        this.controller?.abort();
        this.controller = null;
        this.requestVersion += 1;
        const requestVersion = this.requestVersion;
        this.activeIndex = -1;
        this.onSelect(null);

        if (query.length < MINIMUM_QUERY_LENGTH) {
            this.clearResults();
            return;
        }

        const controller = new AbortController();
        this.controller = controller;
        this.setLoading(true);
        const params = new URLSearchParams({query});
        if (this.region) {
            params.set('region', this.region);
        } else if (this.country) {
            params.set('country', this.country);
        }

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
            this.renderResults(cities);
        } catch (error) {
            if (error.name !== 'AbortError' && requestVersion === this.requestVersion) {
                this.clearResults();
                this.onError(error);
            }
        } finally {
            if (requestVersion === this.requestVersion) {
                this.setLoading(false);
            }
        }
    }

    renderResults(cities) {
        this.items = cities.filter((city) => city?.id && city?.title);
        this.results.replaceChildren();
        this.items.forEach((city, index) => {
            const item = document.createElement('li');
            const option = document.createElement('button');
            option.type = 'button';
            option.className = 'w-full font-normal';
            option.setAttribute('role', 'option');
            option.id = `${this.input.id}-option-${city.id}`;
            option.setAttribute('aria-selected', 'false');

            const content = document.createElement('span');
            content.className = 'flex min-w-0 flex-col items-start';
            const title = document.createElement('span');
            title.className = 'font-medium';
            title.textContent = city.title;
            content.append(title);
            const meta = [city.region, city.country].filter(Boolean).join(', ');
            if (meta) {
                const details = document.createElement('span');
                details.className = 'text-xs text-base-content/70';
                details.textContent = meta;
                content.append(details);
            }
            option.append(content);
            option.addEventListener('click', () => this.select(city));
            item.append(option);
            this.results.append(item);
        });
        this.results.hidden = this.items.length === 0;
        this.input.setAttribute('aria-expanded', String(this.items.length > 0));
    }

    select(city) {
        this.input.value = city.title;
        this.clearResults();
        this.onSelect(city);
    }

    clearResults() {
        this.items = [];
        this.activeIndex = -1;
        this.results?.replaceChildren();
        if (this.results) {
            this.results.hidden = true;
        }
        this.input?.setAttribute('aria-expanded', 'false');
        this.input?.removeAttribute('aria-activedescendant');
    }

    setLoading(isLoading) {
        if (this.loading) {
            this.loading.hidden = !isLoading;
        }
    }

    handleKeyDown(event) {
        if (!this.items.length) {
            return;
        }
        if (event.key === 'Escape') {
            this.clearResults();
            return;
        }
        if (event.key !== 'ArrowDown' && event.key !== 'ArrowUp' && event.key !== 'Enter') {
            return;
        }
        if (event.key === 'Enter') {
            if (this.activeIndex < 0) {
                return;
            }
            event.preventDefault();
            this.select(this.items[this.activeIndex]);
            return;
        }
        event.preventDefault();
        if (this.activeIndex < 0) {
            this.activeIndex = event.key === 'ArrowDown' ? 0 : this.items.length - 1;
        } else {
            const delta = event.key === 'ArrowDown' ? 1 : -1;
            this.activeIndex = (this.activeIndex + delta + this.items.length) % this.items.length;
        }
        this.results.querySelectorAll('[role="option"]').forEach((option, index) => {
            const active = index === this.activeIndex;
            option.classList.toggle('dui-menu-focus', active);
            option.setAttribute('aria-selected', String(active));
            if (active) {
                this.input.setAttribute('aria-activedescendant', option.id);
            }
        });
    }
}
