/**
 * Страница «Поделиться закрытием региона»: изображение по GeoJSON полигону
 * и точкам городов (без подложки карты). Рисуем на Canvas.
 *
 * ----------------------------------------------
 *
 * Copyright © Egor Vavilov (Shecspi)
 * Licensed under the Apache License, Version 2.0
 *
 * ----------------------------------------------
 */

const iso3166El = document.getElementById('iso3166_code');
if (!iso3166El) throw new Error('iso3166_code element not found');
const iso3166_code = iso3166El.dataset.iso3166_code;
const [country_code, region_code] = iso3166_code.split('-');

const all_cities = window.ALL_CITIES || [];
const regionName = window.REGION_NAME || '';
const numVisited = window.SHARE_NUMBER_OF_VISITED ?? 0;
const numCities = window.SHARE_NUMBER_OF_CITIES ?? 0;

const PADDING = 48;
const CAPTION_HEIGHT = 56;
const CAPTION_PADDING = 12;

/** Соотношения сторон: базовая длинная сторона 800px. */
const ASPECT_PRESETS = {
    '16:9': { width: 800, height: 450 },
    '4:3': { width: 800, height: 600 },
    '1:1': { width: 800, height: 800 },
    '3:4': { width: 600, height: 800 },
    '9:16': { width: 450, height: 800 },
};

const DEFAULT_ASPECT = '4:3';
const BASE_LONG_SIDE = 800;

/** Разрешение: длинная сторона в пикселях (720p, 1080p, 2K=1440p). Влияет только на скачиваемый/шаримый файл. */
const RESOLUTION_LONG_SIDE = { '720': 720, '1080': 1080, '1440': 1440 };
const DEFAULT_RESOLUTION = '1080';

/** Текущее соотношение сторон (пресет) — для расчёта экспорта и отображения. */
function getAspectPreset() {
    const aspectEl = document.querySelector('input[name="share-aspect-ratio"]:checked');
    const aspectKey = (aspectEl && aspectEl.value && ASPECT_PRESETS[aspectEl.value]) ? aspectEl.value : DEFAULT_ASPECT;
    return ASPECT_PRESETS[aspectKey];
}

/** Размеры для отображения на странице: по ширине контейнера с сохранением соотношения сторон. */
function getDisplayDimensions() {
    const preset = getAspectPreset();
    const container = document.getElementById('share-image-container');
    if (container && container.clientWidth > 0) {
        return {
            width: container.clientWidth,
            height: Math.round(container.clientWidth * (preset.height / preset.width)),
        };
    }
    return preset;
}

/** Размеры для экспорта (скачать / поделиться) — с учётом выбранного разрешения. */
function getExportDimensions() {
    const base = getAspectPreset();
    const resEl = document.querySelector('input[name="share-resolution"]:checked');
    const resKey = (resEl && resEl.value && RESOLUTION_LONG_SIDE[resEl.value]) ? resEl.value : DEFAULT_RESOLUTION;
    const longSide = RESOLUTION_LONG_SIDE[resKey];
    const scale = longSide / BASE_LONG_SIDE;
    return {
        width: Math.round(base.width * scale),
        height: Math.round(base.height * scale),
    };
}

// Цвета как на карте региона
const FILL_COLOR = 'rgba(99, 130, 255, 0.12)';
const STROKE_COLOR = 'rgba(0, 51, 255, 0.4)';
const STROKE_WIDTH = 2;
const VISITED_COLOR = 'rgb(66, 178, 66)';
const NOT_VISITED_COLOR = 'rgb(210, 90, 90)';
const TILE_SIZE = 256;
const TILE_LOAD_CONCURRENCY = 8;
const TILE_CACHE_MAX_ENTRIES = 300;
const POLYGON_FETCH_TIMEOUT_MS = 12000;

/** Размер маркера-пина на холсте (якорь внизу по центру). */
const PIN_WIDTH = 16;
const PIN_HEIGHT = 22;
const PIN_ANCHOR_X = 8;
const PIN_ANCHOR_Y = 22;

const WATERMARK_PAD = 14;
const WATERMARK_INNER_PAD = 8;
const WATERMARK_LOGO_HEIGHT = 20;
const WATERMARK_LOGO_GAP = 8;
const WATERMARK_TEXT = 'moi-goroda.ru';
const WATERMARK_FONT_SIZE = 14;
const WATERMARK_BG = '#f3f4f6';
const WATERMARK_BORDER = '#9ca3af';
const WATERMARK_BORDER_WIDTH = 1;
const WATERMARK_RADIUS = 6;
const PROGRESS_BADGE_PAD = 14;
const PROGRESS_BADGE_CIRCLE_SIZE = 118;
const PROGRESS_BADGE_RIBBON_WIDTH = 188;
const PROGRESS_BADGE_RIBBON_HEIGHT = 64;
const PROGRESS_BADGE_MINIMAL_WIDTH = 154;
const PROGRESS_BADGE_MINIMAL_HEIGHT = 44;

/** Логотип сайта (глобус из шапки сайдбара), viewBox 0 0 576 512. */
const SITE_LOGO_PATH = 'M408 120c0 54.6-73.1 151.9-105.2 192c-7.7 9.6-22 9.6-29.6 0C241.1 271.9 168 174.6 168 120C168 53.7 221.7 0 288 0s120 53.7 120 120zm8 80.4c3.5-6.9 6.7-13.8 9.6-20.6c.5-1.2 1-2.5 1.5-3.7l116-46.4C558.9 123.4 576 135 576 152V422.8c0 9.8-6 18.6-15.1 22.3L416 503V200.4zM137.6 138.3c2.4 14.1 7.2 28.3 12.8 41.5c2.9 6.8 6.1 13.7 9.6 20.6V451.8L32.9 502.7C17.1 509 0 497.4 0 480.4V209.6c0-9.8 6-18.6 15.1-22.3l122.6-49zM327.8 332c13.9-17.4 35.7-45.7 56.2-77V504.3L192 449.4V255c20.5 31.3 42.3 59.6 56.2 77c20.5 25.6 59.1 25.6 79.6 0zM288 152a40 40 0 1 0 0-80 40 40 0 1 0 0 80z';
const SITE_LOGO_VIEWBOX = { w: 576, h: 512 };
const SITE_LOGO_PATH2D = new Path2D(SITE_LOGO_PATH);

/** SVG пина локации (тот же путь, что в icons.js — locationPinSvg), без тени. */
function locationPinSvgDataUrl(color) {
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512" width="${PIN_WIDTH}" height="${PIN_HEIGHT}"><path fill="${color}" stroke="rgba(0, 0, 0, 0.45)" stroke-width="1" stroke-linejoin="round" d="M215.7 499.2C267 435 384 279.4 384 192C384 86 298 0 192 0S0 86 0 192c0 87.4 117 243 168.3 307.2c12.3 15.3 35.1 15.3 47.4 0zM192 128a64 64 0 1 1 0 128 64 64 0 1 1 0-128z"/></svg>`;
    return 'data:image/svg+xml,' + encodeURIComponent(svg);
}

let pinVisitedImg = null;
let pinNotVisitedImg = null;
let pinImagesReady = null;

function ensurePinImages() {
    if (pinImagesReady) return pinImagesReady;
    pinImagesReady = Promise.all([
        new Promise((resolve) => {
            const img = new Image();
            img.onload = () => { pinVisitedImg = img; resolve(); };
            img.onerror = () => resolve();
            img.src = locationPinSvgDataUrl(VISITED_COLOR);
        }),
        new Promise((resolve) => {
            const img = new Image();
            img.onload = () => { pinNotVisitedImg = img; resolve(); };
            img.onerror = () => resolve();
            img.src = locationPinSvgDataUrl(NOT_VISITED_COLOR);
        }),
    ]);
    return pinImagesReady;
}

const DEFAULT_TILE_LAYER = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
const tileImageCache = new Map();

/**
 * Возвращает массив геометрий для отрисовки (поддержка Feature, FeatureCollection, Geometry).
 */
function getGeometries(geoJson) {
    if (!geoJson) return [];
    if (geoJson.type === 'FeatureCollection' && Array.isArray(geoJson.features)) {
        return geoJson.features
            .map((f) => f.geometry)
            .filter(Boolean);
    }
    const geom = geoJson.geometry || geoJson;
    if (geom.type === 'Polygon' || geom.type === 'MultiPolygon') return [geom];
    return [];
}

/**
 * Собирает все точки [lon, lat] из GeoJSON (полигоны/мультиполигоны, в т.ч. FeatureCollection).
 */
function collectCoordsFromGeoJSON(geoJson) {
    const coords = [];
    function ring(coordList) {
        for (let i = 0; i < coordList.length; i++) coords.push(coordList[i]);
    }
    function polygon(coordRings) {
        for (let r = 0; r < coordRings.length; r++) ring(coordRings[r]);
    }
    function fromGeometry(geom) {
        if (!geom || !geom.coordinates) return;
        if (geom.type === 'Polygon') polygon(geom.coordinates);
        else if (geom.type === 'MultiPolygon') geom.coordinates.forEach((p) => polygon(p));
    }
    const geometries = getGeometries(geoJson);
    for (let g = 0; g < geometries.length; g++) fromGeometry(geometries[g]);
    return coords;
}

/**
 * Преобразует [lon, lat] в пиксели (x, y). North = up.
 * Учитывается cos(широты), чтобы 1° по долготе и 1° по широте давали
 * пропорции как на карте (не сплющивало регион по вертикали).
 */
function project(lon, lat, bbox, mapWidth, mapHeight, pad) {
    const [minLon, minLat, maxLon, maxLat] = bbox;
    const cx = (minLon + maxLon) / 2;
    const cy = (minLat + maxLat) / 2;
    const cosLat = Math.cos((cy * Math.PI) / 180);
    const rangeLonEff = (maxLon - minLon || 1) * Math.max(0.3, cosLat);
    const rangeLat = maxLat - minLat || 1;
    const scaleX = (mapWidth - 2 * pad) / rangeLonEff;
    const scaleY = (mapHeight - 2 * pad) / rangeLat;
    const scale = Math.min(scaleX, scaleY);
    const px = mapWidth / 2 + (lon - cx) * cosLat * scale;
    const py = mapHeight / 2 - (lat - cy) * scale;
    return [px, py];
}

/**
 * Рисует одну геометрию (Polygon или MultiPolygon) на ctx.
 */
function drawGeometry(ctx, geom, bbox, mapWidth, mapHeight, pad) {
    if (!geom || geom.type !== 'Polygon' && geom.type !== 'MultiPolygon') return;

    function drawRing(coordRing, close) {
        if (coordRing.length < 2) return;
        const [x0, y0] = project(coordRing[0][0], coordRing[0][1], bbox, mapWidth, mapHeight, pad);
        ctx.moveTo(x0, y0);
        for (let i = 1; i < coordRing.length; i++) {
            const [x, y] = project(coordRing[i][0], coordRing[i][1], bbox, mapWidth, mapHeight, pad);
            ctx.lineTo(x, y);
        }
        if (close) ctx.closePath();
    }

    ctx.beginPath();
    if (geom.type === 'Polygon') {
        geom.coordinates.forEach((ring) => drawRing(ring, true));
    } else {
        geom.coordinates.forEach((poly) => {
            poly.forEach((ring) => drawRing(ring, true));
        });
    }
    ctx.fillStyle = FILL_COLOR;
    ctx.fill();
    ctx.strokeStyle = STROKE_COLOR;
    ctx.lineWidth = STROKE_WIDTH;
    ctx.stroke();
}

/**
 * Рисует полигон(ы) из GeoJSON на ctx (Feature, FeatureCollection, Geometry).
 */
function drawGeoJSON(ctx, geoJson, bbox, mapWidth, mapHeight, pad) {
    const geometries = getGeometries(geoJson);
    for (let g = 0; g < geometries.length; g++) {
        drawGeometry(ctx, geometries[g], bbox, mapWidth, mapHeight, pad);
    }
}

/**
 * Вычисляет bbox по массиву [lon, lat] и опционально точкам городов.
 */
function computeBbox(polygonCoords, cityPoints) {
    let minLon = Infinity, minLat = Infinity, maxLon = -Infinity, maxLat = -Infinity;
    for (let i = 0; i < polygonCoords.length; i++) {
        const [lon, lat] = polygonCoords[i];
        if (lon < minLon) minLon = lon;
        if (lat < minLat) minLat = lat;
        if (lon > maxLon) maxLon = lon;
        if (lat > maxLat) maxLat = lat;
    }
    if (cityPoints && cityPoints.length) {
        for (let i = 0; i < cityPoints.length; i++) {
            const lon = cityPoints[i].lon, lat = cityPoints[i].lat;
            if (lon < minLon) minLon = lon;
            if (lat < minLat) minLat = lat;
            if (lon > maxLon) maxLon = lon;
            if (lat > maxLat) maxLat = lat;
        }
    }
    if (!isFinite(minLon)) return [0, 0, 1, 1];
    const padLon = (maxLon - minLon) * 0.05 || 0.1;
    const padLat = (maxLat - minLat) * 0.05 || 0.1;
    return [minLon - padLon, minLat - padLat, maxLon + padLon, maxLat + padLat];
}

function getBackgroundOption() {
    const el = document.querySelector('input[name="share-background"]:checked');
    return (el && el.value) || 'none';
}

/**
 * Преобразует lon/lat в пиксели карты Web Mercator при заданном zoom (0–18).
 * Мир = 256 * 2^z пикселей по ширине и высоте.
 */
function lonLatToMercatorPixel(lon, lat, zoom) {
    const n = Math.pow(2, zoom);
    const x = ((lon + 180) / 360) * TILE_SIZE * n;
    const latRad = (lat * Math.PI) / 180;
    const y = (1 - Math.log(Math.tan(Math.PI / 4 + latRad / 2)) / Math.PI) / 2 * TILE_SIZE * n;
    return { x, y };
}

/**
 * Подбирает zoom так, чтобы bbox помещался в область (mapWidth, mapHeight) с отступами.
 */
function getZoomForBbox(bbox, mapWidth, mapHeight, pad) {
    const [minLon, minLat, maxLon, maxLat] = bbox;
    const availableW = mapWidth - 2 * pad;
    const availableH = mapHeight - 2 * pad;
    let bestZ = 10;
    for (let z = 18; z >= 0; z--) {
        const minPx = lonLatToMercatorPixel(minLon, maxLat, z);
        const maxPx = lonLatToMercatorPixel(maxLon, minLat, z);
        const bboxW = maxPx.x - minPx.x;
        const bboxH = maxPx.y - minPx.y;
        const scale = Math.min(availableW / bboxW, availableH / bboxH);
        if (scale >= 0.25) {
            bestZ = z;
            break;
        }
    }
    return bestZ;
}

/**
 * Загружает один тайл как Image. Для CORS используйте прокси или тайл-сервер с заголовком Access-Control-Allow-Origin.
 */
function loadTile(url) {
    const cached = tileImageCache.get(url);
    if (cached) return cached;

    const loadingPromise = new Promise((resolve, reject) => {
        const img = new Image();
        img.crossOrigin = 'anonymous';
        img.onload = () => resolve(img);
        img.onerror = () => {
            tileImageCache.delete(url);
            reject(new Error(`Tile load failed: ${url}`));
        };
        img.src = url;
    }).then((img) => {
        tileImageCache.set(url, Promise.resolve(img));
        // Простой LRU по порядку вставки: ограничиваем рост кэша.
        if (tileImageCache.size > TILE_CACHE_MAX_ENTRIES) {
            const oldestKey = tileImageCache.keys().next().value;
            if (oldestKey) tileImageCache.delete(oldestKey);
        }
        return img;
    });
    tileImageCache.set(url, loadingPromise);
    return loadingPromise;
}

/**
 * Ограничивает параллелизм асинхронных задач (для загрузки тайлов).
 */
async function mapWithConcurrency(items, limit, mapper) {
    if (!Array.isArray(items) || !items.length) return [];
    const safeLimit = Math.max(1, limit | 0);
    const results = new Array(items.length);
    let cursor = 0;

    async function worker() {
        while (cursor < items.length) {
            const idx = cursor++;
            try {
                results[idx] = await mapper(items[idx], idx);
            } catch (_) {
                results[idx] = null;
            }
        }
    }

    const workers = [];
    const workerCount = Math.min(safeLimit, items.length);
    for (let i = 0; i < workerCount; i++) workers.push(worker());
    await Promise.all(workers);
    return results;
}

/**
 * Общий расчёт вида (zoom, scale, offset) в проекции Web Mercator.
 * Пропорции карты сохраняются (один scale). Видимая область расширена под соотношение
 * сторон холста, чтобы подложка заполняла 100% без полос и без растягивания.
 */
function computeMercatorView(bbox, mapWidth, mapHeight, pad) {
    const [minLon, minLat, maxLon, maxLat] = bbox;
    const zoom = getZoomForBbox(bbox, mapWidth, mapHeight, pad);
    const minPx = lonLatToMercatorPixel(minLon, maxLat, zoom);
    const maxPx = lonLatToMercatorPixel(maxLon, minLat, zoom);
    const bboxW = maxPx.x - minPx.x;
    const bboxH = maxPx.y - minPx.y;
    const availableW = mapWidth - 2 * pad;
    const availableH = mapHeight - 2 * pad;
    const canvasAspect = availableW / availableH;
    const bboxAspect = bboxW / bboxH;
    const viewW = bboxAspect >= canvasAspect ? bboxW : bboxH * canvasAspect;
    const viewH = bboxAspect >= canvasAspect ? bboxW / canvasAspect : bboxH;
    const centerX = (minPx.x + maxPx.x) / 2;
    const centerY = (minPx.y + maxPx.y) / 2;
    const viewMinX = centerX - viewW / 2;
    const viewMinY = centerY - viewH / 2;
    const scale = availableW / viewW;
    const offsetX = pad - viewMinX * scale;
    const offsetY = pad - viewMinY * scale;
    return {
        scaleX: scale,
        scaleY: scale,
        offsetX,
        offsetY,
        zoom,
        viewMinX,
        viewMinY,
        viewMaxX: viewMinX + viewW,
        viewMaxY: viewMinY + viewH,
    };
}

/**
 * Рисует подложку из тайлов OpenStreetMap. Вид задаётся mercatorState (расширенная область viewMinX/Y, viewMaxX/Y).
 */
async function drawOsmTiles(ctx, bbox, mercatorState) {
    const { scaleX, scaleY, offsetX, offsetY, zoom, viewMinX, viewMinY, viewMaxX, viewMaxY } = mercatorState;

    const minTileX = Math.floor(viewMinX / TILE_SIZE);
    const maxTileX = Math.ceil(viewMaxX / TILE_SIZE);
    const minTileY = Math.floor(viewMinY / TILE_SIZE);
    const maxTileY = Math.ceil(viewMaxY / TILE_SIZE);

    const tileLayer = (typeof window !== 'undefined' && window.TILE_LAYER && String(window.TILE_LAYER) !== 'None') ? window.TILE_LAYER : DEFAULT_TILE_LAYER;
    const urlTemplate = tileLayer.replace('{s}', 'a').replace('{z}', String(zoom));

    const tileJobs = [];
    const tiles = [];
    for (let ty = minTileY; ty < maxTileY; ty++) {
        for (let tx = minTileX; tx < maxTileX; tx++) {
            const url = urlTemplate.replace('{x}', String(tx)).replace('{y}', String(ty));
            tileJobs.push({ url, tx, ty });
        }
    }
    const results = await mapWithConcurrency(tileJobs, TILE_LOAD_CONCURRENCY, async (job) => {
        const img = await loadTile(job.url);
        return { img, tx: job.tx, ty: job.ty };
    });
    results.forEach((t) => {
        if (t) tiles.push(t);
    });

    const tileW = TILE_SIZE * scaleX;
    const tileH = TILE_SIZE * scaleY;
    for (let i = 0; i < tiles.length; i++) {
        const { img, tx, ty } = tiles[i];
        const dx = offsetX + tx * TILE_SIZE * scaleX;
        const dy = offsetY + ty * TILE_SIZE * scaleY;
        ctx.drawImage(img, dx, dy, tileW, tileH);
    }
}

function mercatorToCanvas(lon, lat, zoom, scaleX, scaleY, offsetX, offsetY) {
    const p = lonLatToMercatorPixel(lon, lat, zoom);
    return { x: offsetX + p.x * scaleX, y: offsetY + p.y * scaleY };
}

function drawGeoJSONMercator(ctx, geoJson, mercatorState, scale) {
    const { scaleX, scaleY, offsetX, offsetY, zoom } = mercatorState;
    const strokeWidth = STROKE_WIDTH * (scale || 1);

    function drawRing(coordRing, close) {
        if (coordRing.length < 2) return;
        const first = mercatorToCanvas(coordRing[0][0], coordRing[0][1], zoom, scaleX, scaleY, offsetX, offsetY);
        ctx.moveTo(first.x, first.y);
        for (let i = 1; i < coordRing.length; i++) {
            const p = mercatorToCanvas(coordRing[i][0], coordRing[i][1], zoom, scaleX, scaleY, offsetX, offsetY);
            ctx.lineTo(p.x, p.y);
        }
        if (close) ctx.closePath();
    }

    const geometries = getGeometries(geoJson);
    for (let g = 0; g < geometries.length; g++) {
        const geom = geometries[g];
        if (!geom || (geom.type !== 'Polygon' && geom.type !== 'MultiPolygon')) continue;
        ctx.beginPath();
        if (geom.type === 'Polygon') {
            geom.coordinates.forEach((ring) => drawRing(ring, true));
        } else {
            geom.coordinates.forEach((poly) => poly.forEach((ring) => drawRing(ring, true)));
        }
        ctx.fillStyle = FILL_COLOR;
        ctx.fill();
        ctx.strokeStyle = STROKE_COLOR;
        ctx.lineWidth = strokeWidth;
        ctx.stroke();
    }
}

/**
 * Рисует сцену на холсте. Если переданы dimensions — рисует в offscreen-холст (для экспорта).
 * Иначе — в видимый холст в разрешении экспорта (как при скачивании), отображаемый в фиксированном размере через CSS.
 */
async function renderToCanvas(geoJson, exportDimensions) {
    const forExport = exportDimensions && exportDimensions.width > 0 && exportDimensions.height > 0;
    const previewRenderSeq = forExport ? null : ++renderSeq;
    const visibleCanvas = document.getElementById('share-image-canvas');
    if (!visibleCanvas) return null;

    // Рисуем всегда на offscreen-холсте, а затем одним вызовом переносим результат
    // в видимый canvas, чтобы избежать моргания при обновлениях превью.
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    if (!ctx) return null;

    const { width: w, height: h } = forExport ? exportDimensions : getExportDimensions();
    canvas.width = w;
    canvas.height = h;

    const mapWidth = w;
    const mapHeight = h;
    const pad = 0;

    const polygonCoords = collectCoordsFromGeoJSON(geoJson);
    const bbox = computeBbox(polygonCoords, all_cities);
    const background = getBackgroundOption();
    const bgColorInput = document.getElementById('share-background-color');
    const bgColor = bgColorInput && bgColorInput.value ? bgColorInput.value : '';
    const mercatorState = computeMercatorView(bbox, mapWidth, mapHeight, pad);

    const baseKey = forExport ? null : JSON.stringify({
        w,
        h,
        background,
        bgColor: background === 'none' ? bgColor : '',
    });

    // Для превью кешируем базовый слой (фон/карта/полигоны/пины),
    // чтобы изменения подписи и водяного знака перерисовывались мгновенно.
    let usedBaseCache = false;
    if (!forExport && baseKey && baseLayerCache && baseLayerCache.key === baseKey && baseLayerCache.canvas) {
        ctx.drawImage(baseLayerCache.canvas, 0, 0, w, h);
        usedBaseCache = true;
    } else {
        let baseBgColor = '#f8fafc';
        if (background === 'none' && bgColor) {
            baseBgColor = bgColor;
        }
        ctx.fillStyle = baseBgColor;
        ctx.fillRect(0, 0, w, h);

        if (background === 'osm') {
            try {
                await drawOsmTiles(ctx, bbox, mercatorState);
            } catch (e) {
                console.warn('Не удалось загрузить тайлы карты:', e);
            }
        }
        if (!forExport && previewRenderSeq !== renderSeq) return null;

        const markerScale = Math.max(w, h) / BASE_LONG_SIDE;
        const pinW = PIN_WIDTH * markerScale;
        const pinH = PIN_HEIGHT * markerScale;
        const pinAnchorX = PIN_ANCHOR_X * markerScale;
        const pinAnchorY = PIN_ANCHOR_Y * markerScale;
        drawGeoJSONMercator(ctx, geoJson, mercatorState, markerScale);
        await ensurePinImages();
        if (!forExport && previewRenderSeq !== renderSeq) return null;
        for (let i = 0; i < all_cities.length; i++) {
            const c = all_cities[i];
            const p = mercatorToCanvas(c.lon, c.lat, mercatorState.zoom, mercatorState.scaleX, mercatorState.scaleY, mercatorState.offsetX, mercatorState.offsetY);
            const pinImg = c.isVisited ? pinVisitedImg : pinNotVisitedImg;
            if (pinImg && pinImg.complete && pinImg.naturalWidth) {
                ctx.drawImage(pinImg, p.x - pinAnchorX, p.y - pinAnchorY, pinW, pinH);
            }
        }

        if (!forExport && baseKey) {
            const baseCanvas = document.createElement('canvas');
            baseCanvas.width = w;
            baseCanvas.height = h;
            const baseCtx = baseCanvas.getContext('2d');
            if (baseCtx) {
                baseCtx.drawImage(canvas, 0, 0, w, h);
                baseLayerCache = { key: baseKey, canvas: baseCanvas };
            }
        }
    }

    const markerScale = Math.max(w, h) / BASE_LONG_SIDE;

    const caption = getCaptionText();
    const captionOptions = getCaptionOptions();
    if (caption) {
        if (forExport) {
            // Для экспорта дожидаемся загрузки шрифта, чтобы получить корректный результат.
            await ensureCaptionFontLoaded(captionOptions);
        } else {
            // Для превью не ждём загрузку шрифта, чтобы убрать визуальную задержку.
            // Шрифт загружается асинхронно, и после загрузки мы триггерим дополнительный рендер.
            ensureCaptionFontLoaded(captionOptions);
        }
    }
    if (!forExport && previewRenderSeq !== renderSeq) return null;
    if (caption) {
        drawCaption(ctx, caption, captionOptions, w, h, markerScale);
    }

    if (lastPositionChangeSource === 'watermark') {
        drawWatermark(ctx, w, h, markerScale, []);
        const watermarkPos = getWatermarkPosition();
        const s = markerScale || 1;
        const wmBadge = getWatermarkBadge(s);
        let watermarkRect = null;
        if (wmBadge && watermarkPos !== 'off') {
            const wmPad = WATERMARK_PAD * s;
            const wmW = wmBadge.width;
            const wmH = wmBadge.height;
            watermarkRect = {
                x: (watermarkPos === 'top-right' || watermarkPos === 'bottom-right') ? w - wmPad - wmW : wmPad,
                y: (watermarkPos === 'top-left' || watermarkPos === 'top-right') ? wmPad : h - wmPad - wmH,
                w: wmW,
                h: wmH,
            };
        }
        const blocked = watermarkRect ? [watermarkRect] : [];
        drawProgressBadge(ctx, w, h, markerScale, blocked);
    } else {
        const badgeRect = drawProgressBadge(ctx, w, h, markerScale, []);
        const occupiedRects = badgeRect ? [badgeRect] : [];
        drawWatermark(ctx, w, h, markerScale, occupiedRects);
    }

    if (forExport) {
        // Для экспорта возвращаем offscreen-холст как есть
        return canvas;
    }

    // Для превью — копируем результат в видимый canvas одним кадром
    const display = getDisplayDimensions();
    visibleCanvas.width = w;
    visibleCanvas.height = h;
    visibleCanvas.style.width = display.width + 'px';
    visibleCanvas.style.height = display.height + 'px';
    const visibleCtx = visibleCanvas.getContext('2d');
    if (!visibleCtx) return null;
    visibleCtx.clearRect(0, 0, w, h);
    visibleCtx.drawImage(canvas, 0, 0, w, h);

    return visibleCanvas;
}

let renderSeq = 0;
let baseLayerCache = null;

let rafPreviewScheduled = false;
let rafPreviewPending = false;

function schedulePreviewRender() {
    // Схлопываем серию input-событий в один рендер на кадр.
    rafPreviewPending = true;
    if (rafPreviewScheduled) return;
    rafPreviewScheduled = true;
    requestAnimationFrame(() => {
        rafPreviewScheduled = false;
        if (!rafPreviewPending) return;
        rafPreviewPending = false;
        if (!geoJsonData) return;
        renderToCanvas(geoJsonData).catch((e) => console.warn(e));
    });
}

function getPrimaryFontName(fontStack) {
    if (!fontStack || typeof fontStack !== 'string') return null;
    const m = fontStack.match(/"([^"]+)"/);
    return m ? m[1] : null;
}

const captionFontLoadCache = new Map();
const FONT_LOAD_SAMPLE_TEXT = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ абвгдежзийклмнопрстуфхцчшщъыьэюя 0123456789';

function getCaptionFontCacheKey(options) {
    const familyStack = FONT_FAMILIES[options.fontFamily] || FONT_FAMILIES.roboto;
    const primary = getPrimaryFontName(familyStack);
    if (!primary) return null;
    const weight = options.fontWeight || 'normal';
    const size = Number(options.fontSize) || 20;
    return `${primary}::${weight}::${size}`;
}

function ensureCaptionFontLoaded(options) {
    try {
        if (!document.fonts || !document.fonts.load) return;
        const familyStack = FONT_FAMILIES[options.fontFamily] || FONT_FAMILIES.roboto;
        const primary = getPrimaryFontName(familyStack);
        if (!primary) return;
        const weight = options.fontWeight || 'normal';
        // На всякий случай грузим и размер по умолчанию, и текущий
        const size = Number(options.fontSize) || 20;
        const key = `${primary}::${weight}::${size}`;
        let p = captionFontLoadCache.get(key);
        if (!p) {
            // Явно указываем sample text с кириллицей и цифрами, чтобы браузер
            // загрузил нужные глифы сразу, а не только latin subset.
            p = document.fonts
                .load(`${weight} ${size}px "${primary}"`, FONT_LOAD_SAMPLE_TEXT)
                .then(() => {
                    // После загрузки шрифта принудительно перерисовываем превью,
                    // чтобы весь текст отрисовался уже новым шрифтом.
                    if (geoJsonData) schedulePreviewRender();
                })
                .catch((e) => {
                    console.warn('Не удалось загрузить шрифт подписи:', e);
                });
            captionFontLoadCache.set(key, p);
        }
        return p;
    } catch (e) {
        // Не блокируем рендер, если Fonts API недоступен/ошибка
        console.warn('Не удалось дождаться загрузки шрифта:', e);
        return;
    }
}

function hexToRgb(hex) {
    const m = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return m ? { r: parseInt(m[1], 16), g: parseInt(m[2], 16), b: parseInt(m[3], 16) } : { r: 255, g: 255, b: 255 };
}

/** Шаблоны подписи для соцсетей (достижение цели). Плейсхолдеры: {numVisited}, {numCities}, {cityWord}, {regionName}, {regionNameIn} (в Калужской области), {regionNameGenitive} (Калужской области). */
const CAPTION_PRESETS = [
    'Уже {numVisited} {cityWord} из {numCities} в {regionNameIn}!',
    'Мой прогресс в {regionNameIn}: {numVisited} из {numCities}',
    '{regionName}: {numVisited} из {numCities}',
    'Путешествую по {regionNameIn}: {numVisited} {cityWord} из {numCities}',
    'В моей копилке уже {numVisited} {cityWord} из {numCities} в {regionNameIn}',
    'Отмечено {numVisited} {cityWord} из {numCities} в {regionNameIn}',
    'Иду к цели в {regionNameIn}: {numVisited} из {numCities}',
    '{regionName} — посещено {numVisited} из {numCities}',
    'Мой результат: {numVisited} {cityWord} из {numCities} в {regionNameIn}',
    'Продолжаю маршрут по {regionNameIn}: {numVisited} из {numCities}',
    'Потихоньку закрываю {regionNameGenitive}: {numVisited} {cityWord} из {numCities}',
    'Кто со мной в {regionNameIn}? {numVisited} {cityWord} из {numCities} уже в копилке',
];

/** Склонение слова «город» по числу: 1 город, 2/3/4 города, 5–20 городов, 21 город, … */
function pluralFormCity(n) {
    const num = Math.abs(Number(n));
    const mod10 = num % 10;
    const mod100 = num % 100;
    if (mod100 >= 11 && mod100 <= 14) return 'городов';
    if (mod10 === 1) return 'город';
    if (mod10 >= 2 && mod10 <= 4) return 'города';
    return 'городов';
}

/** Название региона в предложном падеже (для «в …»: в Калужской области, в Москве). */
function regionNameToPrepositional(name) {
    if (!name || typeof name !== 'string') return name || '';
    const s = name.trim();
    if (!s) return s;
    if (/\s*область\s*$/i.test(s)) {
        return s.replace(/(\w*)(ская)\s+область\s*$/i, '$1ской области').replace(/(\w*)(кая)\s+область\s*$/i, '$1кой области');
    }
    if (/\s*край\s*$/i.test(s)) {
        return s.replace(/(\w*)(ский)\s+край\s*$/i, '$1ском крае').replace(/(\w*)(ий)\s+край\s*$/i, '$1ом крае');
    }
    if (/^Республика\s+/i.test(s)) {
        return s.replace(/^Республика\s+/i, 'Республике ');
    }
    // ХХХская республика / ХХХая республика → ХХХской/ХХХой республике
    if (/\s*республика\s*$/i.test(s)) {
        return s
            .replace(/(\S+?)(ая)\s+республика\s*$/i, '$1ой республике')
            .replace(/(\S+?)(яя)\s+республика\s*$/i, '$1ей республике')
            .replace(/\s+республика\s*$/i, ' республике');
    }
    if (/^Москва\s*$/i.test(s)) return 'Москве';
    if (/^Санкт-Петербург\s*$/i.test(s)) return 'Санкт-Петербурге';
    if (/^Севастополь\s*$/i.test(s)) return 'Севастополе';
    return s;
}

/** Название региона в родительном падеже (для «региона …»). */
function regionNameToGenitive(name) {
    if (!name || typeof name !== 'string') return name || '';
    const s = name.trim();
    if (!s) return s;
    // ХХХская область → ХХХской области
    if (/\s*область\s*$/i.test(s)) {
        return s.replace(/(\w*)(ская)\s+область\s*$/i, '$1ской области').replace(/(\w*)(кая)\s+область\s*$/i, '$1кой области');
    }
    // ХХХский край → ХХХского края, ХХХий край → ХХХого края
    if (/\s*край\s*$/i.test(s)) {
        return s.replace(/(\w*)(ский)\s+край\s*$/i, '$1ского края').replace(/(\w*)(ий)\s+край\s*$/i, '$1ого края');
    }
    // Республика ХХХ — в родительном «Республики ХХХ»
    if (/^Республика\s+/i.test(s)) {
        return s.replace(/^Республика\s+/i, 'Республики ');
    }
    // ХХХская республика / ХХХая республика → ХХХской/ХХХой республики
    if (/\s*республика\s*$/i.test(s)) {
        return s
            .replace(/(\S+?)(ая)\s+республика\s*$/i, '$1ой республики')
            .replace(/(\S+?)(яя)\s+республика\s*$/i, '$1ей республики')
            .replace(/\s+республика\s*$/i, ' республики');
    }
    // Города: Москва → Москвы, Санкт-Петербург → Санкт-Петербурга (упрощённо)
    if (/^Москва\s*$/i.test(s)) return 'Москвы';
    if (/^Санкт-Петербург\s*$/i.test(s)) return 'Санкт-Петербурга';
    if (/^Севастополь\s*$/i.test(s)) return 'Севастополя';
    // По умолчанию — как есть (избегаем неверного склонения)
    return s;
}

function applyCaptionPlaceholders(text) {
    const cityWord = pluralFormCity(numVisited);
    const regionIn = regionNameToPrepositional(regionName);
    return text
        .replace(/\{numVisited\}/g, String(numVisited))
        .replace(/\{numCities\}/g, String(numCities))
        .replace(/\{cityWord\}/g, cityWord)
        .replace(/\{regionNameIn\}/g, regionIn)
        .replace(/\{regionNameGenitive\}/g, regionNameToGenitive(regionName))
        .replace(/\{regionName\}/g, regionName);
}

function getCaptionText() {
    const modeEl = document.querySelector('input[name="caption-text-mode"]:checked');
    const mode = modeEl ? modeEl.value : 'preset';
    if (mode === 'none') {
        return '';
    }
    if (mode === 'custom') {
        const customEl = document.getElementById('caption-text-custom');
        const raw = customEl && customEl.value ? customEl.value.trim() : '';
        if (raw) return raw;
        return applyCaptionPlaceholders(CAPTION_PRESETS[0]);
    }
    const selectEl = document.getElementById('caption-text-preset');
    const value = selectEl ? selectEl.value : '0';
    const index = parseInt(value, 10);
    const template = (index >= 0 && index < CAPTION_PRESETS.length) ? CAPTION_PRESETS[index] : CAPTION_PRESETS[0];
    return applyCaptionPlaceholders(template);
}

function getCaptionOptions() {
    const positionEl = document.querySelector('input[name="caption-position"]:checked');
    const alignEl = document.querySelector('input[name="caption-align"]:checked');
    const sizeEl = document.getElementById('caption-font-size');
    const familyEl = document.getElementById('caption-font-family');
    const weightEl = document.querySelector('input[name="caption-font-weight"]:checked');
    const bgEl = document.querySelector('input[name="caption-background"]:checked');
    const bgColorEl = document.getElementById('caption-bg-color');
    const bgSizeEl = document.getElementById('caption-bg-size');
    const bgOpacityEl = document.getElementById('caption-bg-opacity');
    const bgBlurEl = document.getElementById('caption-bg-blur');
    const textColorEl = document.getElementById('caption-text-color');
    const bgColor = (bgColorEl && bgColorEl.value) ? bgColorEl.value : '#ef4444';
    const bgSizeRaw = bgSizeEl && bgSizeEl.value !== undefined ? parseInt(bgSizeEl.value, 10) : 100;
    const bgSize = Math.max(50, Math.min(300, bgSizeRaw)) / 100;
    const bgOpacity = bgOpacityEl && bgOpacityEl.value !== undefined ? parseInt(bgOpacityEl.value, 10) : 50;
    const bgBlur = bgBlurEl && bgBlurEl.value !== undefined ? parseInt(bgBlurEl.value, 10) : 10;
    const textColor = (textColorEl && textColorEl.value) ? textColorEl.value : '#1f2937';
    return {
        position: (positionEl && positionEl.value) || 'bottom',
        alignment: (alignEl && alignEl.value) || 'center',
        fontSize: sizeEl ? parseInt(sizeEl.value, 10) : 20,
        fontFamily: (familyEl && familyEl.value) || 'roboto',
        fontWeight: (weightEl && weightEl.value) || 'bold',
        background: (bgEl && bgEl.value) || 'box',
        bgColor,
        bgSize,
        // bgOpacitySlider: 0% = нет прозрачности (полностью видно), 100% = полностью прозрачно
        bgOpacity: 1 - Math.max(0, Math.min(100, bgOpacity)) / 100,
        bgBlur: Math.max(0, Math.min(20, bgBlur)),
        textColor,
    };
}

/**
 * Возвращает прямоугольник области для подписи в зависимости от положения.
 * Якорная область не зависит от «Размера» (размер влияет только на бокс/обводку).
 */
function getCaptionAnchorBox(position, canvasWidth, canvasHeight, scale) {
    const pad = CAPTION_PADDING * scale;
    const capHeight = CAPTION_HEIGHT * scale;
    if (position === 'top') {
        return { x: pad, y: pad, w: canvasWidth - 2 * pad, h: capHeight };
    }
    if (position === 'bottom') {
        return { x: pad, y: canvasHeight - pad - capHeight, w: canvasWidth - 2 * pad, h: capHeight };
    }
    if (position === 'center') {
        return { x: pad, y: (canvasHeight - capHeight) / 2, w: canvasWidth - 2 * pad, h: capHeight };
    }
    return { x: pad, y: canvasHeight - pad - capHeight, w: canvasWidth - 2 * pad, h: capHeight };
}

/**
 * Разбивает текст на строки по maxWidth.
 */
function measureWrappedLines(ctx, text, maxWidth) {
    const words = text.split(/\s+/);
    const lines = [];
    let line = '';
    for (let i = 0; i < words.length; i++) {
        const next = line ? line + ' ' + words[i] : words[i];
        const m = ctx.measureText(next);
        if (m.width > maxWidth && line) {
            lines.push(line);
            line = words[i];
        } else line = next;
    }
    if (line) lines.push(line);
    return lines;
}

const FONT_FAMILIES = {
    roboto: '"Roboto", system-ui, -apple-system, "Segoe UI", sans-serif',
    montserrat: '"Montserrat", system-ui, -apple-system, "Segoe UI", sans-serif',
    open_sans: '"Open Sans", system-ui, -apple-system, "Segoe UI", sans-serif',
    rubik: '"Rubik", system-ui, -apple-system, "Segoe UI", sans-serif',
    sofia_sans: '"Sofia Sans", system-ui, -apple-system, "Segoe UI", sans-serif',

    eb_garamond: '"EB Garamond", "Georgia", "Times New Roman", serif',
    playfair: '"Playfair Display", "Georgia", "Times New Roman", serif',
    oswald: '"Oswald", system-ui, -apple-system, "Segoe UI", sans-serif',
    comfortaa: '"Comfortaa", system-ui, -apple-system, "Segoe UI", sans-serif',

    bad_script: '"Bad Script", "Comic Sans MS", system-ui, cursive',
    caveat: '"Caveat", "Comic Sans MS", system-ui, cursive',
    pacifico: '"Pacifico", "Comic Sans MS", system-ui, cursive',
    lobster: '"Lobster", "Comic Sans MS", system-ui, cursive',
    great_vibes: '"Great Vibes", "Comic Sans MS", system-ui, cursive',

    press_start_2p: '"Press Start 2P", "Courier New", ui-monospace, monospace',
    rubik_marker_hatch: '"Rubik Marker Hatch", system-ui, -apple-system, "Segoe UI", sans-serif',
    rubik_wet_paint: '"Rubik Wet Paint", system-ui, -apple-system, "Segoe UI", sans-serif',

    line_seed_jp: '"LINE Seed JP", system-ui, -apple-system, "Segoe UI", sans-serif',
};

function drawCaption(ctx, caption, options, canvasWidth, canvasHeight, scale) {
    const { position, alignment, fontSize, fontFamily, fontWeight, background, bgColor, bgSize, bgOpacity, bgBlur, textColor } = options;
    const s = scale || 1;
    const sizeMult = (bgSize && bgSize > 0) ? bgSize : 1;
    const anchorBox = getCaptionAnchorBox(position, canvasWidth, canvasHeight, s);
    const padWrap = CAPTION_PADDING * s;
    const padBox = CAPTION_PADDING * s * sizeMult;
    const effectiveFontSize = fontSize * s;

    const maxTextWidthForWrap = anchorBox.w - 2 * padWrap;
    const lineHeight = Math.round(effectiveFontSize * 1.15);

    ctx.font = `${fontWeight} ${effectiveFontSize}px ${FONT_FAMILIES[fontFamily] || FONT_FAMILIES.sans}`;
    const lines = measureWrappedLines(ctx, caption, maxTextWidthForWrap);
    const textBlockHeight = lines.length * lineHeight;

    // Фактическая ширина текста (для бокса по тексту)
    let actualMaxLineWidth = 0;
    for (let i = 0; i < lines.length; i++) {
        const w = ctx.measureText(lines[i]).width;
        if (w > actualMaxLineWidth) actualMaxLineWidth = w;
    }

    // Базовый бокс: прямоугольник, в который должен поместиться весь текст
    let boxX = anchorBox.x;
    let boxY = anchorBox.y;
    let boxW = anchorBox.w;
    let boxH = anchorBox.h;

    const boxBg = background || 'box';
    // Всегда рассчитываем размеры бокса по фактическому тексту, чтобы текст не выходил за экран
    const padForBox = boxBg === 'box' ? padBox : padWrap;
    const desiredW = Math.min(anchorBox.w, actualMaxLineWidth + 2 * padForBox);
    const desiredH = textBlockHeight + 2 * padForBox;
    boxW = desiredW;
    boxH = desiredH;
    if (alignment === 'center') {
        boxX = canvasWidth / 2 - boxW / 2;
    } else if (alignment === 'right') {
        boxX = anchorBox.x + anchorBox.w - boxW;
    } else {
        boxX = anchorBox.x;
    }
    boxY = anchorBox.y + (anchorBox.h - boxH) / 2;

    // Гарантируем, что подпись и её фон не выходят за пределы изображения
    const outerPad = CAPTION_PADDING * s;
    const maxBoxW = Math.max(0, canvasWidth - 2 * outerPad);
    const maxBoxH = Math.max(0, canvasHeight - 2 * outerPad);
    if (boxW > maxBoxW) boxW = maxBoxW;
    if (boxH > maxBoxH) boxH = maxBoxH;
    if (boxX < outerPad) boxX = outerPad;
    if (boxY < outerPad) boxY = outerPad;
    if (boxX + boxW > canvasWidth - outerPad) boxX = canvasWidth - outerPad - boxW;
    if (boxY + boxH > canvasHeight - outerPad) boxY = canvasHeight - outerPad - boxH;

    const startY = boxY + (boxH - textBlockHeight) / 2 + lineHeight / 2;

    const rgb = hexToRgb(bgColor || '#ffffff');
    const alpha = typeof bgOpacity === 'number' ? bgOpacity : 0.5;
    const bgRgba = `rgba(${rgb.r},${rgb.g},${rgb.b},${alpha})`;
    const borderRgba = 'rgba(0,0,0,0.06)';

    const blurPx = (typeof bgBlur === 'number' ? bgBlur : 0) * s;
    const needFilter = blurPx > 0 && (boxBg === 'box' || boxBg === 'outline');

    if (boxBg === 'box') {
        if (needFilter) ctx.save();
        if (needFilter) ctx.filter = `blur(${blurPx}px)`;
        ctx.fillStyle = bgRgba;
        roundRect(ctx, boxX, boxY, boxW, boxH, 10 * s);
        ctx.fill();
        if (needFilter) ctx.restore();
    }

    ctx.fillStyle = textColor || '#1f2937';
    ctx.textBaseline = 'middle';
    const hasOutline = boxBg === 'outline';
    if (hasOutline) {
        ctx.strokeStyle = bgRgba;
        ctx.lineWidth = 2 * s * sizeMult;
    }

    function drawLine(x, y, line) {
        if (hasOutline) {
            if (needFilter) ctx.save();
            if (needFilter) ctx.filter = `blur(${blurPx}px)`;
            ctx.strokeText(line, x, y);
            if (needFilter) ctx.restore();
        }
        ctx.fillText(line, x, y);
    }

    const padText = boxBg === 'box' ? padBox : padWrap;
    if (alignment === 'left') {
        ctx.textAlign = 'left';
        const textX = boxX + padText;
        for (let i = 0; i < lines.length; i++) {
            drawLine(textX, startY + i * lineHeight, lines[i]);
        }
    } else if (alignment === 'right') {
        ctx.textAlign = 'right';
        const textX = boxX + boxW - padText;
        for (let i = 0; i < lines.length; i++) {
            drawLine(textX, startY + i * lineHeight, lines[i]);
        }
    } else {
        ctx.textAlign = 'center';
        const textX = boxX + boxW / 2;
        for (let i = 0; i < lines.length; i++) {
            drawLine(textX, startY + i * lineHeight, lines[i]);
        }
    }
}

function getWatermarkPosition() {
    const el = document.querySelector('input[name="share-watermark"]:checked');
    return (el && el.value && el.value !== 'off') ? el.value : 'off';
}

let suppressPositionSourceTracking = false;
let lastPositionChangeSource = 'badge';

function setWatermarkPositionControl(position, options) {
    if (!position || position === 'off') return;
    const target = document.querySelector(`input[name="share-watermark"][value="${position}"]`);
    if (!target || target.disabled || target.checked) return;
    const silent = options && options.silent;
    if (silent) suppressPositionSourceTracking = true;
    target.checked = true;
    target.dispatchEvent(new Event('change', { bubbles: true }));
    if (silent) suppressPositionSourceTracking = false;
}

function setProgressBadgePositionControl(position, options) {
    if (!position || position === 'off') return;
    const target = document.querySelector(`input[name="share-progress-badge-position"][value="${position}"]`);
    if (!target || target.disabled || target.checked) return;
    const silent = options && options.silent;
    if (silent) suppressPositionSourceTracking = true;
    target.checked = true;
    target.dispatchEvent(new Event('change', { bubbles: true }));
    if (silent) suppressPositionSourceTracking = false;
}

const watermarkBadgeCache = new Map();

function getWatermarkBadge(scale) {
    const s = scale || 1;
    const key = `${Math.round(s * 100) / 100}`;
    const cached = watermarkBadgeCache.get(key);
    if (cached) return cached;

    const innerPad = WATERMARK_INNER_PAD * s;
    const logoGap = WATERMARK_LOGO_GAP * s;
    const logoH = WATERMARK_LOGO_HEIGHT * s;
    const logoW = (SITE_LOGO_VIEWBOX.w / SITE_LOGO_VIEWBOX.h) * logoH;
    const fontSize = Math.round(WATERMARK_FONT_SIZE * s);

    const off = document.createElement('canvas');
    const offCtx = off.getContext('2d');
    if (!offCtx) return null;

    offCtx.font = `${fontSize}px system-ui, sans-serif`;
    const textW = offCtx.measureText(WATERMARK_TEXT).width;
    const lineH = fontSize * 1.2;
    const boxW = Math.ceil(innerPad + logoW + logoGap + textW + innerPad);
    const boxH = Math.ceil(Math.max(logoH, lineH) + 2 * innerPad);
    const radius = Math.max(2, WATERMARK_RADIUS * s);

    off.width = boxW;
    off.height = boxH;
    offCtx.font = `${fontSize}px system-ui, sans-serif`;

    roundRect(offCtx, 0, 0, boxW, boxH, radius);
    offCtx.fillStyle = WATERMARK_BG;
    offCtx.fill();
    offCtx.strokeStyle = WATERMARK_BORDER;
    offCtx.lineWidth = WATERMARK_BORDER_WIDTH;
    offCtx.stroke();

    const logoBlockW = Math.ceil(logoW);
    const logoBlockH = Math.ceil(logoH);
    const logoCanvas = document.createElement('canvas');
    logoCanvas.width = logoBlockW;
    logoCanvas.height = logoBlockH;
    const logoCtx = logoCanvas.getContext('2d');
    if (logoCtx) {
        logoCtx.fillStyle = '#374151';
        logoCtx.scale(logoBlockW / SITE_LOGO_VIEWBOX.w, logoBlockH / SITE_LOGO_VIEWBOX.h);
        logoCtx.fill(SITE_LOGO_PATH2D);
        const logoY = (boxH - logoH) / 2;
        offCtx.drawImage(logoCanvas, innerPad, logoY, logoBlockW, logoBlockH);
    }

    const textX = innerPad + logoW + logoGap;
    offCtx.fillStyle = '#374151';
    offCtx.textAlign = 'left';
    offCtx.textBaseline = 'middle';
    offCtx.fillText(WATERMARK_TEXT, textX, boxH / 2);

    watermarkBadgeCache.set(key, off);
    if (watermarkBadgeCache.size > 10) {
        const oldestKey = watermarkBadgeCache.keys().next().value;
        if (oldestKey) watermarkBadgeCache.delete(oldestKey);
    }
    return off;
}

function drawWatermark(ctx, canvasWidth, canvasHeight, scale, occupiedRects) {
    const pos = getWatermarkPosition();
    if (pos === 'off') return;
    const s = scale || 1;
    const pad = WATERMARK_PAD * s;
    const badge = getWatermarkBadge(s);
    if (!badge) return;
    const boxW = badge.width;
    const boxH = badge.height;

    function positionToRect(position) {
        let x;
        let y;
        if (position === 'top-right' || position === 'bottom-right') x = canvasWidth - pad - boxW;
        else x = pad;
        if (position === 'top-left' || position === 'top-right') y = pad;
        else y = canvasHeight - pad - boxH;
        return { x, y, w: boxW, h: boxH };
    }

    function rectsOverlap(a, b) {
        if (!a || !b) return false;
        return !(a.x + a.w <= b.x || b.x + b.w <= a.x || a.y + a.h <= b.y || b.y + b.h <= a.y);
    }

    const blockedRects = Array.isArray(occupiedRects) ? occupiedRects : [];
    const candidates = [pos, 'top-right', 'top-left', 'bottom-right', 'bottom-left'];
    let chosen = positionToRect(pos);
    let chosenPosition = pos;
    for (let i = 0; i < candidates.length; i++) {
        const candidatePosition = candidates[i];
        const candidateRect = positionToRect(candidatePosition);
        const hasCollision = blockedRects.some((r) => rectsOverlap(candidateRect, r));
        if (!hasCollision) {
            chosen = candidateRect;
            chosenPosition = candidatePosition;
            break;
        }
    }

    if (chosenPosition !== pos) {
        setWatermarkPositionControl(chosenPosition, { silent: true });
    }

    ctx.drawImage(badge, chosen.x, chosen.y, boxW, boxH);
}

function roundRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y);
    ctx.quadraticCurveTo(x + w, y, x + w, y + r);
    ctx.lineTo(x + w, y + h - r);
    ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    ctx.lineTo(x + r, y + h);
    ctx.quadraticCurveTo(x, y + h, x, y + h - r);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.closePath();
}

function getProgressBadgeOptions() {
    const enabledEl = document.querySelector('input[name="share-progress-badge-enabled"]:checked');
    const styleEl = document.querySelector('input[name="share-progress-badge-style"]:checked');
    const positionEl = document.querySelector('input[name="share-progress-badge-position"]:checked');
    const percentRaw = numCities > 0 ? Math.round((numVisited / numCities) * 100) : 0;
    return {
        enabled: !!enabledEl && enabledEl.value !== 'off',
        style: (styleEl && styleEl.value) || 'circle',
        position: (positionEl && positionEl.value) || 'top-left',
        percent: Math.max(0, Math.min(100, percentRaw)),
        ratioText: `${numVisited} / ${numCities}`,
    };
}

function drawProgressBadge(ctx, canvasWidth, canvasHeight, scale, occupiedRects) {
    const options = getProgressBadgeOptions();
    if (!options.enabled) return null;

    const s = scale || 1;
    const pad = PROGRESS_BADGE_PAD * s;
    const pos = options.position;
    const isRight = pos === 'top-right' || pos === 'bottom-right';
    const isTop = pos === 'top-left' || pos === 'top-right';

    function startRect(width, height) {
        const x = isRight ? canvasWidth - pad - width : pad;
        const y = isTop ? pad : canvasHeight - pad - height;
        return { x, y, w: width, h: height };
    }

    function rectsOverlap(a, b) {
        if (!a || !b) return false;
        return !(a.x + a.w <= b.x || b.x + b.w <= a.x || a.y + a.h <= b.y || b.y + b.h <= a.y);
    }

    function resolveRect(width, height) {
        const blockedRects = Array.isArray(occupiedRects) ? occupiedRects : [];
        const candidates = [options.position, 'top-right', 'top-left', 'bottom-right', 'bottom-left'];
        let chosenPosition = options.position;
        let chosenRect = startRect(width, height);
        for (let i = 0; i < candidates.length; i++) {
            const candidatePosition = candidates[i];
            const candidateIsRight = candidatePosition === 'top-right' || candidatePosition === 'bottom-right';
            const candidateIsTop = candidatePosition === 'top-left' || candidatePosition === 'top-right';
            const candidateRect = {
                x: candidateIsRight ? canvasWidth - pad - width : pad,
                y: candidateIsTop ? pad : canvasHeight - pad - height,
                w: width,
                h: height,
            };
            const hasCollision = blockedRects.some((r) => rectsOverlap(candidateRect, r));
            if (!hasCollision) {
                chosenPosition = candidatePosition;
                chosenRect = candidateRect;
                break;
            }
        }
        if (chosenPosition !== options.position) {
            setProgressBadgePositionControl(chosenPosition, { silent: true });
        }
        return chosenRect;
    }

    if (options.style === 'ribbon') {
        const rect = resolveRect(PROGRESS_BADGE_RIBBON_WIDTH * s, PROGRESS_BADGE_RIBBON_HEIGHT * s);
        const w = rect.w;
        const h = rect.h;
        const x = rect.x;
        const y = rect.y;

        roundRect(ctx, x, y, w, h, 12 * s);
        ctx.fillStyle = 'rgba(17, 24, 39, 0.84)';
        ctx.fill();
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.35)';
        ctx.lineWidth = Math.max(1, 1.25 * s);
        ctx.stroke();

        const textX = x + w / 2;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';

        ctx.fillStyle = '#f9fafb';
        ctx.font = `700 ${Math.round(22 * s)}px system-ui, sans-serif`;
        ctx.fillText(`${options.percent}%`, textX, y + h * 0.4);

        ctx.fillStyle = 'rgba(249, 250, 251, 0.9)';
        ctx.font = `600 ${Math.round(14 * s)}px system-ui, sans-serif`;
        ctx.fillText(options.ratioText, textX, y + h * 0.72);
        return { x, y, w, h };
    }

    if (options.style === 'glass') {
        const rect = resolveRect(PROGRESS_BADGE_RIBBON_WIDTH * s, PROGRESS_BADGE_RIBBON_HEIGHT * s);
        const w = rect.w;
        const h = rect.h;
        const x = rect.x;
        const y = rect.y;

        roundRect(ctx, x, y, w, h, 14 * s);
        ctx.fillStyle = 'rgba(255, 255, 255, 0.62)';
        ctx.fill();
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.85)';
        ctx.lineWidth = Math.max(1, 1.5 * s);
        ctx.stroke();

        roundRect(ctx, x + 2 * s, y + 2 * s, w - 4 * s, h * 0.42, 12 * s);
        ctx.fillStyle = 'rgba(255, 255, 255, 0.45)';
        ctx.fill();

        const textX = x + w / 2;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';

        ctx.fillStyle = '#0f172a';
        ctx.font = `800 ${Math.round(24 * s)}px system-ui, sans-serif`;
        ctx.fillText(`${options.percent}%`, textX, y + h * 0.42);

        ctx.fillStyle = 'rgba(15, 23, 42, 0.88)';
        ctx.font = `700 ${Math.round(13 * s)}px system-ui, sans-serif`;
        ctx.fillText(`${options.ratioText} городов`, textX, y + h * 0.74);
        return { x, y, w, h };
    }

    if (options.style === 'minimal') {
        const rect = resolveRect(PROGRESS_BADGE_MINIMAL_WIDTH * s, PROGRESS_BADGE_MINIMAL_HEIGHT * s);
        const w = rect.w;
        const h = rect.h;
        const x = rect.x;
        const y = rect.y;
        const progressW = (w - 4 * s) * (options.percent / 100);

        roundRect(ctx, x, y, w, h, 10 * s);
        ctx.fillStyle = 'rgba(2, 6, 23, 0.72)';
        ctx.fill();
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.28)';
        ctx.lineWidth = Math.max(1, 1.1 * s);
        ctx.stroke();

        roundRect(ctx, x + 2 * s, y + h - 10 * s, w - 4 * s, 7 * s, 4 * s);
        ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
        ctx.fill();
        roundRect(ctx, x + 2 * s, y + h - 10 * s, progressW, 7 * s, 4 * s);
        ctx.fillStyle = '#22c55e';
        ctx.fill();

        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillStyle = '#f8fafc';
        ctx.font = `700 ${Math.round(14 * s)}px system-ui, sans-serif`;
        ctx.fillText(`${options.ratioText} · ${options.percent}%`, x + w / 2, y + h * 0.42);
        return { x, y, w, h };
    }

    const size = PROGRESS_BADGE_CIRCLE_SIZE * s;
    const radius = size / 2;
    const rect = resolveRect(size, size);
    const x = rect.x;
    const y = rect.y;
    const cx = x + radius;
    const cy = y + radius;

    ctx.beginPath();
    ctx.arc(cx, cy, radius, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(17, 24, 39, 0.84)';
    ctx.fill();
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.35)';
    ctx.lineWidth = Math.max(1, 1.25 * s);
    ctx.stroke();

    ctx.beginPath();
    ctx.arc(cx, cy, radius * 0.76, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * (options.percent / 100), false);
    ctx.strokeStyle = '#22c55e';
    ctx.lineWidth = Math.max(2, 6 * s);
    ctx.lineCap = 'round';
    ctx.stroke();

    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = '#f9fafb';
    ctx.font = `700 ${Math.round(24 * s)}px system-ui, sans-serif`;
    ctx.fillText(`${options.percent}%`, cx, cy - 9 * s);

    ctx.fillStyle = 'rgba(249, 250, 251, 0.9)';
    ctx.font = `600 ${Math.round(13 * s)}px system-ui, sans-serif`;
    ctx.fillText(options.ratioText, cx, cy + 16 * s);
    return { x, y, w: size, h: size };
}

function getRegionFileName() {
    const safe = (regionName || 'region').replace(/[^a-zA-Zа-яА-ЯёЁ0-9\s-]/g, '').replace(/\s+/g, '_');
    return `moigoroda_${safe}_${numVisited}_из_${numCities}.png`;
}

function canvasToBlob(canvas) {
    return new Promise((resolve, reject) => {
        canvas.toBlob((blob) => (blob ? resolve(blob) : reject(new Error('toBlob failed'))), 'image/png');
    });
}

function downloadImage(blob) {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = getRegionFileName();
    a.click();
    URL.revokeObjectURL(a.href);
}

function shareImage(blob) {
    const file = new File([blob], getRegionFileName(), { type: 'image/png' });
    if (navigator.share && navigator.canShare && navigator.canShare({ files: [file] })) {
        navigator
            .share({
                title: `Мои города — ${regionName}`,
                text: `Я посетил(а) ${numVisited} из ${numCities} городов региона ${regionName}`,
                files: [file],
            })
            .catch((err) => console.warn('Поделиться не удалось:', err));
    }
}

function browserSupportsImageShare() {
    if (!navigator.share || !navigator.canShare || typeof File === 'undefined') return false;
    try {
        const probeFile = new File(['x'], 'probe.png', { type: 'image/png' });
        return navigator.canShare({ files: [probeFile] });
    } catch (_error) {
        return false;
    }
}

function updateShareButtonState() {
    const btnShare = document.getElementById('btn-share-image');
    if (!btnShare) return { supportsImageShare: false };

    const supportsImageShare = browserSupportsImageShare();
    btnShare.disabled = !supportsImageShare;
    btnShare.classList.toggle('hidden', !supportsImageShare);

    return { supportsImageShare };
}

function setButtonsReady() {
    const btnDownload = document.getElementById('btn-download-share-image');
    if (btnDownload) btnDownload.disabled = false;
    updateShareButtonState();
}

function setLoading(loading) {
    const wrap = document.getElementById('share-image-wrapper');
    const loader = document.getElementById('share-image-loading');
    if (!wrap || !loader) return;
    wrap.classList.toggle('opacity-60', loading);
    loader.classList.toggle('hidden', !loading);
}

const polygonUrl = `${window.URL_GEO_POLYGONS}/region/hq/${country_code}/${region_code}`;
let geoJsonData = null;
const polygonController = new AbortController();
const polygonTimeoutId = setTimeout(() => polygonController.abort(), POLYGON_FETCH_TIMEOUT_MS);

fetch(polygonUrl, { signal: polygonController.signal })
    .then((response) => {
        clearTimeout(polygonTimeoutId);
        if (!response.ok) throw new Error(response.statusText);
        return response.json();
    })
    .then((geoJson) => {
        geoJsonData = geoJson;
        setLoading(true);
        renderToCanvas(geoJson).then(() => {
            setLoading(false);
            setButtonsReady();
        }).catch(() => {
            setLoading(false);
            setButtonsReady();
        });
    })
    .catch((err) => {
        clearTimeout(polygonTimeoutId);
        console.warn('Ошибка загрузки границ региона:', err);
        const canvas = document.getElementById('share-image-canvas');
        if (canvas) {
            const { width, height } = getDisplayDimensions();
            canvas.width = width;
            canvas.height = height;
            canvas.style.width = width + 'px';
            canvas.style.height = height + 'px';
            const ctx = canvas.getContext('2d');
            if (ctx) {
                ctx.fillStyle = '#f8fafc';
                ctx.fillRect(0, 0, width, height);
                ctx.fillStyle = '#64748b';
                ctx.font = '16px system-ui, sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText('Не удалось загрузить границы региона', width / 2, height / 2);
            }
        }
        setButtonsReady();
    });

const btnDownload = document.getElementById('btn-download-share-image');
const btnShare = document.getElementById('btn-share-image');

if (btnDownload) {
    btnDownload.addEventListener('click', () => {
        if (!geoJsonData) return;
        const exportSize = getExportDimensions();
        renderToCanvas(geoJsonData, exportSize).then((canvas) => {
            if (canvas) canvasToBlob(canvas).then(downloadImage).catch((e) => console.error(e));
        }).catch((e) => console.error(e));
    });
}

if (btnShare) {
    btnShare.addEventListener('click', () => {
        const { supportsImageShare } = updateShareButtonState();
        if (!supportsImageShare || !geoJsonData) return;
        const exportSize = getExportDimensions();
        renderToCanvas(geoJsonData, exportSize).then((canvas) => {
            if (canvas) canvasToBlob(canvas).then(shareImage).catch((e) => console.error(e));
        }).catch((e) => console.error(e));
    });
}

function redrawOnCaptionOptionsChange() {
    schedulePreviewRender();
}

['share-aspect-ratio', 'share-resolution', 'share-background', 'share-watermark', 'share-progress-badge-enabled', 'share-progress-badge-style', 'share-progress-badge-position', 'caption-text-preset', 'caption-position', 'caption-align', 'caption-font-size', 'caption-font-family', 'caption-font-weight', 'caption-background'].forEach((name) => {
    document.querySelectorAll(`input[name="${name}"]`).forEach((el) => {
        el.addEventListener('change', redrawOnCaptionOptionsChange);
    });
});
document.querySelectorAll('input[name="share-watermark"]').forEach((el) => {
    el.addEventListener('change', () => {
        if (!suppressPositionSourceTracking) lastPositionChangeSource = 'watermark';
    });
});
document.querySelectorAll('input[name="share-progress-badge-position"]').forEach((el) => {
    el.addEventListener('change', () => {
        if (!suppressPositionSourceTracking) lastPositionChangeSource = 'badge';
    });
});
const captionTextPresetWrap = document.getElementById('caption-text-preset-wrap');
const captionTextCustomWrap = document.getElementById('caption-text-custom-wrap');
const captionTextPresetSelect = document.getElementById('caption-text-preset');
const captionTextCustomEl = document.getElementById('caption-text-custom');
function updateCaptionTextControlsVisibility() {
    const modeEl = document.querySelector('input[name="caption-text-mode"]:checked');
    const mode = modeEl ? modeEl.value : 'preset';
    if (captionTextPresetWrap) captionTextPresetWrap.style.display = mode === 'preset' ? 'block' : 'none';
    if (captionTextCustomWrap) captionTextCustomWrap.style.display = mode === 'custom' ? 'block' : 'none';

    const disableTextControls = mode === 'none';
    const textControlSelectors = [
        'input[name="caption-position"]',
        'input[name="caption-align"]',
        '#caption-font-size',
        '#caption-font-family',
        'input[name="caption-font-weight"]',
        'input[name="caption-background"]',
        '#caption-bg-opacity',
        '#caption-bg-blur',
        '#caption-bg-color',
        '#caption-text-color',
        '#caption-bg-size',
    ];
    textControlSelectors.forEach((sel) => {
        document.querySelectorAll(sel).forEach((el) => {
            el.disabled = disableTextControls;

            const label = el.closest && el.closest('label');
            if (label) {
                label.classList.toggle('btn-disabled', disableTextControls);

                // Делаем вид "заблокированной" опции таким же, как и в блоке
                // соотношений сторон: штриховая граница и приглушенный цвет текста.
                if (disableTextControls) {
                    label.classList.add('border-dashed', 'border-layer-line/70', 'text-layer-foreground/70');
                    label.classList.remove('border-layer-line', 'text-layer-foreground');
                } else {
                    label.classList.remove('border-dashed', 'border-layer-line/70', 'text-layer-foreground/70');
                    // Возвращаем базовые цвета (если они присутствовали в исходной разметке).
                    label.classList.add('border-layer-line', 'text-layer-foreground');
                }
            }
        });
    });

    // Подписи к цветам тоже нужно приглушать — иначе они остаются "жирными"
    // даже когда соответствующие input уже disabled.
    const captionTextColorLabel = document.querySelector('label[for="caption-text-color"]');
    const captionBgColorLabel = document.querySelector('label[for="caption-bg-color"]');

    const mutedLabelClasses = ['text-layer-foreground/70', 'font-normal'];
    const resetLabelClasses = ['text-layer-foreground/70', 'font-normal'];

    [captionTextColorLabel, captionBgColorLabel].forEach((lbl) => {
        if (!lbl) return;
        if (disableTextControls) {
            lbl.classList.add(...mutedLabelClasses);
        } else {
            lbl.classList.remove(...resetLabelClasses);
        }
    });
}
document.querySelectorAll('input[name="caption-text-mode"]').forEach((el) => {
    el.addEventListener('change', () => {
        updateCaptionTextControlsVisibility();
        redrawOnCaptionOptionsChange();
    });
});
if (captionTextPresetSelect) {
    captionTextPresetSelect.addEventListener('change', redrawOnCaptionOptionsChange);
}
if (captionTextCustomEl) {
    captionTextCustomEl.addEventListener('input', redrawOnCaptionOptionsChange);
}
updateCaptionTextControlsVisibility();
const captionBgOpacityEl = document.getElementById('caption-bg-opacity');
const captionBgOpacityValue = document.getElementById('caption-bg-opacity-value');
const captionBgBlurEl = document.getElementById('caption-bg-blur');
const captionBgBlurValue = document.getElementById('caption-bg-blur-value');
if (captionBgOpacityEl) {
    captionBgOpacityEl.addEventListener('input', () => {
        if (captionBgOpacityValue) captionBgOpacityValue.textContent = captionBgOpacityEl.value;
        redrawOnCaptionOptionsChange();
    });
}
if (captionBgBlurEl) {
    captionBgBlurEl.addEventListener('input', () => {
        if (captionBgBlurValue) captionBgBlurValue.textContent = captionBgBlurEl.value;
        redrawOnCaptionOptionsChange();
    });
}
const captionBgColorEl = document.getElementById('caption-bg-color');
const captionTextColorEl = document.getElementById('caption-text-color');
if (captionBgColorEl) captionBgColorEl.addEventListener('input', redrawOnCaptionOptionsChange);
if (captionTextColorEl) captionTextColorEl.addEventListener('input', redrawOnCaptionOptionsChange);
const captionBgSizeEl = document.getElementById('caption-bg-size');
const captionBgSizeValue = document.getElementById('caption-bg-size-value');
if (captionBgSizeEl) {
    captionBgSizeEl.addEventListener('input', () => {
        if (captionBgSizeValue) captionBgSizeValue.textContent = (parseInt(captionBgSizeEl.value, 10) / 100).toString();
        redrawOnCaptionOptionsChange();
    });
}

const captionFontSizeEl = document.getElementById('caption-font-size');
const captionFontSizeValue = document.getElementById('caption-font-size-value');
if (captionFontSizeEl) {
    captionFontSizeEl.addEventListener('input', () => {
        if (captionFontSizeValue) captionFontSizeValue.textContent = captionFontSizeEl.value;
        redrawOnCaptionOptionsChange();
    });
}

const captionFontFamilyEl = document.getElementById('caption-font-family');
if (captionFontFamilyEl) {
    captionFontFamilyEl.addEventListener('change', redrawOnCaptionOptionsChange);
}

const shareBackgroundColorEl = document.getElementById('share-background-color');
function updateShareBackgroundColorState() {
    if (!shareBackgroundColorEl) return;
    const bg = getBackgroundOption();
    shareBackgroundColorEl.disabled = bg !== 'none';
}
document.querySelectorAll('input[name="share-background"]').forEach((el) => {
    el.addEventListener('change', () => {
        updateShareBackgroundColorState();
        redrawOnCaptionOptionsChange();
    });
});
if (shareBackgroundColorEl) {
    shareBackgroundColorEl.addEventListener('input', redrawOnCaptionOptionsChange);
}
updateShareBackgroundColorState();

// При изменении ширины контейнера обновляем отображаемый размер canvas (сохраняя соотношение сторон)
(function () {
    const container = document.getElementById('share-image-container');
    const canvas = document.getElementById('share-image-canvas');
    if (!container || !canvas) return;
    const ro = new ResizeObserver(() => {
        const display = getDisplayDimensions();
        canvas.style.width = display.width + 'px';
        canvas.style.height = display.height + 'px';
    });
    ro.observe(container);
})();
