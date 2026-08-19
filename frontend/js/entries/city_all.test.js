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

vi.mock('../components/initCountrySelect', () => ({
    initCountrySelect: vi.fn(),
}));

vi.mock('../components/toast.js', () => ({
    showDangerToast: mocks.showDangerToast,
    showSuccessToast: mocks.showSuccessToast,
}));

describe('city_all', () => {
    let cityAddedListeners;
    let domContentLoadedListeners;

    beforeEach(async () => {
        cityAddedListeners = [];
        domContentLoadedListeners = [];
        const addDocumentEventListener = document.addEventListener.bind(document);
        vi.spyOn(document, 'addEventListener').mockImplementation((...args) => {
            if (args[0] === 'city-added') {
                cityAddedListeners.push(args[1]);
            }
            if (args[0] === 'DOMContentLoaded') {
                domContentLoadedListeners.push(args[1]);
            }

            return addDocumentEventListener(...args);
        });
        vi.resetModules();
        vi.clearAllMocks();
        sessionStorage.clear();
        document.body.innerHTML = '';
        vi.stubGlobal('fetch', vi.fn());
        vi.spyOn(console, 'error').mockImplementation(() => {});

        await import('./city_all.js');
    });

    afterEach(() => {
        cityAddedListeners.forEach((listener) => {
            document.removeEventListener('city-added', listener);
        });
        domContentLoadedListeners.forEach((listener) => {
            document.removeEventListener('DOMContentLoaded', listener);
        });
        document.addEventListener.mockRestore();
        vi.restoreAllMocks();
        vi.unstubAllGlobals();
        sessionStorage.clear();
    });

    it('обновляет список и счётчики после добавления города без перезагрузки', async () => {
        document.body.innerHTML = `
            <div id="toolbar">
                <div class="toolbar-stats"><strong>1</strong></div>
                <button type="button" class="toolbar-controls">Фильтры</button>
            </div>
            <div id="city-list-results" data-fragment-url="/city/all/list/fragment">
                <div>Старый список</div>
            </div>
        `;
        fetch.mockResolvedValue({
            ok: true,
            text: vi.fn().mockResolvedValue(`
                <div class="toolbar-stats"><strong>2</strong></div>
                <div id="city-list-results" data-fragment-url="/city/all/list/fragment"><div>Новый список</div></div>
            `),
        });
        const initialUrl = window.location.href;
        const toolbarControls = document.querySelector('.toolbar-controls');
        const cityAddedEvent = new CustomEvent('city-added', {
            cancelable: true,
            detail: {city: {name: 'Новый город'}},
        });
        const isNotCancelled = document.dispatchEvent(cityAddedEvent);

        expect(isNotCancelled).toBe(false);
        await vi.waitFor(() => expect(document.querySelector('#city-list-results').textContent).toContain('Новый список'));

        expect(fetch).toHaveBeenCalledWith(
            `${window.location.origin}/city/all/list/fragment${window.location.search}`
        );
        expect(document.querySelector('.toolbar-stats').textContent).toContain('2');
        expect(document.querySelector('.toolbar-controls')).toBe(toolbarControls);
        expect(window.location.href).toBe(initialUrl);
        expect(mocks.showSuccessToast).toHaveBeenCalledWith(
            'Успешно',
            'Город Новый город успешно добавлен как посещённый'
        );
    });

    it('сохраняет текущий список и сообщает об ошибке синхронизации', async () => {
        document.body.innerHTML = (
            '<div id="city-list-results" data-fragment-url="/city/all/list/fragment">'
            + '<div>Старый список</div></div>'
        );
        fetch.mockResolvedValue({ok: false, status: 500});

        document.dispatchEvent(new CustomEvent('city-added', {
            cancelable: true,
            detail: {city: {name: 'Новый город'}},
        }));

        await vi.waitFor(() => expect(mocks.showDangerToast).toHaveBeenCalledOnce());

        expect(document.querySelector('#city-list-results').textContent).toContain('Старый список');
        expect(mocks.showSuccessToast).toHaveBeenCalledWith(
            'Успешно',
            'Город Новый город успешно добавлен как посещённый'
        );
        expect(mocks.showDangerToast).toHaveBeenCalledWith(
            'Ошибка',
            'Не удалось обновить список городов. Обновите страницу вручную.'
        );
    });

    it('сохраняет текущие блоки при неполном фрагменте', async () => {
        document.body.innerHTML = `
            <div class="toolbar-stats"><strong>1</strong></div>
            <div id="city-list-results" data-fragment-url="/city/all/list/fragment"><div>Старый список</div></div>
        `;
        fetch.mockResolvedValue({
            ok: true,
            text: vi.fn().mockResolvedValue(
                '<div id="city-list-results"><div>Новый список</div></div>'
            ),
        });

        document.dispatchEvent(new CustomEvent('city-added', {cancelable: true}));

        await vi.waitFor(() => expect(mocks.showDangerToast).toHaveBeenCalledOnce());

        expect(document.querySelector('#city-list-results').textContent).toContain('Старый список');
        expect(document.querySelector('.toolbar-stats').textContent).toContain('1');
    });
});
