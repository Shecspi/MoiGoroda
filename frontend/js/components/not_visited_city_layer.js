// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import L from 'leaflet';
import 'leaflet.markercluster';

export class NotVisitedCityLayer {
    constructor(map, { onChunkProgress = undefined } = {}) {
        this.map = map;
        this.markers = new Map();
        this.isBatchProcessing = false;
        this.pendingRemovals = new Set();
        this.directGroup = L.layerGroup();
        this.clusteringEnabled = true;
        this.visible = false;
        this.batchWaiters = [];
        this.mountedBatchActive = false;
        this.pendingAddOperations = new Map();
        this.lifecycleTail = Promise.resolve();
        this.clusterGroup = L.markerClusterGroup({
            chunkedLoading: true,
            disableClusteringAtZoom: 8,
            chunkProgress: (processed, total, elapsed) => {
                if (processed === total && this.mountedBatchActive) {
                    try {
                        this.pendingRemovals.forEach((marker) => {
                            this.clusterGroup.removeLayer(marker);
                        });
                    } finally {
                        this.pendingRemovals.clear();
                        this.mountedBatchActive = false;
                        this.isBatchProcessing = false;
                        this.resolveBatchWaiters();
                    }
                }
                onChunkProgress?.(processed, total, elapsed);
            },
            removeOutsideVisibleBounds: true,
            showCoverageOnHover: false,
        });
    }

    add(entries) {
        const operation = { entries, cancelledCityIds: new Set() };
        entries.forEach(({ cityId }) => {
            if (!this.pendingAddOperations.has(cityId)) {
                this.pendingAddOperations.set(cityId, new Set());
            }
            this.pendingAddOperations.get(cityId).add(operation);
        });
        return this.enqueueLifecycle(() => {
            entries.forEach(({ cityId }) => {
                const operations = this.pendingAddOperations.get(cityId);
                operations?.delete(operation);
                if (operations?.size === 0) {
                    this.pendingAddOperations.delete(cityId);
                }
            });
            return this.performAdd(entries, operation.cancelledCityIds);
        });
    }

    enqueueLifecycle(operation) {
        const result = this.lifecycleTail.then(operation);
        this.lifecycleTail = result.then(() => undefined, () => undefined);
        return result;
    }

    async performAdd(entries, cancelledCityIds = new Set()) {
        const markersToAdd = [];
        const introducedEntries = [];
        const hadPendingBatch = this.isBatchProcessing;

        try {
            entries.forEach(({ cityId, marker }) => {
                if (cancelledCityIds.has(cityId) || this.markers.has(cityId)) {
                    return;
                }
                this.markers.set(cityId, marker);
                introducedEntries.push({ cityId, marker });
                markersToAdd.push(marker);
            });

            if (markersToAdd.length === 0) {
                return;
            }
            introducedEntries.forEach(({ marker }) => this.directGroup.addLayer(marker));
            this.isBatchProcessing = true;
            if (this.map.hasLayer(this.clusterGroup)) {
                this.startMountedBatch(markersToAdd);
                await this.waitForActiveBatch();
            } else {
                this.clusterGroup.addLayers(markersToAdd);
            }
        } catch (error) {
            this.rollbackAddedEntries(introducedEntries);
            this.mountedBatchActive = false;
            this.isBatchProcessing = hadPendingBatch;
            if (!hadPendingBatch) {
                this.resolveBatchWaiters();
            }
            throw error;
        }
    }

    rollbackAddedEntries(entries) {
        entries.forEach(({ cityId, marker }) => {
            if (this.markers.get(cityId) === marker) {
                this.markers.delete(cityId);
            }
            try {
                this.clusterGroup.removeLayer(marker);
            } catch (cleanupError) {
                console.error('Ошибка при откате маркера из кластера:', cleanupError);
            }
            try {
                this.directGroup.removeLayer(marker);
            } catch (cleanupError) {
                console.error('Ошибка при откате маркера из обычного слоя:', cleanupError);
            }
        });
    }

    startMountedBatch(markers) {
        this.mountedBatchActive = true;
        this.clusterGroup.addLayers(markers);
    }

    resolveBatchWaiters() {
        const waiters = this.batchWaiters.splice(0);
        waiters.forEach((resolve) => resolve());
    }

    waitForBatch() {
        const lifecycle = this.lifecycleTail;
        return lifecycle.then(() => this.waitForActiveBatch());
    }

    waitForActiveBatch() {
        if (!this.isBatchProcessing) {
            return Promise.resolve();
        }
        return new Promise((resolve) => this.batchWaiters.push(resolve));
    }

    getActiveGroup() {
        return this.clusteringEnabled ? this.clusterGroup : this.directGroup;
    }

    show() {
        return this.enqueueLifecycle(() => this.performShow());
    }

    async performShow() {
        const previousVisible = this.visible;
        this.visible = true;
        const activeGroup = this.getActiveGroup();
        const wasMounted = this.map.hasLayer(activeGroup);
        try {
            if (!wasMounted) {
                if (activeGroup === this.clusterGroup && this.isBatchProcessing) {
                    this.mountedBatchActive = true;
                }
                this.map.addLayer(activeGroup);
            }
            if (this.clusteringEnabled) {
                await this.waitForActiveBatch();
            }
        } catch (error) {
            this.visible = previousVisible;
            if (activeGroup === this.clusterGroup) {
                this.mountedBatchActive = false;
                this.resolveBatchWaiters();
            }
            if (!wasMounted) {
                try {
                    if (this.map.hasLayer(activeGroup)) {
                        this.map.removeLayer(activeGroup);
                    }
                } catch (cleanupError) {
                    console.error('Ошибка при откате показа слоя городов:', cleanupError);
                }
            }
            throw error;
        }
    }

    hide() {
        return this.enqueueLifecycle(() => this.performHide());
    }

    performHide() {
        const activeGroup = this.getActiveGroup();
        if (this.map.hasLayer(activeGroup)) {
            try {
                this.map.removeLayer(activeGroup);
            } catch (error) {
                try {
                    if (!this.map.hasLayer(activeGroup)) {
                        this.map.addLayer(activeGroup);
                    }
                } catch (cleanupError) {
                    console.error('Ошибка при восстановлении слоя городов:', cleanupError);
                }
                this.visible = this.map.hasLayer(activeGroup);
                throw error;
            }
        }
        this.visible = false;
    }

    setClusteringEnabled(enabled) {
        return this.enqueueLifecycle(() => this.performSetClusteringEnabled(enabled));
    }

    async performSetClusteringEnabled(enabled) {
        if (enabled === this.clusteringEnabled) {
            return this.clusteringEnabled;
        }
        const previousEnabled = this.clusteringEnabled;
        const previousGroup = this.getActiveGroup();
        if (!this.visible) {
            this.clusteringEnabled = enabled;
            return this.clusteringEnabled;
        }
        const nextGroup = enabled ? this.clusterGroup : this.directGroup;
        try {
            if (this.map.hasLayer(previousGroup)) {
                this.map.removeLayer(previousGroup);
            }
            this.clusteringEnabled = enabled;
            if (nextGroup === this.clusterGroup && this.isBatchProcessing) {
                this.mountedBatchActive = true;
            }
            this.map.addLayer(nextGroup);
            if (enabled) {
                await this.waitForActiveBatch();
            }
            return this.clusteringEnabled;
        } catch (error) {
            try {
                if (this.map.hasLayer(nextGroup)) {
                    this.map.removeLayer(nextGroup);
                }
            } catch (cleanupError) {
                console.error('Ошибка при откате слоя кластеризации:', cleanupError);
            }
            this.clusteringEnabled = previousEnabled;
            if (nextGroup === this.clusterGroup) {
                this.mountedBatchActive = false;
                this.resolveBatchWaiters();
            }
            try {
                if (!this.map.hasLayer(previousGroup)) {
                    this.map.addLayer(previousGroup);
                }
            } catch (cleanupError) {
                console.error('Ошибка при восстановлении слоя кластеризации:', cleanupError);
            }
            throw error;
        }
    }

    remove(cityId) {
        this.pendingAddOperations.get(cityId)?.forEach((operation) => {
            operation.cancelledCityIds.add(cityId);
        });
        const marker = this.markers.get(cityId);
        if (!marker) {
            return null;
        }

        this.markers.delete(cityId);
        if (this.isBatchProcessing && this.map.hasLayer(this.clusterGroup)) {
            this.pendingRemovals.add(marker);
        }
        this.clusterGroup.removeLayer(marker);
        this.directGroup.removeLayer(marker);
        return marker;
    }

    clear() {
        return this.enqueueLifecycle(() => this.performClear());
    }

    performClear() {
        let operationError;
        [this.clusterGroup, this.directGroup].forEach((group) => {
            try {
                if (this.map.hasLayer(group)) {
                    this.map.removeLayer(group);
                }
            } catch (error) {
                operationError ??= error;
            }
        });
        try {
            this.clearLayersNow();
        } catch (error) {
            operationError ??= error;
        }
        this.visible = [this.clusterGroup, this.directGroup]
            .some((group) => this.map.hasLayer(group));
        if (operationError) {
            throw operationError;
        }
    }

    clearLayersNow() {
        let clearError;
        try {
            this.clusterGroup.clearLayers();
        } catch (error) {
            clearError = error;
        }
        try {
            this.directGroup.clearLayers();
        } catch (error) {
            clearError ??= error;
        } finally {
            this.markers.clear();
            this.pendingRemovals.clear();
            this.isBatchProcessing = false;
            this.mountedBatchActive = false;
            this.resolveBatchWaiters();
        }
        if (clearError) {
            throw clearError;
        }
    }
}
