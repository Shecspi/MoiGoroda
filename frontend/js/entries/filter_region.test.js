// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';

describe('filter_region', () => {
    let listeners;

    beforeEach(async () => {
        listeners = [];
        const addDocumentEventListener = document.addEventListener.bind(document);
        vi.spyOn(document, 'addEventListener').mockImplementation((...args) => {
            if (args[0] === 'keydown') {
                listeners.push(args[1]);
            }
            return addDocumentEventListener(...args);
        });
        vi.resetModules();
        document.body.innerHTML = '';
        await import('./filter_region.js');
    });

    afterEach(() => {
        listeners.forEach((listener) => document.removeEventListener('keydown', listener));
        document.addEventListener.mockRestore();
        vi.restoreAllMocks();
    });

    it('binds replacement controls and installs only one Escape listener', () => {
        const root = document.createElement('section');
        root.innerHTML = `
            <button id="btnOpenFilterSortPanel" type="button"></button>
            <div id="offcanvasRight" class="translate-x-full"></div>
            <div data-hs-overlay-backdrop="#offcanvasRight" class="opacity-0 pointer-events-none"></div>
        `;
        document.body.append(root);

        document.dispatchEvent(new CustomEvent('visited-city-list-refreshed', {detail: {root}}));
        document.dispatchEvent(new CustomEvent('visited-city-list-refreshed', {detail: {root}}));
        root.querySelector('#btnOpenFilterSortPanel').click();

        expect(root.querySelector('#offcanvasRight').classList).toContain('translate-x-0');
        expect(listeners).toHaveLength(1);

        document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape'}));
        expect(root.querySelector('#offcanvasRight').classList).toContain('translate-x-full');
    });
});
