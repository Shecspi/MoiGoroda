// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const mocks = vi.hoisted(() => ({
    layerGroup: vi.fn(),
    markerClusterGroup: vi.fn(),
}));

vi.mock('leaflet', () => ({
    default: {
        layerGroup: mocks.layerGroup,
        markerClusterGroup: mocks.markerClusterGroup,
    },
}));

vi.mock('leaflet.markercluster', () => ({}));

import { NotVisitedCityLayer } from './not_visited_city_layer.js';

describe('NotVisitedCityLayer', () => {
    let clusterGroup;
    let directGroup;
    let map;

    beforeEach(() => {
        clusterGroup = {
            addLayers: vi.fn(),
            clearLayers: vi.fn(),
            removeLayer: vi.fn(),
        };
        directGroup = {
            addLayer: vi.fn(),
            clearLayers: vi.fn(),
            removeLayer: vi.fn(),
        };
        map = {
            addLayer: vi.fn(),
            removeLayer: vi.fn(),
            hasLayer: vi.fn(() => false),
        };
        mocks.layerGroup.mockReset();
        mocks.layerGroup.mockReturnValue(directGroup);
        mocks.markerClusterGroup.mockReset();
        mocks.markerClusterGroup.mockReturnValue(clusterGroup);
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    function useStatefulLifecycle() {
        const activeLayers = new Set();
        const directMarkers = new Set();
        const markerOwners = new Map();
        const needsClustering = [];
        const mountedBatches = [];
        const mountedBatchResolvers = [];
        const unobservedMountedBatches = [];
        const events = [];

        const waitForMountedBatchStart = () => {
            if (unobservedMountedBatches.length > 0) {
                return Promise.resolve(unobservedMountedBatches.shift());
            }
            return new Promise((resolve) => mountedBatchResolvers.push(resolve));
        };

        map.hasLayer.mockImplementation((candidate) => activeLayers.has(candidate));
        directGroup.addLayer.mockImplementation((marker) => {
            directMarkers.add(marker);
            if (activeLayers.has(directGroup)) {
                markerOwners.set(marker, directGroup);
            }
        });
        directGroup.removeLayer.mockImplementation((marker) => {
            directMarkers.delete(marker);
            if (markerOwners.get(marker) === directGroup) {
                markerOwners.delete(marker);
            }
        });
        directGroup.clearLayers.mockImplementation(() => {
            directMarkers.forEach((marker) => markerOwners.delete(marker));
            directMarkers.clear();
        });
        clusterGroup.removeLayer.mockImplementation((marker) => {
            if (markerOwners.get(marker) === clusterGroup) {
                markerOwners.delete(marker);
            }
        });
        map.removeLayer.mockImplementation((candidate) => {
            events.push(`remove:${candidate === clusterGroup ? 'cluster' : 'direct'}`);
            activeLayers.delete(candidate);
            markerOwners.forEach((owner, marker) => {
                if (owner === candidate) {
                    markerOwners.delete(marker);
                }
            });
        });
        clusterGroup.addLayers.mockImplementation((markers) => {
            if (activeLayers.has(clusterGroup)) {
                events.push(`cluster:${markers.map((marker) => marker.id).join(',')}`);
                mountedBatches.push(markers);
                markers.forEach((marker) => markerOwners.set(marker, clusterGroup));
                const resolve = mountedBatchResolvers.shift();
                if (resolve) {
                    resolve(markers);
                } else {
                    unobservedMountedBatches.push(markers);
                }
            } else {
                events.push(`needs:${markers.map((marker) => marker.id).join(',')}`);
                needsClustering.push(...markers);
            }
        });
        map.addLayer.mockImplementation((candidate) => {
            events.push(`add:${candidate === clusterGroup ? 'cluster' : 'direct'}`);
            activeLayers.add(candidate);
            if (candidate === directGroup) {
                directMarkers.forEach((marker) => markerOwners.set(marker, directGroup));
            }
            if (candidate === clusterGroup && needsClustering.length > 0) {
                clusterGroup.addLayers(needsClustering.splice(0));
            }
        });

        return {
            activeLayers,
            directMarkers,
            events,
            markerOwners,
            mountedBatches,
            needsClustering,
            waitForMountedBatchStart,
        };
    }

    function getChunkProgress() {
        return mocks.markerClusterGroup.mock.calls[0][0].chunkProgress;
    }

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

    it('добавляет новые маркеры одним пакетом и индексирует их по ID', async () => {
        const layer = new NotVisitedCityLayer(map);
        const firstMarker = { id: 'first' };
        const secondMarker = { id: 'second' };

        await layer.add([
            { cityId: 1, marker: firstMarker },
            { cityId: 2, marker: secondMarker },
        ]);

        expect(clusterGroup.addLayers).toHaveBeenCalledOnce();
        expect(clusterGroup.addLayers).toHaveBeenCalledWith([firstMarker, secondMarker]);
        expect(directGroup.addLayer).toHaveBeenNthCalledWith(1, firstMarker);
        expect(directGroup.addLayer).toHaveBeenNthCalledWith(2, secondMarker);
        expect(layer.markers.get(1)).toBe(firstMarker);
        expect(layer.markers.get(2)).toBe(secondMarker);
    });

    it('не добавляет повторно уже проиндексированный город', async () => {
        const layer = new NotVisitedCityLayer(map);
        const marker = { id: 'first' };

        await layer.add([{ cityId: 1, marker }]);
        await layer.add([{ cityId: 1, marker: { id: 'duplicate' } }]);

        expect(clusterGroup.addLayers).toHaveBeenCalledTimes(1);
        expect(layer.markers.get(1)).toBe(marker);
    });

    it('по умолчанию показывает и скрывает кластерный слой', async () => {
        const layer = new NotVisitedCityLayer(map);
        expect(layer.clusteringEnabled).toBe(true);

        await layer.show();
        expect(map.addLayer).toHaveBeenCalledWith(clusterGroup);
        expect(map.addLayer).not.toHaveBeenCalledWith(directGroup);

        map.hasLayer.mockReturnValue(true);
        await layer.hide();
        expect(map.removeLayer).toHaveBeenCalledWith(clusterGroup);
        expect(layer.visible).toBe(false);
        expect(clusterGroup.clearLayers).not.toHaveBeenCalled();
    });

    it('показывает обычный слой до завершения кластерной обработки', async () => {
        const layer = new NotVisitedCityLayer(map);
        layer.add([{ cityId: 1, marker: { id: 'pending' } }]);
        await layer.setClusteringEnabled(false);

        await expect(layer.show()).resolves.toBeUndefined();

        expect(layer.isBatchProcessing).toBe(true);
        expect(map.addLayer).toHaveBeenCalledWith(directGroup);
        expect(map.addLayer).not.toHaveBeenCalledWith(clusterGroup);
    });

    it('переключает видимый слой без пересоздания маркеров', async () => {
        const layer = new NotVisitedCityLayer(map);
        layer.visible = true;
        map.hasLayer.mockImplementation((candidate) => candidate === clusterGroup);

        await expect(layer.setClusteringEnabled(false)).resolves.toBe(false);

        expect(map.removeLayer).toHaveBeenCalledWith(clusterGroup);
        expect(map.addLayer).toHaveBeenCalledWith(directGroup);
        expect(clusterGroup.addLayers).not.toHaveBeenCalled();
    });

    it('меняет будущий режим скрытого слоя без добавления на карту', async () => {
        const layer = new NotVisitedCityLayer(map);

        await expect(layer.setClusteringEnabled(false)).resolves.toBe(false);

        expect(layer.clusteringEnabled).toBe(false);
        expect(map.addLayer).not.toHaveBeenCalled();
        expect(map.removeLayer).not.toHaveBeenCalled();
    });

    it('ждёт завершения кластерного batch перед выключением', async () => {
        const layer = new NotVisitedCityLayer(map);
        layer.add([{ cityId: 1, marker: { id: 'pending' } }]);
        layer.visible = true;
        map.hasLayer.mockImplementation((candidate) => candidate === clusterGroup);
        let settled = false;

        const switching = layer.setClusteringEnabled(false).finally(() => {
            settled = true;
        });
        await Promise.resolve();

        expect(settled).toBe(false);
        expect(map.removeLayer).not.toHaveBeenCalled();
        const { chunkProgress } = mocks.markerClusterGroup.mock.calls[0][0];
        chunkProgress(1, 1, 10);
        await expect(switching).resolves.toBe(false);
        expect(map.addLayer).toHaveBeenCalledWith(directGroup);
    });

    it('не снимает кластер при hide до завершения mounted batch', async () => {
        const layer = new NotVisitedCityLayer(map);
        const { activeLayers } = useStatefulLifecycle();
        activeLayers.add(clusterGroup);
        layer.visible = true;
        layer.add([{ cityId: 1, marker: { id: 'pending' } }]);
        await Promise.resolve();
        getChunkProgress()(1, 2, 10);
        let settled = false;

        const hiding = Promise.resolve(layer.hide()).finally(() => {
            settled = true;
        });
        await Promise.resolve();

        expect(settled).toBe(false);
        expect(activeLayers.has(clusterGroup)).toBe(true);
        expect(map.removeLayer).not.toHaveBeenCalled();
        getChunkProgress()(2, 2, 20);
        await expect(hiding).resolves.toBeUndefined();
        expect(activeLayers.has(clusterGroup)).toBe(false);
    });

    it('не очищает кластер до завершения mounted batch', async () => {
        const layer = new NotVisitedCityLayer(map);
        const { activeLayers } = useStatefulLifecycle();
        activeLayers.add(clusterGroup);
        layer.visible = true;
        layer.add([{ cityId: 1, marker: { id: 'pending' } }]);
        await Promise.resolve();
        getChunkProgress()(1, 2, 10);
        let settled = false;

        const clearing = Promise.resolve(layer.clear()).finally(() => {
            settled = true;
        });
        await Promise.resolve();

        expect(settled).toBe(false);
        expect(clusterGroup.clearLayers).not.toHaveBeenCalled();
        expect(layer.markers.size).toBe(1);
        getChunkProgress()(2, 2, 20);
        await expect(clearing).resolves.toBeUndefined();
        expect(clusterGroup.clearLayers).toHaveBeenCalledOnce();
        expect(directGroup.clearLayers).toHaveBeenCalledOnce();
        expect(layer.markers.size).toBe(0);
    });

    it.each([
        ['кластерного', true],
        ['обычного', false],
    ])('полная очистка снимает %s представление перед сменой режима', async (name, enabled) => {
        const layer = new NotVisitedCityLayer(map);
        const {
            activeLayers,
            markerOwners,
            waitForMountedBatchStart,
        } = useStatefulLifecycle();
        if (!enabled) {
            await layer.setClusteringEnabled(false);
        }
        const activeGroup = enabled ? clusterGroup : directGroup;
        activeLayers.add(activeGroup);
        layer.visible = true;

        await layer.clear();

        expect(activeLayers.has(activeGroup)).toBe(false);
        expect(layer.visible).toBe(false);

        await layer.setClusteringEnabled(!enabled);
        const marker = { id: 'after-clear' };
        await layer.add([{ cityId: 1, marker }]);
        const showing = layer.show();
        const nextGroup = enabled ? directGroup : clusterGroup;
        if (nextGroup === clusterGroup) {
            await waitForMountedBatchStart();
            getChunkProgress()(1, 1, 10);
        }
        await showing;

        expect(activeLayers.size).toBe(1);
        expect(activeLayers.has(nextGroup)).toBe(true);
        expect(markerOwners.get(marker)).toBe(nextGroup);
    });

    it('сохраняет видимый слой и позволяет повторить hide после ошибки', async () => {
        const layer = new NotVisitedCityLayer(map);
        const { activeLayers } = useStatefulLifecycle();
        const originalError = new Error('remove failed');
        activeLayers.add(clusterGroup);
        layer.visible = true;
        map.removeLayer.mockImplementationOnce(() => {
            throw originalError;
        });

        await expect(layer.hide()).rejects.toBe(originalError);

        expect(layer.visible).toBe(true);
        expect(activeLayers.has(clusterGroup)).toBe(true);

        await expect(layer.hide()).resolves.toBeUndefined();
        expect(layer.visible).toBe(false);
        expect(activeLayers.has(clusterGroup)).toBe(false);
    });

    it('сериализует два add во время mounted batch', async () => {
        const layer = new NotVisitedCityLayer(map);
        const { activeLayers, mountedBatches, waitForMountedBatchStart } = useStatefulLifecycle();
        activeLayers.add(clusterGroup);
        const firstMarker = { id: 'first' };
        const secondMarker = { id: 'second' };

        const firstStarted = waitForMountedBatchStart();
        const addingFirst = layer.add([{ cityId: 1, marker: firstMarker }]);
        const addingSecond = layer.add([{ cityId: 2, marker: secondMarker }]);
        const waiting = layer.waitForBatch();
        let settled = false;
        waiting.finally(() => {
            settled = true;
        });

        await firstStarted;
        expect(clusterGroup.addLayers).toHaveBeenCalledOnce();
        expect(mountedBatches).toEqual([[firstMarker]]);
        const secondStarted = waitForMountedBatchStart();
        getChunkProgress()(1, 1, 10);
        expect(clusterGroup.addLayers).toHaveBeenCalledOnce();
        await secondStarted;
        expect(settled).toBe(false);
        expect(clusterGroup.addLayers).toHaveBeenCalledTimes(2);
        expect(mountedBatches).toEqual([[firstMarker], [secondMarker]]);
        getChunkProgress()(1, 1, 20);
        await Promise.all([addingFirst, addingSecond, waiting]);
        expect(settled).toBe(true);
    });

    it('объединяет unmounted add при переходе из direct в cluster', async () => {
        const layer = new NotVisitedCityLayer(map);
        const {
            activeLayers,
            markerOwners,
            mountedBatches,
            needsClustering,
        } = useStatefulLifecycle();
        const firstMarker = { id: 'first' };
        const secondMarker = { id: 'second' };
        await layer.setClusteringEnabled(false);
        layer.add([{ cityId: 1, marker: firstMarker }]);
        layer.add([{ cityId: 2, marker: secondMarker }]);

        await layer.show();
        expect(activeLayers.has(directGroup)).toBe(true);
        expect(needsClustering).toEqual([firstMarker, secondMarker]);
        expect(markerOwners.get(firstMarker)).toBe(directGroup);
        expect(markerOwners.get(secondMarker)).toBe(directGroup);
        let settled = false;
        const switching = layer.setClusteringEnabled(true).finally(() => {
            settled = true;
        });
        await Promise.resolve();

        expect(activeLayers.has(directGroup)).toBe(false);
        expect(activeLayers.has(clusterGroup)).toBe(true);
        expect(mountedBatches).toEqual([[firstMarker, secondMarker]]);
        expect(markerOwners.get(firstMarker)).toBe(clusterGroup);
        expect(markerOwners.get(secondMarker)).toBe(clusterGroup);
        expect(settled).toBe(false);
        getChunkProgress()(2, 2, 20);
        await expect(switching).resolves.toBe(true);
        expect(settled).toBe(true);
    });

    it('откатывает visible и карту после ошибки show', async () => {
        const layer = new NotVisitedCityLayer(map);
        const originalError = new Error('mount failed');
        const activeLayers = new Set();
        map.hasLayer.mockImplementation((candidate) => activeLayers.has(candidate));
        map.addLayer.mockImplementation((candidate) => {
            activeLayers.add(candidate);
            throw originalError;
        });
        map.removeLayer.mockImplementation((candidate) => activeLayers.delete(candidate));

        await expect(layer.show()).rejects.toBe(originalError);

        expect(layer.visible).toBe(false);
        expect(activeLayers.has(clusterGroup)).toBe(false);
        expect(map.removeLayer).toHaveBeenCalledWith(clusterGroup);
    });

    it('разрешает batch waiters после ошибки mounted show', async () => {
        const layer = new NotVisitedCityLayer(map);
        const originalError = new Error('mount failed');
        layer.add([{ cityId: 1, marker: { id: 'pending' } }]);
        const waiting = layer.waitForBatch();
        let waiterSettled = false;
        waiting.finally(() => {
            waiterSettled = true;
        });
        map.addLayer.mockImplementation(() => {
            throw originalError;
        });

        await expect(layer.show()).rejects.toBe(originalError);
        await Promise.resolve();

        expect(waiterSettled).toBe(true);
        await expect(waiting).resolves.toBeUndefined();
    });

    it('сериализует противоположные переключения во время mounted batch', async () => {
        const layer = new NotVisitedCityLayer(map);
        const { activeLayers } = useStatefulLifecycle();
        activeLayers.add(clusterGroup);
        layer.visible = true;
        layer.add([{ cityId: 1, marker: { id: 'pending' } }]);
        const disabling = layer.setClusteringEnabled(false);
        let enablingSettled = false;
        const enabling = layer.setClusteringEnabled(true).finally(() => {
            enablingSettled = true;
        });
        await Promise.resolve();

        expect(enablingSettled).toBe(false);
        getChunkProgress()(1, 1, 20);
        await expect(disabling).resolves.toBe(false);
        await expect(enabling).resolves.toBe(true);
        expect(layer.clusteringEnabled).toBe(true);
        expect(activeLayers.has(clusterGroup)).toBe(true);
        expect(activeLayers.has(directGroup)).toBe(false);
    });

    it('откатывает слой и режим после ошибки переключения', async () => {
        const layer = new NotVisitedCityLayer(map);
        const originalError = new Error('direct layer failed');
        const activeLayers = new Set([clusterGroup]);
        map.hasLayer.mockImplementation((candidate) => activeLayers.has(candidate));
        map.removeLayer.mockImplementation((candidate) => activeLayers.delete(candidate));
        map.addLayer.mockImplementation((candidate) => {
            if (candidate === directGroup) {
                throw originalError;
            }
            activeLayers.add(candidate);
        });
        layer.visible = true;

        await expect(layer.setClusteringEnabled(false)).rejects.toBe(originalError);

        expect(layer.clusteringEnabled).toBe(true);
        expect(activeLayers.has(clusterGroup)).toBe(true);
        expect(map.addLayer).toHaveBeenLastCalledWith(clusterGroup);
    });

    it('не маскирует исходную ошибку ошибкой восстановления слоя', async () => {
        const layer = new NotVisitedCityLayer(map);
        const originalError = new Error('direct layer failed');
        const cleanupError = new Error('restore failed');
        const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
        const activeLayers = new Set([clusterGroup]);
        map.hasLayer.mockImplementation((candidate) => activeLayers.has(candidate));
        map.removeLayer.mockImplementation((candidate) => activeLayers.delete(candidate));
        map.addLayer
            .mockImplementationOnce(() => {
                throw originalError;
            })
            .mockImplementationOnce(() => {
                throw cleanupError;
            });
        layer.visible = true;

        await expect(layer.setClusteringEnabled(false)).rejects.toBe(originalError);

        expect(layer.clusteringEnabled).toBe(true);
        expect(consoleError).toHaveBeenCalledWith(
            'Ошибка при восстановлении слоя кластеризации:',
            cleanupError,
        );
    });

    it('удаляет один город из кластера и индекса', async () => {
        const layer = new NotVisitedCityLayer(map);
        const marker = { id: 'first' };
        await layer.add([{ cityId: 1, marker }]);

        expect(layer.remove(1)).toBe(marker);
        expect(clusterGroup.removeLayer).toHaveBeenCalledWith(marker);
        expect(layer.markers.has(1)).toBe(false);
        expect(layer.remove(999)).toBeNull();
    });

    it('не добавляет город после remove, вызванного до запуска queued add', async () => {
        const layer = new NotVisitedCityLayer(map);
        const marker = { id: 'pending' };

        const adding = layer.add([{ cityId: 1, marker }]);
        expect(layer.remove(1)).toBeNull();

        await adding;

        expect(layer.markers.has(1)).toBe(false);
        expect(clusterGroup.addLayers).not.toHaveBeenCalled();
        expect(directGroup.addLayer).not.toHaveBeenCalled();
    });

    it('повторяет удаление незавершённого маркера до внешнего completion callback', async () => {
        const order = [];
        let layer;
        const onChunkProgress = vi.fn(() => {
            expect(layer.isBatchProcessing).toBe(false);
            expect(layer.pendingRemovals.size).toBe(0);
            order.push('external-completion');
        });
        layer = new NotVisitedCityLayer(map, { onChunkProgress });
        map.hasLayer.mockImplementation((candidate) => candidate === clusterGroup);
        const marker = { id: 'pending' };
        clusterGroup.removeLayer.mockImplementation(() => order.push('remove'));
        const adding = layer.add([{ cityId: 1, marker }]);
        await Promise.resolve();

        expect(layer.remove(1)).toBe(marker);
        expect(layer.markers.has(1)).toBe(false);
        expect(order).toEqual(['remove']);

        const { chunkProgress } = mocks.markerClusterGroup.mock.calls[0][0];
        chunkProgress(1, 1, 20);

        expect(order).toEqual(['remove', 'remove', 'external-completion']);
        expect(clusterGroup.removeLayer).toHaveBeenCalledTimes(2);
        expect(onChunkProgress).toHaveBeenCalledWith(1, 1, 20);
        await adding;
    });

    it('полностью откатывает неудачный batch и позволяет добавить его повторно', async () => {
        const layer = new NotVisitedCityLayer(map);
        const marker = { id: 'pending' };
        clusterGroup.addLayers.mockImplementationOnce(() => {
            throw new Error('add failed');
        });

        await expect(layer.add([{ cityId: 1, marker }])).rejects.toThrow('add failed');
        expect(layer.isBatchProcessing).toBe(false);
        expect(layer.pendingRemovals.size).toBe(0);
        expect(layer.markers.has(1)).toBe(false);
        expect(clusterGroup.removeLayer).toHaveBeenCalledWith(marker);
        expect(directGroup.removeLayer).toHaveBeenCalledWith(marker);

        await layer.add([{ cityId: 1, marker }]);

        expect(clusterGroup.addLayers).toHaveBeenCalledTimes(2);
        expect(clusterGroup.addLayers).toHaveBeenLastCalledWith([marker]);
        expect(layer.markers.get(1)).toBe(marker);
    });

    it('очищает pending removals при полной очистке активного batch', async () => {
        const layer = new NotVisitedCityLayer(map);
        const marker = { id: 'pending' };
        layer.add([{ cityId: 1, marker }]);
        layer.remove(1);

        await layer.clear();

        expect(layer.isBatchProcessing).toBe(false);
        expect(layer.pendingRemovals.size).toBe(0);
        expect(layer.markers.size).toBe(0);
    });

    it('разрешает ожидающих batch при полной очистке', async () => {
        const layer = new NotVisitedCityLayer(map);
        layer.add([{ cityId: 1, marker: { id: 'pending' } }]);
        const waiting = layer.waitForBatch();

        const clearing = layer.clear();

        await expect(waiting).resolves.toBeUndefined();
        await clearing;
        expect(layer.batchWaiters).toHaveLength(0);
    });

    it('полностью очищает кластер при синхронизации данных', async () => {
        const layer = new NotVisitedCityLayer(map);
        layer.add([{ cityId: 1, marker: { id: 'first' } }]);

        await layer.clear();

        expect(clusterGroup.clearLayers).toHaveBeenCalledOnce();
        expect(directGroup.clearLayers).toHaveBeenCalledOnce();
        expect(layer.visible).toBe(false);
        expect(layer.markers.size).toBe(0);
    });

    it('удаляет маркер из обоих слоёв', async () => {
        const layer = new NotVisitedCityLayer(map);
        const marker = { id: 'first' };
        await layer.add([{ cityId: 1, marker }]);

        layer.remove(1);

        expect(clusterGroup.removeLayer).toHaveBeenCalledWith(marker);
        expect(directGroup.removeLayer).toHaveBeenCalledWith(marker);
    });

    it('упорядочивает active add, hide и add из batch waiter', async () => {
        const layer = new NotVisitedCityLayer(map);
        const { activeLayers, events, waitForMountedBatchStart } = useStatefulLifecycle();
        activeLayers.add(clusterGroup);
        layer.visible = true;
        const firstMarker = { id: 'A' };
        const secondMarker = { id: 'B' };

        const firstStarted = waitForMountedBatchStart();
        const addingFirst = layer.add([{ cityId: 1, marker: firstMarker }]);
        expect(addingFirst).toBeInstanceOf(Promise);
        await firstStarted;
        getChunkProgress()(1, 2, 10);
        const hiding = layer.hide();
        const addingAfterBatch = layer.waitForBatch().then(() => (
            layer.add([{ cityId: 2, marker: secondMarker }])
        ));

        getChunkProgress()(2, 2, 20);
        await Promise.all([addingFirst, hiding, addingAfterBatch]);

        expect(events).toEqual(['cluster:A', 'remove:cluster', 'needs:B']);
        expect(activeLayers.has(clusterGroup)).toBe(false);
        expect(layer.markers.get(2)).toBe(secondMarker);
    });

    it('упорядочивает active add, clear и add из batch waiter', async () => {
        const layer = new NotVisitedCityLayer(map);
        const {
            activeLayers,
            directMarkers,
            events,
            waitForMountedBatchStart,
        } = useStatefulLifecycle();
        activeLayers.add(clusterGroup);
        layer.visible = true;
        const firstMarker = { id: 'A' };
        const secondMarker = { id: 'B' };

        const firstStarted = waitForMountedBatchStart();
        const addingFirst = layer.add([{ cityId: 1, marker: firstMarker }]);
        await firstStarted;
        getChunkProgress()(1, 2, 10);
        const clearing = layer.clear();
        const addingAfterBatch = layer.waitForBatch().then(() => (
            layer.add([{ cityId: 2, marker: secondMarker }])
        ));

        getChunkProgress()(2, 2, 20);
        await Promise.all([addingFirst, clearing, addingAfterBatch]);

        expect(events).toEqual(['cluster:A', 'remove:cluster', 'needs:B']);
        expect(activeLayers.has(clusterGroup)).toBe(false);
        expect(layer.markers.has(1)).toBe(false);
        expect(layer.markers.get(2)).toBe(secondMarker);
        expect(directMarkers.has(firstMarker)).toBe(false);
        expect(directMarkers.has(secondMarker)).toBe(true);
    });

    it('упорядочивает concurrent show и hide за mounted batch', async () => {
        const layer = new NotVisitedCityLayer(map);
        const { activeLayers, events, waitForMountedBatchStart } = useStatefulLifecycle();
        const marker = { id: 'A' };
        await layer.add([{ cityId: 1, marker }]);

        const showing = layer.show();
        const hiding = layer.hide();
        await waitForMountedBatchStart();

        expect(activeLayers.has(clusterGroup)).toBe(true);
        expect(map.removeLayer).not.toHaveBeenCalled();
        getChunkProgress()(1, 1, 20);
        await Promise.all([showing, hiding]);
        expect(events).toEqual(['needs:A', 'add:cluster', 'cluster:A', 'remove:cluster']);
        expect(layer.visible).toBe(false);
        expect(activeLayers.has(clusterGroup)).toBe(false);
    });

    it('откатывает failed queued add и продолжает lifecycle queue', async () => {
        const layer = new NotVisitedCityLayer(map);
        const { directMarkers, needsClustering } = useStatefulLifecycle();
        const failedMarker = { id: 'failed' };
        const nextMarker = { id: 'next' };
        const originalError = new Error('add failed');
        clusterGroup.addLayers.mockImplementationOnce(() => {
            throw originalError;
        });

        const failed = layer.add([{ cityId: 1, marker: failedMarker }]);
        const next = layer.add([{ cityId: 2, marker: nextMarker }]);

        await expect(failed).rejects.toBe(originalError);
        await expect(next).resolves.toBeUndefined();
        expect(layer.markers.has(1)).toBe(false);
        expect(directMarkers.has(failedMarker)).toBe(false);
        expect(layer.markers.get(2)).toBe(nextMarker);
        expect(directMarkers.has(nextMarker)).toBe(true);
        expect(needsClustering).toEqual([nextMarker]);
    });
});
