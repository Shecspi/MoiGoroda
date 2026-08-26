// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import {beforeEach, describe, expect, it, vi} from 'vitest';

describe('region_search', () => {
    beforeEach(() => {
        vi.resetModules();
        document.body.innerHTML = '';
    });

    it('binds the replacement combobox once after the list refresh lifecycle event', async () => {
        await import('./region_search.js');
        const root = document.createElement('section');
        root.innerHTML = '<div id="region-search-combobox"></div>';
        document.body.append(root);
        const combobox = root.querySelector('#region-search-combobox');

        document.dispatchEvent(new CustomEvent('visited-city-list-refreshed', {detail: {root}}));
        document.dispatchEvent(new CustomEvent('visited-city-list-refreshed', {detail: {root}}));

        expect(combobox.dataset.mgRegionSearchBound).toBe('1');
    });
});
