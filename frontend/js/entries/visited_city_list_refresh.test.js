// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';

const mocks = vi.hoisted(() => ({
    showDangerToast: vi.fn(),
    showSuccessToast: vi.fn(),
}));

vi.mock('../components/toast.js', () => ({
    showDangerToast: mocks.showDangerToast,
    showSuccessToast: mocks.showSuccessToast,
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
    });

    it('does nothing when the page has no refresh container', () => {
        const event = new CustomEvent('city-added', {
            cancelable: true,
            detail: {city: {name: 'Новый город'}},
        });

        expect(document.dispatchEvent(event)).toBe(true);
        expect(fetch).not.toHaveBeenCalled();
        expect(mocks.showSuccessToast).not.toHaveBeenCalled();
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

        const event = new CustomEvent('city-added', {
            cancelable: true,
            detail: {city: {name: 'Новый город'}},
        });

        expect(document.dispatchEvent(event)).toBe(false);
        await vi.waitFor(() => {
            expect(document.querySelector('[data-visited-city-refresh]').textContent).toContain('Новый список');
        });

        expect(fetch).toHaveBeenCalledWith(`${window.location.origin}/region/1/list/fragment?filter=visited&page=2`);
        expect(mocks.showSuccessToast).toHaveBeenCalledWith(
            'Успешно',
            'Город Новый город успешно добавлен как посещённый',
        );
    });

    it('refreshes after a repeat visit', async () => {
        document.body.innerHTML = '<section data-visited-city-refresh data-fragment-url="/collection/1/list/fragment">Старый список</section>';
        fetch.mockResolvedValue({
            ok: true,
            text: vi.fn().mockResolvedValue(
                '<section data-visited-city-refresh data-fragment-url="/collection/1/list/fragment">Новый список</section>',
            ),
        });

        document.dispatchEvent(new CustomEvent('city-added', {
            cancelable: true,
            detail: {city: {name: 'Повторный город', number_of_visits: 2}},
        }));

        await vi.waitFor(() => {
            expect(document.querySelector('[data-visited-city-refresh]').textContent).toContain('Новый список');
        });
    });

    it('keeps the current container when the fragment request fails', async () => {
        document.body.innerHTML = '<section data-visited-city-refresh data-fragment-url="/city/all/list/fragment">Старый список</section>';
        fetch.mockResolvedValue({ok: false, status: 500});

        document.dispatchEvent(new CustomEvent('city-added', {cancelable: true}));

        await vi.waitFor(() => expect(mocks.showDangerToast).toHaveBeenCalledOnce());

        expect(document.querySelector('[data-visited-city-refresh]').textContent).toContain('Старый список');
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
});
