// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import {afterEach, beforeEach, describe, expect, it} from 'vitest';

describe('city_search', () => {
    beforeEach(async () => {
        document.body.innerHTML = '';
        await import('./city_search.js');
    });

    afterEach(() => {
        document.body.innerHTML = '';
    });

    it('binds the combobox created by the list refresh lifecycle event', () => {
        const root = document.createElement('section');
        root.innerHTML = '<div id="city-search-combobox"></div>';
        document.body.append(root);

        document.dispatchEvent(new CustomEvent('visited-city-list-refreshed', {
            detail: {root},
        }));

        expect(root.querySelector('#city-search-combobox').dataset.mgCitySearchBound).toBe('1');
    });
});
