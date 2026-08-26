// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import {beforeEach, describe, expect, it} from 'vitest';

describe('collection_search', () => {
    beforeEach(async () => {
        document.body.innerHTML = '';
        await import('./collection_search.js');
    });

    it('binds replacement search controls once after the list refresh lifecycle event', () => {
        const root = document.createElement('section');
        root.innerHTML = `
            <div id="collection-search-combobox"></div>
            <input id="collection-search">
            <div id="search-overlay"></div>
        `;
        document.body.append(root);

        document.dispatchEvent(new CustomEvent('visited-city-list-refreshed', {detail: {root}}));
        document.dispatchEvent(new CustomEvent('visited-city-list-refreshed', {detail: {root}}));
        root.querySelector('#collection-search').dispatchEvent(new Event('focus'));

        expect(root.querySelector('#collection-search-combobox').dataset.mgCollectionSearchBound).toBe('1');
        expect(root.querySelector('#search-overlay').classList).toContain('active');
    });
});
