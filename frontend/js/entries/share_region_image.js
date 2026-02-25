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

/** Размеры для отображения на странице (без учёта разрешения — визуально не меняется). */
function getDisplayDimensions() {
    const aspectEl = document.querySelector('input[name="share-aspect-ratio"]:checked');
    const aspectKey = (aspectEl && aspectEl.value && ASPECT_PRESETS[aspectEl.value]) ? aspectEl.value : DEFAULT_ASPECT;
    return ASPECT_PRESETS[aspectKey];
}

/** Размеры для экспорта (скачать / поделиться) — с учётом выбранного разрешения. */
function getExportDimensions() {
    const base = getDisplayDimensions();
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

/** Размер маркера-пина на холсте (якорь внизу по центру). */
const PIN_WIDTH = 16;
const PIN_HEIGHT = 22;
const PIN_ANCHOR_X = 8;
const PIN_ANCHOR_Y = 22;

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
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.crossOrigin = 'anonymous';
        img.onload = () => resolve(img);
        img.onerror = () => reject(new Error(`Tile load failed: ${url}`));
        img.src = url;
    });
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

    const promises = [];
    const tiles = [];
    for (let ty = minTileY; ty < maxTileY; ty++) {
        for (let tx = minTileX; tx < maxTileX; tx++) {
            const url = urlTemplate.replace('{x}', String(tx)).replace('{y}', String(ty));
            promises.push(loadTile(url).then((img) => ({ img, tx, ty })));
        }
    }
    const results = await Promise.all(promises.map((p) => p.catch(() => null)));
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
    const canvas = forExport
        ? document.createElement('canvas')
        : document.getElementById('share-image-canvas');
    if (!canvas) return null;
    const ctx = canvas.getContext('2d');
    if (!ctx) return null;

    const { width: w, height: h } = forExport ? exportDimensions : getExportDimensions();
    canvas.width = w;
    canvas.height = h;
    if (!forExport) {
        const display = getDisplayDimensions();
        canvas.style.width = display.width + 'px';
        canvas.style.height = display.height + 'px';
    }

    const mapWidth = w;
    const mapHeight = h;
    const pad = 0;

    const polygonCoords = collectCoordsFromGeoJSON(geoJson);
    const bbox = computeBbox(polygonCoords, all_cities);
    const background = getBackgroundOption();
    const mercatorState = computeMercatorView(bbox, mapWidth, mapHeight, pad);

    ctx.fillStyle = '#f8fafc';
    ctx.fillRect(0, 0, w, h);

    if (background === 'osm') {
        try {
            await drawOsmTiles(ctx, bbox, mercatorState);
        } catch (e) {
            console.warn('Не удалось загрузить тайлы карты:', e);
        }
    }

    const markerScale = Math.max(w, h) / BASE_LONG_SIDE;
    const pinW = PIN_WIDTH * markerScale;
    const pinH = PIN_HEIGHT * markerScale;
    const pinAnchorX = PIN_ANCHOR_X * markerScale;
    const pinAnchorY = PIN_ANCHOR_Y * markerScale;
    drawGeoJSONMercator(ctx, geoJson, mercatorState, markerScale);
    await ensurePinImages();
    for (let i = 0; i < all_cities.length; i++) {
        const c = all_cities[i];
        const p = mercatorToCanvas(c.lon, c.lat, mercatorState.zoom, mercatorState.scaleX, mercatorState.scaleY, mercatorState.offsetX, mercatorState.offsetY);
        const pinImg = c.isVisited ? pinVisitedImg : pinNotVisitedImg;
        if (pinImg && pinImg.complete && pinImg.naturalWidth) {
            ctx.drawImage(pinImg, p.x - pinAnchorX, p.y - pinAnchorY, pinW, pinH);
        }
    }

    const caption = `Поздравляем! Вы посетили ${numVisited} из ${numCities} городов региона ${regionName}`;
    const captionOptions = getCaptionOptions();
    drawCaption(ctx, caption, captionOptions, w, h, markerScale);

    return canvas;
}

function hexToRgb(hex) {
    const m = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return m ? { r: parseInt(m[1], 16), g: parseInt(m[2], 16), b: parseInt(m[3], 16) } : { r: 255, g: 255, b: 255 };
}

function getCaptionOptions() {
    const positionEl = document.querySelector('input[name="caption-position"]:checked');
    const alignEl = document.querySelector('input[name="caption-align"]:checked');
    const sizeEl = document.querySelector('input[name="caption-font-size"]:checked');
    const familyEl = document.querySelector('input[name="caption-font-family"]:checked');
    const weightEl = document.querySelector('input[name="caption-font-weight"]:checked');
    const bgEl = document.querySelector('input[name="caption-background"]:checked');
    const bgColorEl = document.getElementById('caption-bg-color');
    const bgSizeEl = document.getElementById('caption-bg-size');
    const bgOpacityEl = document.getElementById('caption-bg-opacity');
    const bgBlurEl = document.getElementById('caption-bg-blur');
    const bgColor = (bgColorEl && bgColorEl.value) ? bgColorEl.value : '#ef4444';
    const bgSizeRaw = bgSizeEl && bgSizeEl.value !== undefined ? parseInt(bgSizeEl.value, 10) : 100;
    const bgSize = Math.max(50, Math.min(300, bgSizeRaw)) / 100;
    const bgOpacity = bgOpacityEl && bgOpacityEl.value !== undefined ? parseInt(bgOpacityEl.value, 10) : 50;
    const bgBlur = bgBlurEl && bgBlurEl.value !== undefined ? parseInt(bgBlurEl.value, 10) : 10;
    return {
        position: (positionEl && positionEl.value) || 'bottom',
        alignment: (alignEl && alignEl.value) || 'center',
        fontSize: sizeEl ? parseInt(sizeEl.value, 10) : 20,
        fontFamily: (familyEl && familyEl.value) || 'sans',
        fontWeight: (weightEl && weightEl.value) || 'bold',
        background: (bgEl && bgEl.value) || 'box',
        bgColor,
        bgSize,
        // bgOpacitySlider: 0% = нет прозрачности (полностью видно), 100% = полностью прозрачно
        bgOpacity: 1 - Math.max(0, Math.min(100, bgOpacity)) / 100,
        bgBlur: Math.max(0, Math.min(20, bgBlur)),
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
        const boxW = Math.min(0.85 * canvasWidth, 620 * scale);
        const boxH = capHeight + 16 * scale;
        return { x: (canvasWidth - boxW) / 2, y: (canvasHeight - boxH) / 2, w: boxW, h: boxH };
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
    sans: 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif',
    serif: 'Georgia, "Times New Roman", serif',
    mono: '"ui-monospace", "Cascadia Code", "Source Code Pro", monospace',
};

function drawCaption(ctx, caption, options, canvasWidth, canvasHeight, scale) {
    const { position, alignment, fontSize, fontFamily, fontWeight, background, bgColor, bgSize, bgOpacity, bgBlur } = options;
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

    // Базовый бокс: либо якорный (для old full box), либо «по тексту»
    let boxX = anchorBox.x;
    let boxY = anchorBox.y;
    let boxW = anchorBox.w;
    let boxH = anchorBox.h;

    const boxBg = background || 'box';
    if (boxBg === 'box') {
        const desiredW = Math.min(anchorBox.w, actualMaxLineWidth + 2 * padBox);
        const desiredH = textBlockHeight + 2 * padBox;
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
    }

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

    ctx.fillStyle = '#1f2937';
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

function setButtonsReady() {
    const btnDownload = document.getElementById('btn-download-share-image');
    const btnShare = document.getElementById('btn-share-image');
    if (btnDownload) btnDownload.disabled = false;
    if (btnShare && navigator.share && navigator.canShare) {
        btnShare.disabled = false;
        btnShare.classList.remove('disabled:opacity-50');
        btnShare.classList.add('border-blue-500', 'text-blue-600', 'hover:bg-blue-50');
        btnShare.classList.remove('border-gray-300', 'text-gray-700');
    }
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

fetch(polygonUrl)
    .then((response) => {
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
    if (navigator.share && navigator.canShare) {
        btnShare.addEventListener('click', () => {
            if (!geoJsonData) return;
            const exportSize = getExportDimensions();
            renderToCanvas(geoJsonData, exportSize).then((canvas) => {
                if (canvas) canvasToBlob(canvas).then(shareImage).catch((e) => console.error(e));
            }).catch((e) => console.error(e));
        });
    }
}

function redrawOnCaptionOptionsChange() {
    if (!geoJsonData) return;
    renderToCanvas(geoJsonData).catch((e) => console.warn(e));
}

['share-aspect-ratio', 'share-resolution', 'share-background', 'caption-position', 'caption-align', 'caption-font-size', 'caption-font-family', 'caption-font-weight', 'caption-background'].forEach((name) => {
    document.querySelectorAll(`input[name="${name}"]`).forEach((el) => {
        el.addEventListener('change', redrawOnCaptionOptionsChange);
    });
});
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
if (captionBgColorEl) captionBgColorEl.addEventListener('input', redrawOnCaptionOptionsChange);
const captionBgSizeEl = document.getElementById('caption-bg-size');
const captionBgSizeValue = document.getElementById('caption-bg-size-value');
if (captionBgSizeEl) {
    captionBgSizeEl.addEventListener('input', () => {
        if (captionBgSizeValue) captionBgSizeValue.textContent = (parseInt(captionBgSizeEl.value, 10) / 100).toString();
        redrawOnCaptionOptionsChange();
    });
}
