// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';

const mocks = vi.hoisted(() => ({initCountrySelect: vi.fn()}));

vi.mock('../components/initCountrySelect', () => ({initCountrySelect: mocks.initCountrySelect}));

describe('region_all', () => {
    let refreshListeners;

    beforeEach(async () => {
        refreshListeners = [];
        const addDocumentEventListener = document.addEventListener.bind(document);
        vi.spyOn(document, 'addEventListener').mockImplementation((...args) => {
            if (args[0] === 'visited-city-list-refreshed') {
                refreshListeners.push(args[1]);
            }
            return addDocumentEventListener(...args);
        });
        vi.resetModules();
        vi.clearAllMocks();
        await import('./region_all.js');
        vi.clearAllMocks();
    });

    afterEach(() => {
        refreshListeners.forEach((listener) => document.removeEventListener('visited-city-list-refreshed', listener));
        document.addEventListener.mockRestore();
        vi.restoreAllMocks();
    });

    it('reinitializes the country select after the list refresh lifecycle event', async () => {
        document.dispatchEvent(new CustomEvent('visited-city-list-refreshed'));

        await vi.waitFor(() => {
            expect(mocks.initCountrySelect).toHaveBeenCalledWith({showAllOption: false});
        });
    });
});
