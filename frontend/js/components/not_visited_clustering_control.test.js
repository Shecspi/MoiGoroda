// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const mocks = vi.hoisted(() => ({
    handlers: new Map(),
}));

vi.mock('leaflet', () => {
    class Control {
        constructor(options) {
            this.options = options;
        }

        addTo(map) {
            this._container = this.onAdd(map);
            map.addControl(this);
            return this;
        }

        getContainer() {
            return this._container;
        }
    }

    Control.extend = (definition) => {
        class ExtendedControl extends Control {}
        Object.assign(ExtendedControl.prototype, definition);
        return ExtendedControl;
    };

    return {
        default: {
            Control,
            DomUtil: {
                create(tagName, className, parent) {
                    const element = document.createElement(tagName);
                    element.className = className;
                    parent?.appendChild(element);
                    return element;
                },
            },
            DomEvent: {
                disableClickPropagation: vi.fn(),
                disableScrollPropagation: vi.fn(),
                on(element, eventName, handler) {
                    mocks.handlers.set(`${eventName}:${element.tagName}`, handler);
                    element.addEventListener(eventName, handler);
                },
                preventDefault(event) {
                    event.preventDefault();
                },
                stopPropagation(event) {
                    event.stopPropagation();
                },
            },
        },
    };
});

import {
    addNotVisitedClusteringControl,
    syncNotVisitedClusteringControl,
} from './not_visited_clustering_control.js';

describe('addNotVisitedClusteringControl', () => {
    let map;

    beforeEach(() => {
        mocks.handlers.clear();
        map = { addControl: vi.fn() };
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    function getButton(control) {
        return control.getContainer().querySelector('[role="button"]');
    }

    it('по умолчанию отражает включённую кластеризацию', () => {
        const control = addNotVisitedClusteringControl(map, {
            getEnabled: () => true,
            getVisible: () => true,
            onToggle: vi.fn(),
        });
        const button = getButton(control);

        expect(control.options.position).toBe('topright');
        expect(button.getAttribute('aria-pressed')).toBe('true');
        expect(button.getAttribute('aria-disabled')).toBe('false');
        expect(button.getAttribute('aria-label')).toBe('Показать города отдельно');
        expect(button.getAttribute('tabindex')).toBe('0');
        expect(button.querySelector('svg')?.getAttribute('viewBox')).toBe('0 0 384 512');
        expect(button.querySelector('path')?.getAttribute('d')).toBe(
            'M215.7 499.2C267 435 384 279.4 384 192C384 86 298 0 192 0S0 86 0 192c0 87.4 117 243 168.3 307.2c12.3 15.3 35.1 15.3 47.4 0zM192 128a64 64 0 1 1 0 128 64 64 0 1 1 0-128z',
        );
    });

    it('переключает режим мышью и синхронизирует aria', async () => {
        let enabled = true;
        const onToggle = vi.fn(async () => (enabled = !enabled));
        const control = addNotVisitedClusteringControl(map, {
            getEnabled: () => enabled,
            getVisible: () => true,
            onToggle,
        });
        const button = getButton(control);

        button.click();

        await vi.waitFor(() => expect(onToggle).toHaveBeenCalledOnce());
        await vi.waitFor(() => expect(button.getAttribute('aria-pressed')).toBe('false'));
        expect(button.getAttribute('aria-label')).toBe('Собрать города в кластеры');
        expect(button.querySelector('svg')?.getAttribute('viewBox')).toBe('0 0 640 640');
        expect(button.querySelector('path')?.getAttribute('d')).toBe(
            'M482.4 221.9C517.7 213.6 544 181.9 544 144C544 99.8 508.2 64 464 64C420.6 64 385.3 98.5 384 141.5L200.2 215.1C185.7 200.8 165.9 192 144 192C99.8 192 64 227.8 64 272C64 316.2 99.8 352 144 352C156.2 352 167.8 349.3 178.1 344.4L323.7 471.8C321.3 479.4 320 487.6 320 496C320 540.2 355.8 576 400 576C444.2 576 480 540.2 480 496C480 468.3 466 443.9 444.6 429.6L482.4 221.9zM220.3 296.2C222.5 289.3 223.8 282 224 274.5L407.8 201C411.4 204.5 415.2 207.7 419.4 210.5L381.6 418.1C376.1 419.4 370.8 421.2 365.8 423.6L220.3 296.2z',
        );
    });

    it.each(['Enter', ' '])('переключает режим клавишей %s', async (key) => {
        let enabled = true;
        const onToggle = vi.fn(async () => (enabled = false));
        const control = addNotVisitedClusteringControl(map, {
            getEnabled: () => enabled,
            getVisible: () => true,
            onToggle,
        });
        const button = getButton(control);

        button.dispatchEvent(new KeyboardEvent('keydown', { key, bubbles: true }));

        await vi.waitFor(() => expect(onToggle).toHaveBeenCalledOnce());
        await vi.waitFor(() => expect(button.getAttribute('aria-pressed')).toBe('false'));
    });

    it('не запускает повторное переключение до завершения первого', async () => {
        let finishToggle;
        const onToggle = vi.fn(() => new Promise((resolve) => {
            finishToggle = resolve;
        }));
        const control = addNotVisitedClusteringControl(map, {
            getEnabled: () => true,
            getVisible: () => true,
            onToggle,
        });
        const button = getButton(control);

        button.click();
        button.click();

        expect(onToggle).toHaveBeenCalledOnce();
        expect(button.getAttribute('aria-disabled')).toBe('true');
        finishToggle(true);
        await vi.waitFor(() => expect(button.getAttribute('aria-disabled')).toBe('false'));
    });

    it('после ошибки восстанавливает доступность и текущее состояние', async () => {
        const error = new Error('toggle failed');
        const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
        const control = addNotVisitedClusteringControl(map, {
            getEnabled: () => true,
            getVisible: () => true,
            onToggle: vi.fn().mockRejectedValue(error),
        });
        const button = getButton(control);

        button.click();

        await vi.waitFor(() => expect(button.getAttribute('aria-disabled')).toBe('false'));
        expect(button.getAttribute('aria-pressed')).toBe('true');
        expect(consoleError).toHaveBeenCalledWith(
            'Ошибка при переключении кластеризации:',
            error,
        );
    });

    it('синхронизирует видимость', () => {
        let visible = false;
        const control = addNotVisitedClusteringControl(map, {
            getEnabled: () => true,
            getVisible: () => visible,
            onToggle: vi.fn(),
        });
        const container = control.getContainer();

        expect(container.hidden).toBe(true);

        visible = true;
        syncNotVisitedClusteringControl(control);
        expect(container.hidden).toBe(false);

        visible = false;
        syncNotVisitedClusteringControl(control);
        expect(container.hidden).toBe(true);
    });
});
