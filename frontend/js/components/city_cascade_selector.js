/**
 * ---------------------------------------------
 *
 * Copyright © Egor Vavilov (Shecspi)
 * Licensed under the Apache License, Version 2.0
 *
 * ----------------------------------------------
 */

export class CityCascadeSelector {
    constructor(root, {
        onChange = () => {}, onError = () => {}, updateOptions = null, locationValueMode = 'id',
    } = {}) {
        this.root = root;
        this.onChange = onChange;
        this.onError = onError;
        this.updateOptions = updateOptions;
        this.locationValueMode = locationValueMode;
        this.countrySelect = root.querySelector('[data-city-country]');
        this.regionSelect = root.querySelector('[data-city-region]');
        this.citySelect = root.querySelector('[data-city]');
        this.countriesController = null;
        this.countryController = null;
        this.regionController = null;
        this.countryItems = [];
        this.regionItems = [];
        this.boundCountryChange = () => this.loadForCountry();
        this.boundRegionChange = () => this.loadForRegion();
    }

    async init({loadCountries = true, reset = true} = {}) {
        if (!this.countrySelect || !this.regionSelect) {
            return;
        }

        this.countrySelect.addEventListener('change', this.boundCountryChange);
        this.regionSelect.addEventListener('change', this.boundRegionChange);
        if (reset) {
            this.setOptions(this.regionSelect, [], 'Выберите регион', true);
            this.setOptions(this.citySelect, [], 'Выберите город', true);
        }

        if (loadCountries) {
            await this.loadCountries();
        }
    }

    destroy() {
        this.countriesController?.abort();
        this.countriesController = null;
        this.countryController?.abort();
        this.regionController?.abort();
        this.countrySelect?.removeEventListener('change', this.boundCountryChange);
        this.regionSelect?.removeEventListener('change', this.boundRegionChange);
    }

    async loadCountries() {
        this.countriesController?.abort();
        const controller = new AbortController();
        this.countriesController = controller;
        try {
            const response = await fetch('/api/country/list_by_cities', {
                signal: controller.signal,
            });
            if (!response.ok) {
                throw new Error('Не удалось загрузить список стран');
            }
            const countries = await response.json();
            if (controller.signal.aborted || this.countriesController !== controller) {
                return;
            }
            this.setOptions(this.countrySelect, countries, 'Выберите страну');
        } catch (error) {
            if (error.name !== 'AbortError' && !controller.signal.aborted
                && this.countriesController === controller) {
                this.onError(error);
            }
        } finally {
            if (this.countriesController === controller) {
                this.countriesController = null;
            }
        }
    }

    async loadForCountry() {
        const countryValue = this.countrySelect.value;
        this.countryController?.abort();
        this.regionController?.abort();
        this.countryController = null;
        this.regionController = null;
        this.setOptions(this.regionSelect, [], 'Выберите регион', true);
        this.setOptions(this.citySelect, [], 'Выберите город', true);

        if (!countryValue) {
            this.onChange(this.value);
            return;
        }

        const controller = new AbortController();
        this.countryController = controller;
        this.setOptions(this.regionSelect, [], 'Загрузка...', true);
        this.onChange(this.value);

        try {
            const regionsResponse = await fetch(this.getRegionsUrl(countryValue), {
                signal: controller.signal,
            });
            if (!regionsResponse.ok) {
                throw new Error('Не удалось загрузить список регионов');
            }
            const regions = await regionsResponse.json();
            if (controller.signal.aborted || this.countrySelect.value !== countryValue) {
                return;
            }

            if (regions.length > 0) {
                this.setOptions(this.regionSelect, regions, 'Выберите регион');
                return;
            }

            if (!this.citySelect) {
                this.setOptions(this.regionSelect, [], 'Нет регионов', true);
                return;
            }

            const countryId = this.getSelectedItemId(this.countrySelect);
            const citiesResponse = await fetch(`/api/city/list_by_country?country_id=${countryId}`, {
                signal: controller.signal,
            });
            if (!citiesResponse.ok) {
                throw new Error('Не удалось загрузить список городов');
            }
            const cities = await citiesResponse.json();
            if (controller.signal.aborted || this.countrySelect.value !== countryValue) {
                return;
            }
            this.setOptions(this.regionSelect, [], 'Нет регионов', true);
            if (cities.length === 0) {
                this.setOptions(this.citySelect, [], 'Нет городов', true);
                this.onChange(this.value);
                return;
            }
            this.setOptions(this.citySelect, cities, 'Выберите город', false, true);
            this.onChange(this.value);
        } catch (error) {
            if (error.name !== 'AbortError') {
                this.setOptions(this.regionSelect, [], 'Выберите регион', true);
                this.setOptions(this.citySelect, [], 'Выберите город', true);
                this.onError(error);
            }
        }
    }

    async loadForRegion() {
        const regionValue = this.regionSelect.value;
        this.regionController?.abort();
        this.regionController = null;
        this.setOptions(this.citySelect, [], 'Выберите город', true);

        if (!regionValue) {
            this.onChange(this.value);
            return;
        }

        if (!this.citySelect) {
            this.onChange(this.value);
            return;
        }

        const controller = new AbortController();
        this.regionController = controller;
        this.setOptions(this.citySelect, [], 'Загрузка...', true);
        const regionId = this.getSelectedItemId(this.regionSelect);

        try {
            const response = await fetch(`/api/city/list_by_region?region_id=${regionId}`, {
                signal: controller.signal,
            });
            if (!response.ok) {
                throw new Error('Не удалось загрузить список городов');
            }
            const cities = await response.json();
            if (controller.signal.aborted || this.regionSelect.value !== regionValue) {
                return;
            }
            if (cities.length === 0) {
                this.setOptions(this.citySelect, [], 'Нет городов', true);
                this.onChange(this.value);
                return;
            }
            this.setOptions(this.citySelect, cities, 'Выберите город', false, true);
            this.onChange(this.value);
        } catch (error) {
            if (error.name !== 'AbortError') {
                this.setOptions(this.citySelect, [], 'Выберите город', true);
                this.onError(error);
            }
        }
    }

    get value() {
        const cityId = this.citySelect?.value || '';
        if (this.locationValueMode === 'code') {
            return {
                countryCode: this.countrySelect?.value || '',
                regionCode: this.regionSelect?.value || '',
                cityId,
            };
        }
        return {
            countryId: this.countrySelect?.value || '',
            regionId: this.regionSelect?.value || '',
            cityId,
        };
    }

    getOptionValue(select, item) {
        if (this.locationValueMode === 'code' && select === this.countrySelect) {
            return String(item.code);
        }
        if (this.locationValueMode === 'code' && select === this.regionSelect) {
            return String(item.iso3166);
        }
        return String(item.id);
    }

    getRegionsUrl(countryValue) {
        if (this.locationValueMode === 'code') {
            return `/api/region/list/${encodeURIComponent(countryValue)}/`;
        }
        return `/api/region/list?country_id=${encodeURIComponent(countryValue)}`;
    }

    getSelectedItemId(select) {
        if (this.locationValueMode === 'id') {
            return select.value;
        }
        const items = select === this.countrySelect ? this.countryItems : this.regionItems;
        const item = items.find((candidate) => this.getOptionValue(select, candidate) === select.value);
        return item ? String(item.id) : '';
    }

    setOptions(select, items, placeholder, disabled = false, selectFirst = false) {
        if (!select) {
            return;
        }
        if (select === this.countrySelect) {
            this.countryItems = items;
        }
        if (select === this.regionSelect) {
            this.regionItems = items;
        }
        if (this.updateOptions) {
            this.updateOptions(
                select,
                items,
                placeholder,
                disabled,
                selectFirst,
                (item) => this.getOptionValue(select, item),
            );
            return;
        }
        select.replaceChildren();
        const placeholderOption = document.createElement('option');
        placeholderOption.value = '';
        placeholderOption.textContent = placeholder;
        select.add(placeholderOption);
        items.forEach((item) => {
            const option = document.createElement('option');
            option.value = this.getOptionValue(select, item);
            option.textContent = item.name || item.title;
            select.add(option);
        });
        select.disabled = disabled;
        select.value = selectFirst && items.length > 0 ? this.getOptionValue(select, items[0]) : '';
    }
}
