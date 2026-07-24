// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const mocks = vi.hoisted(() => ({
    markerClusterGroup: vi.fn(),
}));

vi.mock('leaflet', () => ({
    default: {
        markerClusterGroup: mocks.markerClusterGroup,
    },
}));

vi.mock('leaflet.markercluster', () => ({}));

import { NotVisitedCityLayer } from './not_visited_city_layer.js';

describe('NotVisitedCityLayer', () => {
    let clusterGroup;
    let map;

    beforeEach(() => {
        clusterGroup = {
            addLayers: vi.fn(),
            clearLayers: vi.fn(),
            removeLayer: vi.fn(),
        };
        map = {
            addLayer: vi.fn(),
            removeLayer: vi.fn(),
            hasLayer: vi.fn(() => false),
        };
        mocks.markerClusterGroup.mockReset();
        mocks.markerClusterGroup.mockReturnValue(clusterGroup);
    });

    it('создаёт кластер с пакетной загрузкой и передаёт прогресс наружу', () => {
        const onChunkProgress = vi.fn();
        new NotVisitedCityLayer(map, { onChunkProgress });

        expect(mocks.markerClusterGroup).toHaveBeenCalledWith(expect.objectContaining({
            chunkedLoading: true,
            chunkProgress: expect.any(Function),
            disableClusteringAtZoom: 8,
            removeOutsideVisibleBounds: true,
            showCoverageOnHover: false,
        }));

        const { chunkProgress } = mocks.markerClusterGroup.mock.calls[0][0];
        chunkProgress(1, 2, 15);
        expect(onChunkProgress).toHaveBeenCalledWith(1, 2, 15);
    });

    it('добавляет новые маркеры одним пакетом и индексирует их по ID', () => {
        const layer = new NotVisitedCityLayer(map);
        const firstMarker = { id: 'first' };
        const secondMarker = { id: 'second' };

        layer.add([
            { cityId: 1, marker: firstMarker },
            { cityId: 2, marker: secondMarker },
        ]);

        expect(clusterGroup.addLayers).toHaveBeenCalledOnce();
        expect(clusterGroup.addLayers).toHaveBeenCalledWith([firstMarker, secondMarker]);
        expect(layer.markers.get(1)).toBe(firstMarker);
        expect(layer.markers.get(2)).toBe(secondMarker);
    });

    it('не добавляет повторно уже проиндексированный город', () => {
        const layer = new NotVisitedCityLayer(map);
        const marker = { id: 'first' };

        layer.add([{ cityId: 1, marker }]);
        layer.add([{ cityId: 1, marker: { id: 'duplicate' } }]);

        expect(clusterGroup.addLayers).toHaveBeenCalledTimes(1);
        expect(layer.markers.get(1)).toBe(marker);
    });

    it('показывает и скрывает весь слой без удаления маркеров', () => {
        const layer = new NotVisitedCityLayer(map);

        layer.show();
        expect(map.addLayer).toHaveBeenCalledWith(clusterGroup);

        map.hasLayer.mockReturnValue(true);
        layer.hide();
        expect(map.removeLayer).toHaveBeenCalledWith(clusterGroup);
        expect(clusterGroup.clearLayers).not.toHaveBeenCalled();
    });

    it('удаляет один город из кластера и индекса', () => {
        const layer = new NotVisitedCityLayer(map);
        const marker = { id: 'first' };
        layer.add([{ cityId: 1, marker }]);

        expect(layer.remove(1)).toBe(marker);
        expect(clusterGroup.removeLayer).toHaveBeenCalledWith(marker);
        expect(layer.markers.has(1)).toBe(false);
        expect(layer.remove(999)).toBeNull();
    });

    it('повторяет удаление незавершённого маркера до внешнего completion callback', () => {
        const order = [];
        let layer;
        const onChunkProgress = vi.fn(() => {
            expect(layer.isBatchProcessing).toBe(false);
            expect(layer.pendingRemovals.size).toBe(0);
            order.push('external-completion');
        });
        layer = new NotVisitedCityLayer(map, { onChunkProgress });
        const marker = { id: 'pending' };
        clusterGroup.removeLayer.mockImplementation(() => order.push('remove'));
        layer.add([{ cityId: 1, marker }]);

        expect(layer.remove(1)).toBe(marker);
        expect(layer.markers.has(1)).toBe(false);
        expect(order).toEqual(['remove']);

        const { chunkProgress } = mocks.markerClusterGroup.mock.calls[0][0];
        chunkProgress(1, 1, 20);

        expect(order).toEqual(['remove', 'remove', 'external-completion']);
        expect(clusterGroup.removeLayer).toHaveBeenCalledTimes(2);
        expect(onChunkProgress).toHaveBeenCalledWith(1, 1, 20);
    });

    it('полностью откатывает неудачный batch и позволяет добавить его повторно', () => {
        const layer = new NotVisitedCityLayer(map);
        const marker = { id: 'pending' };
        clusterGroup.addLayers.mockImplementationOnce(() => {
            throw new Error('add failed');
        });

        expect(() => layer.add([{ cityId: 1, marker }])).toThrow('add failed');
        expect(layer.isBatchProcessing).toBe(false);
        expect(layer.pendingRemovals.size).toBe(0);
        expect(layer.markers.has(1)).toBe(false);
        expect(clusterGroup.clearLayers).toHaveBeenCalledOnce();

        layer.add([{ cityId: 1, marker }]);

        expect(clusterGroup.addLayers).toHaveBeenCalledTimes(2);
        expect(clusterGroup.addLayers).toHaveBeenLastCalledWith([marker]);
        expect(layer.markers.get(1)).toBe(marker);
    });

    it('очищает pending removals при полной очистке активного batch', () => {
        const layer = new NotVisitedCityLayer(map);
        const marker = { id: 'pending' };
        layer.add([{ cityId: 1, marker }]);
        layer.remove(1);

        layer.clear();

        expect(layer.isBatchProcessing).toBe(false);
        expect(layer.pendingRemovals.size).toBe(0);
        expect(layer.markers.size).toBe(0);
    });

    it('полностью очищает кластер при синхронизации данных', () => {
        const layer = new NotVisitedCityLayer(map);
        layer.add([{ cityId: 1, marker: { id: 'first' } }]);

        layer.clear();

        expect(clusterGroup.clearLayers).toHaveBeenCalledOnce();
        expect(layer.markers.size).toBe(0);
    });
});
