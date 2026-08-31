/*
 * ---------------------------------------------
 *
 * Copyright © Egor Vavilov (Shecspi)
 * Licensed under the Apache License, Version 2.0
 *
 * ----------------------------------------------
 */

import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';

const mocks = vi.hoisted(() => ({
    showDaisyToast: vi.fn(),
}));

vi.mock('../components/daisyui_toast.js', () => ({
    showDaisyToast: mocks.showDaisyToast,
}));

describe('city_visits', () => {
    let visitListeners;

    beforeEach(async () => {
        visitListeners = [];
        const addDocumentEventListener = document.addEventListener.bind(document);
        vi.spyOn(document, 'addEventListener').mockImplementation((...args) => {
            if (['visited-city-created', 'visited-city-updated'].includes(args[0])) {
                visitListeners.push([args[0], args[1]]);
            }

            return addDocumentEventListener(...args);
        });
        vi.resetModules();
        vi.clearAllMocks();
        vi.stubGlobal('fetch', vi.fn());
        vi.spyOn(console, 'error').mockImplementation(() => {});
        document.body.innerHTML = `
            <section id="user-visits" data-city-id="42" data-fragment-url="/city/42/visits/fragment">
                <strong id="user-visits-count">1</strong>
                <div id="user-visits-list">
                    <article data-visit-id="17">Старая запись</article>
                </div>
            </section>`;
        await import('./city_visits.js');
    });

    afterEach(() => {
        visitListeners.forEach(([type, listener]) => {
            document.removeEventListener(type, listener);
        });
        document.addEventListener.mockRestore();
        console.error.mockRestore();
        vi.unstubAllGlobals();
        delete window.MGUi;
        document.body.innerHTML = '';
    });

    it.each(['visited-city-created', 'visited-city-updated'])('replaces visits with the server fragment after %s for the current city', async (eventName) => {
        window.MGUi = {
            destroyAll: vi.fn(),
            initAll: vi.fn(),
        };
        fetch.mockResolvedValue({
            ok: true,
            text: vi.fn().mockResolvedValue(`
                <section id="user-visits" data-city-id="42" data-fragment-url="/city/42/visits/fragment">
                    <strong id="user-visits-count">2</strong>
                    <div id="user-visits-list">
                        <article data-visit-id="18">Новая серверная запись <button class="delete_city"></button><button data-action="edit-visited-city"></button></article>
                        <article data-visit-id="17"><button class="delete_city"></button><button data-action="edit-visited-city"></button></article>
                    </div>
                    <button data-action="add-city"></button>
                </section>`),
        });
        const previousRoot = document.querySelector('#user-visits');

        document.dispatchEvent(new CustomEvent(eventName, {
            detail: {
                visit: {
                    city: 42,
                },
            },
        }));

        await vi.waitFor(() => {
            expect(document.querySelector('#user-visits-list').textContent).toContain('Новая серверная запись');
        });

        const updatedRoot = document.querySelector('#user-visits');
        expect(fetch).toHaveBeenCalledWith(`${window.location.origin}/city/42/visits/fragment`);
        expect(window.MGUi.destroyAll).toHaveBeenCalledWith(previousRoot);
        expect(window.MGUi.initAll).toHaveBeenCalledWith(updatedRoot);
    });

    it('does not request a fragment for another city', () => {
        document.dispatchEvent(new CustomEvent('visited-city-created', {
            detail: {visit: {city: 7}},
        }));

        expect(fetch).not.toHaveBeenCalled();
        expect(document.querySelector('#user-visits-list').textContent).toContain('Старая запись');
    });

    it.each([
        {error: new Error('Network error')},
        {response: {ok: false, status: 500}},
        {response: {ok: true, text: vi.fn().mockResolvedValue('<main>Неполный ответ</main>')}},
        {response: {ok: true, text: vi.fn().mockResolvedValue('<section id="user-visits" data-city-id="42"></section>')}},
        {response: {ok: true, text: vi.fn().mockResolvedValue(`
            <section id="user-visits" data-city-id="42">
                <strong id="user-visits-count">1</strong>
                <div id="user-visits-list"><article data-visit-id="18"></article></div>
                <button data-action="add-city"></button>
            </section>`)}},
    ])('keeps the previous visits and shows an error toast when the fragment response is invalid', async ({error, response}) => {
        const previousRoot = document.querySelector('#user-visits');
        if (error) {
            fetch.mockRejectedValue(error);
        } else {
            fetch.mockResolvedValue(response);
        }

        document.dispatchEvent(new CustomEvent('visited-city-created', {
            detail: {visit: {city: 42}},
        }));

        await vi.waitFor(() => expect(mocks.showDaisyToast).toHaveBeenCalledOnce());

        expect(document.querySelector('#user-visits')).toBe(previousRoot);
        expect(document.querySelector('#user-visits-list').textContent).toContain('Старая запись');
        expect(mocks.showDaisyToast).toHaveBeenCalledWith({
            type: 'error',
            content: 'Не удалось обновить посещения. Обновите страницу вручную.',
            duration: 5000,
            dismissible: true,
            pauseOnInteraction: true,
        });
    });
});
