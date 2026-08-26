// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import {beforeEach, describe, expect, it, vi} from 'vitest';

const mocks = vi.hoisted(() => ({
    showDangerToast: vi.fn(),
    showSuccessToast: vi.fn(),
}));

vi.mock('../components/get_cookie.js', () => ({getCookie: vi.fn()}));
vi.mock('../components/toast.js', () => mocks);

describe('collection_favorite', () => {
    beforeEach(async () => {
        document.body.innerHTML = '';
        vi.clearAllMocks();
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
            ok: true,
            json: vi.fn().mockResolvedValue({is_favorite: true}),
        }));
        await import('./collection_favorite.js');
    });

    it('binds a replacement favorite control once after the list refresh lifecycle event', async () => {
        const root = document.createElement('section');
        root.innerHTML = `
            <div id="collection-card-4"><button class="favorite-star" data-collection-id="4" data-is-favorite="false"><svg></svg><span class="favorite-text"></span></button></div>
        `;
        document.body.append(root);

        document.dispatchEvent(new CustomEvent('visited-city-list-refreshed', {detail: {root}}));
        document.dispatchEvent(new CustomEvent('visited-city-list-refreshed', {detail: {root}}));
        root.querySelector('.favorite-star').click();

        await vi.waitFor(() => expect(fetch).toHaveBeenCalledOnce());
        expect(fetch).toHaveBeenCalledWith('/api/collection/favorite/4', expect.objectContaining({method: 'POST'}));
        expect(root.querySelector('.favorite-star').dataset.mgFavoriteBound).toBe('1');
    });
});
