// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import {describe, expect, it, vi} from 'vitest';

describe('filter_city', () => {
    it('binds filter controls created by the list refresh lifecycle event', async () => {
        vi.resetModules();
        document.body.innerHTML = '';
        await import('./filter_city.js');

        const root = document.createElement('section');
        root.innerHTML = `
            <button id="btnOpenFilterSortPanel" type="button"></button>
            <div id="offcanvasRight" class="translate-x-full"></div>
            <div data-hs-overlay-backdrop="#offcanvasRight" class="opacity-0 pointer-events-none"></div>
        `;
        document.body.append(root);

        document.dispatchEvent(new CustomEvent('visited-city-list-refreshed', {
            detail: {root},
        }));
        root.querySelector('#btnOpenFilterSortPanel').click();

        expect(root.querySelector('#offcanvasRight').classList).toContain('translate-x-0');
        expect(root.querySelector('[data-hs-overlay-backdrop]').classList).toContain('opacity-100');
    });
});
