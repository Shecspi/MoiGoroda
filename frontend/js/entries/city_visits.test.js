/**
 * ---------------------------------------------
 *
 * Copyright © Egor Vavilov (Shecspi)
 * Licensed under the Apache License, Version 2.0
 *
 * ----------------------------------------------
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

describe('city_visits', () => {
    beforeEach(() => {
        vi.resetModules();
        document.body.innerHTML = `
            <section id="user-visits" data-city-id="42">
                <strong id="user-visits-count">1</strong>
                <div id="user-visits-list">
                    <article data-visit-id="17">Старая запись</article>
                </div>
            </section>`;
    });

    afterEach(() => {
        document.body.innerHTML = '';
    });

    it('replaces the matching visit card after an update event', async () => {
        await import('./city_visits.js');

        document.dispatchEvent(new CustomEvent('visited-city-updated', {
            detail: {
                visit: {
                    id: 17,
                    city: 42,
                    city_title: 'Тверь',
                    date_of_visit: '2026-08-05',
                    rating: 4,
                    has_magnet: true,
                    impression_html: '<p>Набережная</p>',
                },
            },
        }));

        expect(document.querySelector('[data-visit-id="17"]').textContent).toContain('Набережная');
        expect(document.querySelector('#user-visits-count').textContent).toBe('1');
    });

    it('replaces the empty state after the first created visit', async () => {
        document.body.innerHTML = `
            <section id="user-visits" data-city-id="42">
                <h2 id="user-visits-heading" class="hidden"><span id="user-visits-count">0</span></h2>
                <p id="user-visits-empty-state">Вы ещё не посетили город</p>
                <div id="user-visits-list"></div>
            </section>`;
        await import('./city_visits.js');

        document.dispatchEvent(new CustomEvent('visited-city-created', {
            detail: {
                visit: {
                    id: 18,
                    city: 42,
                    city_title: 'Тверь',
                    date_of_visit: '2026-08-05',
                    rating: 4,
                },
            },
        }));

        expect(document.querySelector('#user-visits-empty-state')).toBeNull();
        expect(document.querySelector('#user-visits-heading').classList.contains('hidden')).toBe(false);
        expect(document.querySelector('#user-visits-count').textContent).toBe('1');
        expect(document.querySelector('.delete_city')).not.toBeNull();
    });
});
