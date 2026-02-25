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

const CANVAS_WIDTH = 800;
const CANVAS_HEIGHT = 520;
const PADDING = 48;
const CAPTION_HEIGHT = 56;
const CAPTION_PADDING = 12;

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
 * Используется и с подложкой OSM, и без неё — чтобы масштаб полигона совпадал.
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
    const scale = Math.min(availableW / bboxW, availableH / bboxH);
    const offsetX = mapWidth / 2 - (minPx.x + bboxW / 2) * scale;
    const offsetY = mapHeight / 2 - (minPx.y + bboxH / 2) * scale;
    return { scale, offsetX, offsetY, zoom };
}

/**
 * Рисует подложку из тайлов OpenStreetMap. Вид (scale, offset, zoom) задаётся mercatorState.
 */
async function drawOsmTiles(ctx, bbox, mercatorState) {
    const { scale, offsetX, offsetY, zoom } = mercatorState;
    const [minLon, minLat, maxLon, maxLat] = bbox;
    const minPx = lonLatToMercatorPixel(minLon, maxLat, zoom);
    const maxPx = lonLatToMercatorPixel(maxLon, minLat, zoom);

    const minTileX = Math.floor(minPx.x / TILE_SIZE);
    const maxTileX = Math.ceil(maxPx.x / TILE_SIZE);
    const minTileY = Math.floor(minPx.y / TILE_SIZE);
    const maxTileY = Math.ceil(maxPx.y / TILE_SIZE);

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

    for (let i = 0; i < tiles.length; i++) {
        const { img, tx, ty } = tiles[i];
        const dx = offsetX + tx * TILE_SIZE * scale;
        const dy = offsetY + ty * TILE_SIZE * scale;
        ctx.drawImage(img, dx, dy, TILE_SIZE * scale, TILE_SIZE * scale);
    }
}

function mercatorToCanvas(lon, lat, zoom, scale, offsetX, offsetY) {
    const p = lonLatToMercatorPixel(lon, lat, zoom);
    return { x: offsetX + p.x * scale, y: offsetY + p.y * scale };
}

function drawGeoJSONMercator(ctx, geoJson, mercatorState) {
    const { scale, offsetX, offsetY, zoom } = mercatorState;

    function drawRing(coordRing, close) {
        if (coordRing.length < 2) return;
        const first = mercatorToCanvas(coordRing[0][0], coordRing[0][1], zoom, scale, offsetX, offsetY);
        ctx.moveTo(first.x, first.y);
        for (let i = 1; i < coordRing.length; i++) {
            const p = mercatorToCanvas(coordRing[i][0], coordRing[i][1], zoom, scale, offsetX, offsetY);
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
        ctx.lineWidth = STROKE_WIDTH;
        ctx.stroke();
    }
}

async function renderToCanvas(geoJson) {
    const canvas = document.getElementById('share-image-canvas');
    if (!canvas) return null;
    const ctx = canvas.getContext('2d');
    if (!ctx) return null;

    const mapWidth = CANVAS_WIDTH;
    const mapHeight = CANVAS_HEIGHT;
    const pad = 0;

    const polygonCoords = collectCoordsFromGeoJSON(geoJson);
    const bbox = computeBbox(polygonCoords, all_cities);
    const background = getBackgroundOption();
    const mercatorState = computeMercatorView(bbox, mapWidth, mapHeight, pad);

    ctx.fillStyle = '#f8fafc';
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

    if (background === 'osm') {
        try {
            await drawOsmTiles(ctx, bbox, mercatorState);
        } catch (e) {
            console.warn('Не удалось загрузить тайлы карты:', e);
        }
    }

    drawGeoJSONMercator(ctx, geoJson, mercatorState);
    await ensurePinImages();
    for (let i = 0; i < all_cities.length; i++) {
        const c = all_cities[i];
        const p = mercatorToCanvas(c.lon, c.lat, mercatorState.zoom, mercatorState.scale, mercatorState.offsetX, mercatorState.offsetY);
        const pinImg = c.isVisited ? pinVisitedImg : pinNotVisitedImg;
        if (pinImg && pinImg.complete && pinImg.naturalWidth) {
            ctx.drawImage(pinImg, p.x - PIN_ANCHOR_X, p.y - PIN_ANCHOR_Y, PIN_WIDTH, PIN_HEIGHT);
        }
    }

    const caption = `Поздравляем! Вы посетили ${numVisited} из ${numCities} городов региона ${regionName}`;
    const captionOptions = getCaptionOptions();
    drawCaption(ctx, caption, captionOptions);

    return canvas;
}

function getCaptionOptions() {
    const positionEl = document.querySelector('input[name="caption-position"]:checked');
    const alignEl = document.querySelector('input[name="caption-align"]:checked');
    const sizeEl = document.querySelector('input[name="caption-font-size"]:checked');
    const familyEl = document.querySelector('input[name="caption-font-family"]:checked');
    const weightEl = document.querySelector('input[name="caption-font-weight"]:checked');
    return {
        position: (positionEl && positionEl.value) || 'bottom',
        alignment: (alignEl && alignEl.value) || 'center',
        fontSize: sizeEl ? parseInt(sizeEl.value, 10) : 20,
        fontFamily: (familyEl && familyEl.value) || 'sans',
        fontWeight: (weightEl && weightEl.value) || 'bold',
    };
}

/**
 * Возвращает прямоугольник блока подписи в зависимости от положения.
 */
function getCaptionBox(position) {
    const pad = CAPTION_PADDING;
    if (position === 'top') {
        return { x: pad, y: pad, w: CANVAS_WIDTH - 2 * pad, h: CAPTION_HEIGHT };
    }
    if (position === 'bottom') {
        return { x: pad, y: CANVAS_HEIGHT - pad - CAPTION_HEIGHT, w: CANVAS_WIDTH - 2 * pad, h: CAPTION_HEIGHT };
    }
    if (position === 'center') {
        const w = Math.min(0.85 * CANVAS_WIDTH, 620);
        const h = CAPTION_HEIGHT + 16;
        return { x: (CANVAS_WIDTH - w) / 2, y: (CANVAS_HEIGHT - h) / 2, w, h };
    }
    return { x: pad, y: CANVAS_HEIGHT - pad - CAPTION_HEIGHT, w: CANVAS_WIDTH - 2 * pad, h: CAPTION_HEIGHT };
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

function drawCaption(ctx, caption, options) {
    const { position, alignment, fontSize, fontFamily, fontWeight } = options;
    const box = getCaptionBox(position);
    const { x: boxX, y: boxY, w: boxW, h: boxH } = box;
    const maxTextWidth = boxW - 2 * CAPTION_PADDING;
    const lineHeight = Math.round(fontSize * 1.15);

    ctx.font = `${fontWeight} ${fontSize}px ${FONT_FAMILIES[fontFamily] || FONT_FAMILIES.sans}`;
    const lines = measureWrappedLines(ctx, caption, maxTextWidth);
    const textBlockHeight = lines.length * lineHeight;
    const startY = boxY + (boxH - textBlockHeight) / 2 + lineHeight / 2;

    ctx.fillStyle = 'rgba(255,255,255,0.96)';
    ctx.strokeStyle = 'rgba(0,0,0,0.06)';
    ctx.lineWidth = 1;
    roundRect(ctx, boxX, boxY, boxW, boxH, 10);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = '#1f2937';
    ctx.textBaseline = 'middle';
    if (alignment === 'left') {
        ctx.textAlign = 'left';
        const textX = boxX + CAPTION_PADDING;
        for (let i = 0; i < lines.length; i++) {
            ctx.fillText(lines[i], textX, startY + i * lineHeight);
        }
    } else if (alignment === 'right') {
        ctx.textAlign = 'right';
        const textX = boxX + boxW - CAPTION_PADDING;
        for (let i = 0; i < lines.length; i++) {
            ctx.fillText(lines[i], textX, startY + i * lineHeight);
        }
    } else {
        ctx.textAlign = 'center';
        const textX = boxX + boxW / 2;
        for (let i = 0; i < lines.length; i++) {
            ctx.fillText(lines[i], textX, startY + i * lineHeight);
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
            const ctx = canvas.getContext('2d');
            if (ctx) {
                ctx.fillStyle = '#f8fafc';
                ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
                ctx.fillStyle = '#64748b';
                ctx.font = '16px system-ui, sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText('Не удалось загрузить границы региона', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2);
            }
        }
        setButtonsReady();
    });

const btnDownload = document.getElementById('btn-download-share-image');
const btnShare = document.getElementById('btn-share-image');

if (btnDownload) {
    btnDownload.addEventListener('click', () => {
        if (!geoJsonData) return;
        renderToCanvas(geoJsonData).then((canvas) => {
            if (canvas) canvasToBlob(canvas).then(downloadImage).catch((e) => console.error(e));
        }).catch((e) => console.error(e));
    });
}

if (btnShare) {
    if (navigator.share && navigator.canShare) {
        btnShare.addEventListener('click', () => {
            if (!geoJsonData) return;
            renderToCanvas(geoJsonData).then((canvas) => {
                if (canvas) canvasToBlob(canvas).then(shareImage).catch((e) => console.error(e));
            }).catch((e) => console.error(e));
        });
    }
}

function redrawOnCaptionOptionsChange() {
    if (!geoJsonData) return;
    renderToCanvas(geoJsonData).catch((e) => console.warn(e));
}

['share-background', 'caption-position', 'caption-align', 'caption-font-size', 'caption-font-family', 'caption-font-weight'].forEach((name) => {
    document.querySelectorAll(`input[name="${name}"]`).forEach((el) => {
        el.addEventListener('change', redrawOnCaptionOptionsChange);
    });
});
