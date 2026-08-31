// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';

const mocks = vi.hoisted(() => ({
    showDangerToast: vi.fn(),
    showVisitedCityCreatedToast: vi.fn(),
}));

vi.mock('../components/toast.js', () => ({
    showDangerToast: mocks.showDangerToast,
}));

vi.mock('../components/visited_city_created_toast.js', () => ({
    showVisitedCityCreatedToast: mocks.showVisitedCityCreatedToast,
}));

describe('visited_city_list_refresh', () => {
    let cityAddedListeners;

    beforeEach(async () => {
        cityAddedListeners = [];
        const addDocumentEventListener = document.addEventListener.bind(document);
        vi.spyOn(document, 'addEventListener').mockImplementation((...args) => {
            if (args[0] === 'city-added') {
                cityAddedListeners.push(args[1]);
            }

            return addDocumentEventListener(...args);
        });
        vi.resetModules();
        vi.clearAllMocks();
        document.body.innerHTML = '';
        vi.stubGlobal('fetch', vi.fn());
        vi.spyOn(console, 'error').mockImplementation(() => {});

        await import('./visited_city_list_refresh.js');
    });

    afterEach(() => {
        cityAddedListeners.forEach((listener) => {
            document.removeEventListener('city-added', listener);
        });
        document.addEventListener.mockRestore();
        vi.restoreAllMocks();
        vi.unstubAllGlobals();
        delete window.MGUi;
    });

    it('does nothing when the page has no refresh container', () => {
        const event = new CustomEvent('city-added', {
            cancelable: true,
            detail: {city: {name: 'Новый город'}},
        });

        expect(document.dispatchEvent(event)).toBe(true);
        expect(fetch).not.toHaveBeenCalled();
        expect(mocks.showVisitedCityCreatedToast).not.toHaveBeenCalled();
    });

    it('refreshes the full container and preserves query parameters', async () => {
        window.history.replaceState({}, '', '/region/1/list?filter=visited&page=2');
        document.body.innerHTML = `
            <section data-visited-city-refresh data-fragment-url="/region/1/list/fragment">
                <div>Старый список</div>
            </section>
        `;
        fetch.mockResolvedValue({
            ok: true,
            text: vi.fn().mockResolvedValue(`
                <section data-visited-city-refresh data-fragment-url="/region/1/list/fragment">
                    <div>Новый список</div>
                </section>
            `),
        });

        const collectionContext = {
            city: {id: 1, title: 'Новый город', url: '/city/1'},
            common_collections: {count: 0, single: null, catalog_url: '/collection/'},
        };
        const event = new CustomEvent('city-added', {
            cancelable: true,
            detail: {city: {name: 'Новый город'}, collectionContext},
        });

        expect(document.dispatchEvent(event)).toBe(false);
        await vi.waitFor(() => {
            expect(document.querySelector('[data-visited-city-refresh]').textContent).toContain('Новый список');
        });

        expect(fetch).toHaveBeenCalledWith(`${window.location.origin}/region/1/list/fragment?filter=visited&page=2`);
        expect(mocks.showVisitedCityCreatedToast).toHaveBeenCalledWith(collectionContext);
    });

    it.each([
        '/city/all/list/fragment',
        '/region/1/list/fragment',
        '/region/all/list/fragment',
        '/collection/fragment',
        '/collection/1/list/fragment',
        '/collection/personal/fragment',
        '/collection/personal/00000000-0000-0000-0000-000000000001/list/fragment',
    ])('refreshes %s after new and repeat visits', async (fragmentUrl) => {
        window.history.replaceState({}, '', '/city/all/list?filter=not_visited');
        document.body.innerHTML = `<section data-visited-city-refresh data-fragment-url="${fragmentUrl}">Старый список</section>`;
        fetch
            .mockResolvedValueOnce({
                ok: true,
                text: vi.fn().mockResolvedValue(
                    `<section data-visited-city-refresh data-fragment-url="${fragmentUrl}">После нового посещения</section>`,
                ),
            })
            .mockResolvedValueOnce({
                ok: true,
                text: vi.fn().mockResolvedValue(
                    `<section data-visited-city-refresh data-fragment-url="${fragmentUrl}">После повторного посещения</section>`,
                ),
            });

        document.dispatchEvent(new CustomEvent('city-added', {
            cancelable: true,
            detail: {city: {name: 'Новый город'}},
        }));
        await vi.waitFor(() => {
            expect(document.querySelector('[data-visited-city-refresh]').textContent).toContain('После нового посещения');
        });

        document.dispatchEvent(new CustomEvent('city-added', {
            cancelable: true,
            detail: {city: {name: 'Новый город', number_of_visits: 2}},
        }));
        await vi.waitFor(() => {
            expect(document.querySelector('[data-visited-city-refresh]').textContent).toContain('После повторного посещения');
        });

        expect(fetch).toHaveBeenNthCalledWith(
            1,
            `${window.location.origin}${fragmentUrl}?filter=not_visited`,
        );
        expect(fetch).toHaveBeenNthCalledWith(
            2,
            `${window.location.origin}${fragmentUrl}?filter=not_visited`,
        );
    });

    it('replaces the empty state with refreshed results', async () => {
        document.body.innerHTML = `
            <section data-visited-city-refresh data-fragment-url="/collection/personal/1/list/fragment">
                <p>В этой коллекции пока нет городов</p>
            </section>
        `;
        fetch.mockResolvedValue({
            ok: true,
            text: vi.fn().mockResolvedValue(`
                <section data-visited-city-refresh data-fragment-url="/collection/personal/1/list/fragment">
                    <article>Посещённый город</article>
                </section>
            `),
        });

        document.dispatchEvent(new CustomEvent('city-added', {
            cancelable: true,
            detail: {city: {name: 'Новый город'}},
        }));

        await vi.waitFor(() => {
            expect(document.querySelector('[data-visited-city-refresh]').textContent).toContain('Посещённый город');
        });
        expect(document.body.textContent).not.toContain('В этой коллекции пока нет городов');
    });

    it('reinitializes controls after replacing the refresh container', async () => {
        document.body.innerHTML = '<section data-visited-city-refresh data-fragment-url="/city/all/list/fragment">Старый список</section>';
        window.MGUi = {
            destroyAll: vi.fn(),
            initAll: vi.fn(),
        };
        const refreshed = vi.fn();
        document.addEventListener('visited-city-list-refreshed', refreshed);
        fetch.mockResolvedValue({
            ok: true,
            text: vi.fn().mockResolvedValue(
                '<section data-visited-city-refresh data-fragment-url="/city/all/list/fragment">Новый список</section>',
            ),
        });

        const previousContainer = document.querySelector('[data-visited-city-refresh]');
        document.dispatchEvent(new CustomEvent('city-added', {cancelable: true}));

        await vi.waitFor(() => expect(refreshed).toHaveBeenCalledOnce());

        const updatedContainer = document.querySelector('[data-visited-city-refresh]');
        expect(window.MGUi.destroyAll).toHaveBeenCalledWith(previousContainer);
        expect(window.MGUi.initAll).toHaveBeenCalledWith(updatedContainer);
        expect(refreshed).toHaveBeenCalledWith(expect.objectContaining({
            detail: {root: updatedContainer},
        }));
        document.removeEventListener('visited-city-list-refreshed', refreshed);
    });

    it('keeps the current container when the fragment request fails', async () => {
        document.body.innerHTML = '<section data-visited-city-refresh data-fragment-url="/city/all/list/fragment">Старый список</section>';
        fetch.mockResolvedValue({ok: false, status: 500});

        document.dispatchEvent(new CustomEvent('city-added', {cancelable: true}));

        await vi.waitFor(() => expect(mocks.showDangerToast).toHaveBeenCalledOnce());

        expect(document.querySelector('[data-visited-city-refresh]').textContent).toContain('Старый список');
        expect(mocks.showVisitedCityCreatedToast).toHaveBeenCalledOnce();
        expect(mocks.showDangerToast).toHaveBeenCalledWith(
            'Ошибка',
            'Не удалось обновить список. Обновите страницу вручную.',
        );
    });

    it('keeps the current container when the fragment is incomplete', async () => {
        document.body.innerHTML = '<section data-visited-city-refresh data-fragment-url="/city/all/list/fragment">Старый список</section>';
        fetch.mockResolvedValue({
            ok: true,
            text: vi.fn().mockResolvedValue('<div>Неполный ответ</div>'),
        });

        document.dispatchEvent(new CustomEvent('city-added', {cancelable: true}));

        await vi.waitFor(() => expect(mocks.showDangerToast).toHaveBeenCalledOnce());

        expect(document.querySelector('[data-visited-city-refresh]').textContent).toContain('Старый список');
    });

    it('restores the current container when refreshed controls fail to initialize', async () => {
        document.body.innerHTML = '<section data-visited-city-refresh data-fragment-url="/city/all/list/fragment">Старый список</section>';
        window.MGUi = {
            destroyAll: vi.fn(),
            initAll: vi.fn((root) => {
                if (root.textContent.includes('Новый список')) {
                    throw new Error('init failed');
                }
            }),
        };
        fetch.mockResolvedValue({
            ok: true,
            text: vi.fn().mockResolvedValue(
                '<section data-visited-city-refresh data-fragment-url="/city/all/list/fragment">Новый список</section>',
            ),
        });

        document.dispatchEvent(new CustomEvent('city-added', {cancelable: true}));

        await vi.waitFor(() => expect(mocks.showDangerToast).toHaveBeenCalledOnce());

        expect(document.querySelector('[data-visited-city-refresh]').textContent).toContain('Старый список');
    });

    it('shows success before the asynchronous refresh finishes', () => {
        document.body.innerHTML = '<section data-visited-city-refresh data-fragment-url="/city/all/list/fragment">Старый список</section>';
        fetch.mockReturnValue(new Promise(() => {}));
        const collectionContext = {
            city: {id: 1, title: 'Новый город', url: '/city/1'},
            common_collections: {count: 0, single: null, catalog_url: '/collection/'},
        };

        const event = new CustomEvent('city-added', {
            cancelable: true,
            detail: {collectionContext},
        });
        const notCancelled = document.dispatchEvent(event);

        expect(notCancelled).toBe(false);
        expect(mocks.showVisitedCityCreatedToast).toHaveBeenCalledWith(collectionContext);
    });
});
