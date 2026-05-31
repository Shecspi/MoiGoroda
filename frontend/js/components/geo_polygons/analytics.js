const yandexMetrikaId = window.YANDEX_METRIKA_ID || '';

const pageOpenTracked = { value: false };

function getBasePayload(extraPayload) {
    return {
        is_authenticated: Boolean(window.OSM_VIEWER_IS_AUTHENTICATED),
        has_active_subscription: Boolean(window.OSM_VIEWER_HAS_ACTIVE_SUBSCRIPTION),
        has_advanced_premium: Boolean(window.OSM_VIEWER_HAS_ADVANCED_PREMIUM),
        ...extraPayload,
    };
}

export function trackGeoPolygonsGoal(goalName, extraPayload) {
    if (!goalName || !yandexMetrikaId || typeof window.ym !== 'function') return;
    const payload = getBasePayload(extraPayload);
    try {
        window.ym(yandexMetrikaId, 'reachGoal', goalName, payload);
    } catch (error) {
        console.warn('Не удалось отправить событие Я.Метрики:', goalName, error);
    }
}

export function initGeoPolygonsAnalytics() {
    if (!pageOpenTracked.value) {
        trackGeoPolygonsGoal('geo_polygons_page_open');
        pageOpenTracked.value = true;
    }

    const helpModal = document.getElementById('geo-polygons-help-modal');
    if (helpModal) {
        helpModal.addEventListener('open.hs.overlay', () => {
            trackGeoPolygonsGoal('geo_polygons_help_open');
        });
    }

    const importantModal = document.getElementById('geo-polygons-important-modal');
    if (importantModal) {
        importantModal.addEventListener('open.hs.overlay', () => {
            trackGeoPolygonsGoal('geo_polygons_important_open');
        });
    }
}
