/**
 * Кнопка переключения режима отображения городов на карте региона: маркеры / полигоны.
 *
 * ----------------------------------------------
 *
 * Copyright © Egor Vavilov (Shecspi)
 * Licensed under the Apache License, Version 2.0
 *
 * ----------------------------------------------
 */

import L from 'leaflet';

/** Обе иконки: viewBox 24×24 и class control-icon (1rem в leaflet-controls.css). */
const ICON_MARKERS =
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="control-icon" fill="none" stroke="currentColor" aria-hidden="true">' +
    '<path stroke-linecap="round" stroke-linejoin="round" d="M20 10c0 4.99-8 12-8 12s-8-7.01-8-12a8 8 0 1 1 16 0Z"/>' +
    '<circle cx="12" cy="10" r="3"/>' +
    '</svg>';

const ICON_POLYGONS =
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="control-icon" fill="none" stroke="currentColor" aria-hidden="true">' +
    '<path stroke-linecap="round" stroke-linejoin="round" d="M12 3l8 4.5v9L12 21l-8-4.5v-9L12 3z"/>' +
    '<path stroke-linecap="round" stroke-linejoin="round" d="M12 12l8-4.5M12 12v9M12 12L4 7.5"/>' +
    '</svg>';

/**
 * @param {L.Map} map
 * @param {{ getMode: () => string, onToggle: () => void | Promise<void>, getDisabled?: () => boolean }} handlers
 */
export function addRegionCityDisplayControl(map, {getMode, onToggle, getDisabled}) {
    const Control = L.Control.extend({
        onAdd() {
            const bar = L.DomUtil.create('div', 'leaflet-bar leaflet-control-region-city-display');
            const btn = L.DomUtil.create('a', 'custom-control-for-map', bar);
            btn.href = '#';
            btn.setAttribute('role', 'button');
            btn.setAttribute('tabindex', '0');

            const syncUi = () => {
                const disabled = getDisabled ? getDisabled() : false;
                const polygonsMode = getMode() === 'polygons';
                btn.classList.toggle('custom-control-for-map--active', polygonsMode);
                btn.classList.toggle('custom-control-for-map--disabled', disabled);
                btn.disabled = disabled;
                btn.innerHTML = polygonsMode ? ICON_MARKERS : ICON_POLYGONS;
                btn.title = disabled
                    ? 'Границы городов недоступны'
                    : polygonsMode
                        ? 'Показать маркеры городов'
                        : 'Показать границы городов';
                btn.setAttribute('aria-label', btn.title);
                btn.setAttribute('aria-pressed', polygonsMode ? 'true' : 'false');
            };

            const activate = (e) => {
                if (btn.disabled) return;
                L.DomEvent.preventDefault(e);
                L.DomEvent.stopPropagation(e);
                void Promise.resolve(onToggle()).then(syncUi);
            };

            L.DomEvent.disableClickPropagation(bar);
            L.DomEvent.disableScrollPropagation(bar);
            L.DomEvent.on(btn, 'click', activate);
            L.DomEvent.on(btn, 'keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    activate(e);
                }
            });

            btn._mgSyncRegionCityDisplay = syncUi;
            syncUi();

            return bar;
        },
    });

    const control = new Control({position: 'topleft'});
    control.addTo(map);
    return control;
}

/**
 * Обновляет иконку и подсказку кнопки после смены режима снаружи.
 * @param {L.Control} control
 */
export function syncRegionCityDisplayControl(control) {
    const wrap = control.getContainer();
    const btn = wrap?.querySelector('.custom-control-for-map');
    if (btn && typeof btn._mgSyncRegionCityDisplay === 'function') {
        btn._mgSyncRegionCityDisplay();
    }
}
