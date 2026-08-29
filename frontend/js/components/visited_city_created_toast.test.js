// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import {beforeEach, describe, expect, it, vi} from 'vitest';

const {showDaisyToast} = vi.hoisted(() => ({showDaisyToast: vi.fn()}));

vi.mock('./daisyui_toast.js', () => ({showDaisyToast}));

import {showVisitedCityCreatedToast} from './visited_city_created_toast.js';

const collectionContext = (count, single = null) => ({
    city: {
        id: 42,
        title: '<Тверь>',
        url: '/city/42',
    },
    common_collections: {
        count,
        single,
        catalog_url: '/collection/',
    },
});

describe('showVisitedCityCreatedToast', () => {
    beforeEach(() => showDaisyToast.mockClear());

    it('shows only a safe canonical city link when there are no common collections', () => {
        showVisitedCityCreatedToast(collectionContext(0));

        expect(showDaisyToast).toHaveBeenCalledOnce();
        const options = showDaisyToast.mock.calls[0][0];
        expect(options).toMatchObject({
            type: 'success',
            duration: 5000,
            dismissible: true,
            pauseOnInteraction: true,
        });
        expect(options.content.textContent).toBe('Добавлено посещение: <Тверь>');
        expect(options.content.querySelectorAll('a')).toHaveLength(1);
        expect(options.content.querySelector('a')).toMatchObject({
            textContent: '<Тверь>',
            pathname: '/city/42',
        });
        expect(options.content.querySelector('script')).toBeNull();
    });

    it('links the only common collection and preserves its full accessible title', () => {
        showVisitedCityCreatedToast(collectionContext(1, {
            id: 7,
            title: '<b>Очень длинная коллекция</b>',
            url: '/collection/7/list',
        }));

        const content = showDaisyToast.mock.calls[0][0].content;
        const links = content.querySelectorAll('a');
        expect(content.textContent).toBe(
            'Добавлено посещение: <Тверь>Город входит в коллекцию «<b>Очень длинная коллекция</b>».',
        );
        expect(links).toHaveLength(2);
        expect(links[1]).toMatchObject({
            textContent: '<b>Очень длинная коллекция</b>',
            pathname: '/collection/7/list',
            title: '<b>Очень длинная коллекция</b>',
            tabIndex: 0,
        });
        expect(links[1].getAttribute('href')).toBe('/collection/7/list');
        expect(content.querySelector('b')).toBeNull();
    });

    it.each([
        [2, 'коллекциях'],
        [5, 'коллекциях'],
        [11, 'коллекциях'],
        [21, 'коллекции'],
        [22, 'коллекциях'],
        [25, 'коллекциях'],
    ])('shows the catalog action for %s common collections', (count, noun) => {
        showVisitedCityCreatedToast(collectionContext(count));

        const content = showDaisyToast.mock.calls[0][0].content;
        expect(content.textContent).toBe(
            `Добавлено посещение: <Тверь>Город состоит в ${count} ${noun}. Посмотреть коллекции`,
        );
        expect(content.querySelectorAll('a')).toHaveLength(2);
        expect(content.querySelectorAll('a')[1]).toMatchObject({
            textContent: 'Посмотреть коллекции',
            pathname: '/collection/',
        });
    });
});
