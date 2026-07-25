// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import { afterAll, afterEach, beforeAll, describe, expect, it, vi } from 'vitest';

let L;
let NotVisitedCityLayer;

beforeAll(async () => {
    ({ default: L } = await import('leaflet'));
    globalThis.L = L;
    await import('leaflet.markercluster');
    ({ NotVisitedCityLayer } = await import('./not_visited_city_layer.js'));
});

afterAll(() => {
    delete globalThis.L;
});

describe('NotVisitedCityLayer с настоящим Leaflet.markercluster', () => {
    let map;
    let mapElement;

    afterEach(() => {
        map?.remove();
        mapElement?.remove();
    });

    it('повторно удаляет ещё не обработанный маркер после chunked batch', async () => {
        mapElement = document.createElement('div');
        Object.defineProperties(mapElement, {
            clientWidth: { configurable: true, value: 800 },
            clientHeight: { configurable: true, value: 600 },
            offsetWidth: { configurable: true, value: 800 },
            offsetHeight: { configurable: true, value: 600 },
        });
        document.body.appendChild(mapElement);
        map = L.map(mapElement, { maxZoom: 18 }).setView([0, 0], 3);

        let layer;
        let targetMarker;
        let removedDuringBatch = false;
        layer = new NotVisitedCityLayer(map, {
            onChunkProgress: (processed, total) => {
                if (processed >= total || removedDuringBatch) {
                    return;
                }
                expect(targetMarker.__parent).toBeUndefined();
                expect(layer.remove(total)).toBe(targetMarker);
                expect(layer.pendingRemovals.has(targetMarker)).toBe(true);
                removedDuringBatch = true;
            },
        });
        layer.clusterGroup.options.chunkInterval = 0;
        layer.clusterGroup.options.chunkDelay = 0;
        const removeLayer = vi.spyOn(layer.clusterGroup, 'removeLayer');

        const entries = Array.from({ length: 1000 }, (_, index) => ({
            cityId: index + 1,
            marker: L.marker([
                (index % 80) / 100,
                (index % 160) / 100,
            ]),
        }));
        targetMarker = entries.at(-1).marker;

        await layer.add(entries);
        expect(layer.clusterGroup._needsClustering).toContain(targetMarker);

        await layer.show();

        expect(removedDuringBatch).toBe(true);
        expect(layer.markers.has(entries.length)).toBe(false);
        expect(layer.clusterGroup.hasLayer(targetMarker)).toBe(false);
        expect(targetMarker.__parent).toBeUndefined();
        expect(layer.pendingRemovals.size).toBe(0);
        expect(
            removeLayer.mock.calls.filter(([marker]) => marker === targetMarker),
        ).toHaveLength(2);
    });
});
