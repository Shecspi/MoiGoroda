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
        this.clusterGroup = L.markerClusterGroup({
            chunkedLoading: true,
            disableClusteringAtZoom: 8,
            chunkProgress: (processed, total, elapsed) => {
                if (processed === total && this.isBatchProcessing) {
                    const pendingRemovals = [...this.pendingRemovals];
                    this.pendingRemovals.clear();
                    this.isBatchProcessing = false;
                    pendingRemovals.forEach((marker) => {
                        this.clusterGroup.removeLayer(marker);
                    });
                }
                onChunkProgress?.(processed, total, elapsed);
            },
            removeOutsideVisibleBounds: true,
            showCoverageOnHover: false,
        });
    }

    add(entries) {
        const markersToAdd = [];

        entries.forEach(({ cityId, marker }) => {
            if (this.markers.has(cityId)) {
                return;
            }
            this.markers.set(cityId, marker);
            markersToAdd.push(marker);
        });

        if (markersToAdd.length > 0) {
            this.isBatchProcessing = true;
            try {
                this.clusterGroup.addLayers(markersToAdd);
            } catch (error) {
                try {
                    this.clear();
                } catch (cleanupError) {
                    console.error(
                        'Ошибка при очистке кластера после сбоя добавления:',
                        cleanupError,
                    );
                }
                throw error;
            }
        }
    }

    show() {
        if (!this.map.hasLayer(this.clusterGroup)) {
            this.map.addLayer(this.clusterGroup);
        }
    }

    hide() {
        if (this.map.hasLayer(this.clusterGroup)) {
            this.map.removeLayer(this.clusterGroup);
        }
    }

    remove(cityId) {
        const marker = this.markers.get(cityId);
        if (!marker) {
            return null;
        }

        this.markers.delete(cityId);
        if (this.isBatchProcessing) {
            this.pendingRemovals.add(marker);
        }
        this.clusterGroup.removeLayer(marker);
        return marker;
    }

    clear() {
        try {
            this.clusterGroup.clearLayers();
        } finally {
            this.markers.clear();
            this.pendingRemovals.clear();
            this.isBatchProcessing = false;
        }
    }
}
