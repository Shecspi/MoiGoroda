// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import L from 'leaflet';

const CLUSTER_ACTION_ICON =
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640" class="control-icon control-icon--solid" aria-hidden="true">' +
    '<path d="M482.4 221.9C517.7 213.6 544 181.9 544 144C544 99.8 508.2 64 464 64C420.6 64 385.3 98.5 384 141.5L200.2 215.1C185.7 200.8 165.9 192 144 192C99.8 192 64 227.8 64 272C64 316.2 99.8 352 144 352C156.2 352 167.8 349.3 178.1 344.4L323.7 471.8C321.3 479.4 320 487.6 320 496C320 540.2 355.8 576 400 576C444.2 576 480 540.2 480 496C480 468.3 466 443.9 444.6 429.6L482.4 221.9zM220.3 296.2C222.5 289.3 223.8 282 224 274.5L407.8 201C411.4 204.5 415.2 207.7 419.4 210.5L381.6 418.1C376.1 419.4 370.8 421.2 365.8 423.6L220.3 296.2z"/>' +
    '</svg>';

const MARKER_ACTION_ICON =
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512" class="control-icon control-icon--solid" aria-hidden="true">' +
    '<path d="M215.7 499.2C267 435 384 279.4 384 192C384 86 298 0 192 0S0 86 0 192c0 87.4 117 243 168.3 307.2c12.3 15.3 35.1 15.3 47.4 0zM192 128a64 64 0 1 1 0 128 64 64 0 1 1 0-128z"/>' +
    '</svg>';

export function addNotVisitedClusteringControl(map, { getEnabled, getVisible, onToggle }) {
    const Control = L.Control.extend({
        onAdd() {
            const bar = L.DomUtil.create(
                'div',
                'leaflet-bar leaflet-control-not-visited-clustering',
            );
            const button = L.DomUtil.create('a', 'custom-control-for-map', bar);
            button.href = '#';
            button.setAttribute('role', 'button');
            button.setAttribute('tabindex', '0');
            let pending = false;

            const syncUi = () => {
                const enabled = getEnabled();
                bar.hidden = !getVisible();
                button.classList.toggle('custom-control-for-map--disabled', pending);
                button.setAttribute('aria-disabled', String(pending));
                button.setAttribute('aria-pressed', String(enabled));
                button.innerHTML = enabled ? MARKER_ACTION_ICON : CLUSTER_ACTION_ICON;
                button.title = enabled
                    ? 'Показать города отдельно'
                    : 'Собрать города в кластеры';
                button.setAttribute('aria-label', button.title);
            };
            bar._mgSyncNotVisitedClustering = syncUi;

            const activate = async (event) => {
                L.DomEvent.preventDefault(event);
                L.DomEvent.stopPropagation(event);
                if (pending) {
                    return;
                }

                pending = true;
                syncUi();
                try {
                    await onToggle();
                } catch (error) {
                    console.error('Ошибка при переключении кластеризации:', error);
                } finally {
                    pending = false;
                    syncUi();
                }
            };

            L.DomEvent.disableClickPropagation(bar);
            L.DomEvent.disableScrollPropagation(bar);
            L.DomEvent.on(button, 'click', activate);
            L.DomEvent.on(button, 'keydown', (event) => {
                if (event.key === 'Enter' || event.key === ' ') {
                    void activate(event);
                }
            });
            syncUi();

            return bar;
        },
    });

    const control = new Control({ position: 'topright' });
    control.addTo(map);
    return control;
}

export function syncNotVisitedClusteringControl(control) {
    const container = control.getContainer();
    if (typeof container?._mgSyncNotVisitedClustering === 'function') {
        container._mgSyncNotVisitedClustering();
    }
}
