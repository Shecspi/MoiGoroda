// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import { beforeEach, describe, expect, it, vi } from 'vitest';

describe('timeline_modal', () => {
    beforeEach(() => {
        vi.resetModules();
        document.body.innerHTML = '';
    });

    async function loadTimelineModal() {
        await import('./timeline_modal.js');
        document.dispatchEvent(new Event('DOMContentLoaded'));
    }

    function createTimelineModal() {
        document.body.innerHTML = `
            <button data-timeline-modal-trigger="region-timeline-modal">Открыть</button>
            <dialog id="region-timeline-modal">
                <form data-timeline-year-filter-form>
                    <input type="checkbox" value="2024" data-timeline-year-filter="2024">
                    <input type="checkbox" value="2023" data-timeline-year-filter="2023">
                    <input type="reset" value="×">
                </form>
                <div data-timeline-scroll-container>
                    <ul>
                        <li data-timeline-item>Непосещённый</li>
                        <li data-timeline-item data-timeline-year="2024" data-timeline-first-visited>2024</li>
                        <li data-timeline-item data-timeline-year="2023">2023</li>
                        <li data-timeline-item>Без даты</li>
                    </ul>
                </div>
            </dialog>
        `;

        const modal = document.getElementById('region-timeline-modal');
        modal.showModal = vi.fn();

        return modal;
    }

    function waitForAnimationFrame() {
        return new Promise((resolve) => {
            requestAnimationFrame(resolve);
        });
    }

    it('фильтрует хронологию по выбранному году', async () => {
        createTimelineModal();
        await loadTimelineModal();

        document.querySelector('[data-timeline-year-filter="2024"]').click();

        const items = [...document.querySelectorAll('[data-timeline-item]')];
        expect(items.map((item) => item.hidden)).toEqual([true, false, true, true]);
    });

    it('показывает элементы любого выбранного года', async () => {
        createTimelineModal();
        await loadTimelineModal();

        document.querySelector('[data-timeline-year-filter="2024"]').click();
        document.querySelector('[data-timeline-year-filter="2023"]').click();

        const items = [...document.querySelectorAll('[data-timeline-item]')];
        expect(items.map((item) => item.hidden)).toEqual([true, false, false, true]);
    });

    it('сбрасывает фильтр годов и показывает всю хронологию', async () => {
        createTimelineModal();
        await loadTimelineModal();

        document.querySelector('[data-timeline-year-filter="2024"]').click();
        document.querySelector('[data-timeline-year-filter-form]').reset();
        document.querySelector('[data-timeline-year-filter-form]').dispatchEvent(new Event('reset'));
        await waitForAnimationFrame();

        const items = [...document.querySelectorAll('[data-timeline-item]')];
        expect(items.map((item) => item.hidden)).toEqual([false, false, false, false]);
    });

    it('после фильтра скроллит к первому видимому посещению', async () => {
        createTimelineModal();
        await loadTimelineModal();

        const scrollContainer = document.querySelector('[data-timeline-scroll-container]');
        const year2023Item = document.querySelector('[data-timeline-year="2023"]');
        scrollContainer.getBoundingClientRect = () => ({ top: 10 });
        year2023Item.getBoundingClientRect = () => ({ top: 70 });

        document.querySelector('[data-timeline-year-filter="2023"]').click();
        await waitForAnimationFrame();

        expect(scrollContainer.scrollTop).toBeGreaterThan(0);
    });

    it('открывает modal, созданный после refresh lifecycle event', async () => {
        await loadTimelineModal();
        const root = document.createElement('section');
        document.body.append(root);
        root.innerHTML = `
            <button data-timeline-modal-trigger="region-timeline-modal">Открыть</button>
            <dialog id="region-timeline-modal"><div data-timeline-scroll-container></div></dialog>
        `;
        const modal = root.querySelector('#region-timeline-modal');
        modal.showModal = vi.fn();

        document.dispatchEvent(new CustomEvent('visited-city-list-refreshed', {
            detail: {root},
        }));
        root.querySelector('[data-timeline-modal-trigger]').click();

        expect(modal.showModal).toHaveBeenCalledOnce();
    });
});
