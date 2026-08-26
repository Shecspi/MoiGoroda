// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';

const mocks = vi.hoisted(() => ({
    initCountrySelect: vi.fn(),
}));

vi.mock('../components/initCountrySelect', () => ({
    initCountrySelect: mocks.initCountrySelect,
}));

describe('city_all', () => {
    let domContentLoadedListeners;
    let refreshListeners;

    beforeEach(async () => {
        domContentLoadedListeners = [];
        refreshListeners = [];
        const addDocumentEventListener = document.addEventListener.bind(document);
        vi.spyOn(document, 'addEventListener').mockImplementation((...args) => {
            if (args[0] === 'DOMContentLoaded') {
                domContentLoadedListeners.push(args[1]);
            }
            if (args[0] === 'visited-city-list-refreshed') {
                refreshListeners.push(args[1]);
            }

            return addDocumentEventListener(...args);
        });
        vi.resetModules();
        vi.clearAllMocks();
        document.body.innerHTML = '<div id="toolbar"></div>';

        await import('./city_all.js');
        vi.clearAllMocks();
    });

    afterEach(() => {
        domContentLoadedListeners.forEach((listener) => {
            document.removeEventListener('DOMContentLoaded', listener);
        });
        refreshListeners.forEach((listener) => {
            document.removeEventListener('visited-city-list-refreshed', listener);
        });
        document.addEventListener.mockRestore();
        vi.restoreAllMocks();
    });

    it('initializes city list controls on the initial page load', async () => {
        document.dispatchEvent(new Event('DOMContentLoaded'));

        await vi.waitFor(() => {
            expect(mocks.initCountrySelect).toHaveBeenCalledOnce();
            expect(document.getElementById('toolbar').classList).toContain('toolbar-loaded');
        });
    });

    it('initializes city list controls after the refresh lifecycle event', async () => {
        document.dispatchEvent(new CustomEvent('visited-city-list-refreshed', {
            detail: {root: document.body},
        }));

        await vi.waitFor(() => {
            expect(mocks.initCountrySelect).toHaveBeenCalledOnce();
            expect(document.getElementById('toolbar').classList).toContain('toolbar-loaded');
        });
    });
});
