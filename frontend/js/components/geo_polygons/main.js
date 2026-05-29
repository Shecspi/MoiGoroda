import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import './style.css'
import { showDangerToast } from '../toast.js'

export function initOSMViewer(containerId, sidebarId) {
    const map = L.map(containerId, {
        zoomControl: false,
        attributionControl: false
    }).setView([55.7558, 37.6173], 13)

    L.control.zoom({
        zoomInTitle: 'Приблизить карту',
        zoomOutTitle: 'Отдалить карту',
    }).addTo(map)

    const locationPinSvg = (color) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512" width="21" height="28" style="filter: drop-shadow(0 0 2px rgba(0, 0, 0, 0.5));">
        <path fill="${color}" stroke="rgba(0, 0, 0, 0.3)" stroke-width="1.5" stroke-linejoin="round" d="M215.7 499.2C267 435 384 279.4 384 192C384 86 298 0 192 0S0 86 0 192c0 87.4 117 243 168.3 307.2c12.3 15.3 35.1 15.3 47.4 0zM192 128a64 64 0 1 1 0 128 64 64 0 1 1 0-128z"/>
    </svg>`

    const icon_click_pin = L.divIcon({
        className: 'custom-click-pin',
        html: locationPinSvg('rgb(220, 38, 38)'),
        iconSize: [21, 28],
        iconAnchor: [10.5, 28],
        popupAnchor: [0, -28]
    })

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: 'Используются карты <a href="http://www.openstreetmap.org/copyright" target="_blank">© OpenStreetMap</a> под лицензией <a href="https://opendatacommons.org/licenses/odbl/" target="_blank">ODbL</a>.'
    }).addTo(map)

    L.control.attribution({position: 'bottomright', prefix: false}).addTo(map)

    let currentObjects = []
    let selectedObject = null
    let geojsonLayer = null
    let clickMarker = null
    let isSelectionLoading = false
    let lastClickLat = null
    let lastClickLng = null

    const adminLevelIcons = {
        country: '🌍', state: '🗺️', region: '🗺️', county: '📍',
        city: '🏙️', town: '🏘️', village: '🏡', suburb: '🏘️',
        neighbourhood: '📍', district: '📌', municipality: '🏛️', postcode: '📮',
        island: '🏝️', islet: '🏝️', locality: '📍', quarter: '🏘️',
    }

    const adminLevelMap = {
        '2': 'country', '3': 'region', '4': 'state', '5': 'region',
        '6': 'county', '7': 'district', '8': 'city', '9': 'suburb', '10': 'village',
    }

    /** Иконки по значению OSM-тега (boundary, landuse, natural и т.д.) */
    const osmValueIcons = {
        // boundary
        protected_area: '🛡️', national_park: '🏞️', postal_code: '📮',
        forest: '🌲', forest_compartment: '🌲', place: '📌', timezone: '🕐',
        census: '📊', aboriginal_lands: '🪶', maritime: '⚓',
        // landuse
        residential: '🏘️', industrial: '🏭', commercial: '🏬', retail: '🛍️',
        farmland: '🌾', meadow: '🌾', grass: '🌿', orchard: '🍎', vineyard: '🍇',
        military: '🪖', quarry: '⛏️', basin: '💧', recreation_ground: '⚽',
        cemetery: '⚰️', allotments: '🌱', construction: '🚧',
        // natural
        water: '💧', wood: '🌲', wetland: '🦆', grassland: '🌿', heath: '🌿',
        scrub: '🌿', bare_rock: '🪨', beach: '🏖️', glacier: '🏔️', peak: '⛰️',
        bay: '🌊', strait: '🌊', spring: '💧',
        // leisure
        park: '🌳', garden: '🌸', nature_reserve: '🦌', playground: '🛝',
        sports_centre: '🏟️', pitch: '⚽', golf_course: '⛳', stadium: '🏟️',
        // water / waterway
        lake: '🏞️', pond: '💧', river: '🌊', reservoir: '💧', canal: '🚣',
        stream: '🌊', ditch: '〰️',
        // tourism / historic / amenity
        theme_park: '🎢', attraction: '🎡', museum: '🏛️', zoo: '🦁',
        ruins: '🏚️', castle: '🏰', monument: '🗿',
        school: '🏫', university: '🎓', hospital: '🏥', place_of_worship: '⛪',
        // building / man_made / aeroway
        yes: '🏢', tower: '🗼', bridge: '🌉', dam: '🧱',
        aerodrome: '✈️', helipad: '🚁',
    }

    /** Иконка по ключу тега, если значение не найдено в osmValueIcons */
    const osmTagKeyIcons = {
        boundary: '🏷️', landuse: '🗺️', natural: '🌿', leisure: '🎯',
        water: '💧', waterway: '🌊', tourism: '📸', historic: '🏛️',
        amenity: '📍', building: '🏢', military: '🪖', man_made: '🏗️',
        aeroway: '✈️', zone: '🔲', geocode: '📊',
    }

    const placeTypeMap = {
        city: 'city', town: 'town', village: 'village', hamlet: 'village',
        suburb: 'suburb', neighbourhood: 'neighbourhood', island: 'island',
        islet: 'islet', locality: 'locality', quarter: 'quarter',
    }

    /**
     * Определяет тип объекта и исходный OSM-тег для иконки и подписи.
     * @returns {{ adminType: string, categoryKey: string|null, categoryValue: string|null }}
     */
    function resolveAreaType(tags) {
        const adminLevel = tags.admin_level ? String(tags.admin_level) : null
        if (adminLevel && adminLevelMap[adminLevel]) {
            return { adminType: adminLevelMap[adminLevel], categoryKey: 'admin_level', categoryValue: adminLevel }
        }

        const place = tags.place
        if (place && placeTypeMap[place]) {
            return { adminType: placeTypeMap[place], categoryKey: 'place', categoryValue: place }
        }

        if (tags.boundary === 'administrative') {
            return { adminType: 'district', categoryKey: 'boundary', categoryValue: 'administrative' }
        }

        const tagPriority = [
            'boundary', 'landuse', 'natural', 'leisure', 'water', 'waterway',
            'tourism', 'historic', 'amenity', 'building', 'military', 'man_made', 'aeroway', 'zone',
        ]
        for (const key of tagPriority) {
            const value = tags[key]
            if (value) {
                return { adminType: value, categoryKey: key, categoryValue: value }
            }
        }

        return { adminType: 'other', categoryKey: null, categoryValue: null }
    }

    function getIcon(obj) {
        const type = obj._adminType
        if (type && type !== 'other') {
            const icon = adminLevelIcons[type] || osmValueIcons[type]
            if (icon) return icon
        }
        if (obj._categoryKey && obj._categoryValue) {
            const icon = osmValueIcons[obj._categoryValue] || osmTagKeyIcons[obj._categoryKey]
            if (icon) return icon
        }
        return '📍'
    }

    function getElementName(element) {
        const tags = element.tags || {}
        return tags.name || tags['name:en'] || tags['name:ru'] || tags.ref || `${element.type} (${element.id})`
    }

    function getElementDetails(element) {
        const parts = []
        if (element._adminLevel && element._adminLevel !== 'unknown') {
            parts.push(`admin_level: ${element._adminLevel}`)
        }
        if (element._relationId != null) {
            parts.push(`relation_id: ${element._relationId}`)
        }
        return parts.join(' · ')
    }

    const OVERPASS_ENDPOINTS = [
        'https://overpass-api.de/api/interpreter',
        'https://overpass.kumi.systems/api/interpreter',
        'https://overpass.openstreetmap.ru/api/interpreter',
    ]

    async function queryOverpassIsIn(lat, lon) {
        const query = `[out:json][timeout:15];is_in(${lat},${lon})->.a;area.a;out body;`
        const body = `data=${encodeURIComponent(query)}`
        for (const endpoint of OVERPASS_ENDPOINTS) {
            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body,
                })
                if (!response.ok) {
                    const text = await response.text()
                    if (text.includes('runtime error') || text.includes('too busy')) continue
                    throw new Error('Overpass is_in error')
                }
                const data = await response.json()
                return data.elements
            } catch (e) {
                if (e.message === 'Overpass is_in error') throw e
                continue
            }
        }
        throw new Error('Все серверы Overpass заняты')
    }

    async function fetchPolygonFromServer(relationId) {
        const response = await fetch(`/api/geo-polygons/polygon/${relationId}/`)
        if (!response.ok) return null
        return response.json()
    }

    function normalizeGeometry(geometry) {
        if (!geometry) return null
        if (geometry.type === 'Point' || geometry.type === 'Polygon' || geometry.type === 'MultiPolygon') return geometry
        if (geometry.type === 'LineString') {
            const coords = geometry.coordinates
            if (coords.length > 2) {
                const first = coords[0], last = coords[coords.length - 1]
                if (first[0] !== last[0] || first[1] !== last[1]) coords.push([first[0], first[1]])
            }
            return { type: 'Polygon', coordinates: [coords] }
        }
        if (geometry.type === 'MultiLineString') {
            const polygons = geometry.coordinates.map(line => {
                if (line.length > 2) {
                    const first = line[0], last = line[line.length - 1]
                    if (first[0] !== last[0] || first[1] !== last[1]) line.push([first[0], first[1]])
                }
                return line
            })
            return { type: 'MultiPolygon', coordinates: polygons.map(p => [p]) }
        }
        return geometry
    }

    function displayObjects(adminBoundaries) {
        const list = document.getElementById('object-list')
        if (!list) return
        list.innerHTML = ''
        if (adminBoundaries.length === 0) {
            list.innerHTML = '<div class="status-message">Границы не найдены</div>'
            return
        }
        currentObjects = []
        adminBoundaries.forEach(admin => currentObjects.push(admin))
        currentObjects.forEach((obj, index) => {
            const item = document.createElement('div')
            item.className = 'list-item'
            item.dataset.index = index
            const icon = getIcon(obj)
            const name = getElementName(obj)
            const details = getElementDetails(obj)
            item.innerHTML = `<div class="item-name">${icon} ${name}</div><div class="item-details">${details}</div>`
            item.addEventListener('click', () => selectObject(index))
            list.appendChild(item)
        })
    }

    async function selectObject(index) {
        if (isSelectionLoading) return
        if (!window.OSM_VIEWER_IS_AUTHENTICATED) {
            showAuthToast()
            return
        }
        const obj = currentObjects[index]
        if (!obj) return
        selectedObject = obj
        document.querySelectorAll('.list-item').forEach(item => {
            item.classList.toggle('selected', parseInt(item.dataset.index) === index)
        })
        if (geojsonLayer) { map.removeLayer(geojsonLayer); geojsonLayer = null }
        if (obj._geojson) {
            geojsonLayer = L.geoJSON(obj._geojson, {
                style: { color: '#7c5cff', weight: 3, fillOpacity: 0.15, fillColor: '#7c5cff' }
            }).addTo(map)
            geojsonLayer.bindPopup(getElementName(obj))
            map.fitBounds(geojsonLayer.getBounds().pad(0.1))
            updateDownloadButton()
        } else if (obj._relationId) {
            isSelectionLoading = true
            const btn = document.getElementById('download-btn')
            btn.textContent = 'Загрузка...'
            btn.disabled = true
            try {
                const geojson = await fetchPolygonFromServer(obj._relationId)
                if (geojson && geojson.geometry) {
                    obj._geojson = geojson
                    geojsonLayer = L.geoJSON(geojson, {
                        style: { color: '#7c5cff', weight: 3, fillOpacity: 0.15, fillColor: '#7c5cff' }
                    }).addTo(map)
                    geojsonLayer.bindPopup(getElementName(obj))
                    map.fitBounds(geojsonLayer.getBounds().pad(0.1))
                    updateDownloadButton()
                } else {
                    btn.textContent = 'Нет полигона'
                    btn.disabled = true
                }
            } catch (e) {
                console.error('Error loading boundary:', e)
                btn.textContent = 'Ошибка'
                btn.disabled = true
            } finally {
                isSelectionLoading = false
            }
        }
    }

    function updateDownloadButton() {
        const btn = document.getElementById('download-btn')
        if (window.OSM_VIEWER_HAS_ADVANCED_PREMIUM) {
            btn.textContent = 'Скачать GeoJSON'
            btn.disabled = false
        } else {
            btn.textContent = 'Нужен Premium'
            btn.disabled = true
        }
    }

    function showAuthToast() {
        showDangerToast('Требуется авторизация', 'Для просмотра объектов необходимо <a href="/account/login/" class="font-semibold underline">войти</a> или <a href="/account/signup/" class="font-semibold underline">зарегистрироваться</a>.')
    }

    function showPremiumToast() {
        showDangerToast('Требуется Premium', 'Для скачивания GeoJSON необходима <a href="/premium/plans/" class="font-semibold underline">расширенная подписка</a>.')
    }

    function downloadGeoJSON() {
        if (!window.OSM_VIEWER_HAS_ADVANCED_PREMIUM) {
            showPremiumToast()
            return
        }
        if (!selectedObject || !selectedObject._geojson) return
        const data = JSON.stringify(selectedObject._geojson, null, 2)
        const blob = new Blob([data], { type: 'application/json' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        const name = getElementName(selectedObject).replace(/[<>:"/\\|?*\x00-\x1f]/g, '_').trim() || 'osm_object'
        a.href = url
        a.download = `${name}.geojson`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
    }

    function setCopyButtonVisible(visible) {
        const copyBtn = document.getElementById('copy-btn')
        copyBtn.classList.toggle('is-hidden', !visible)
        copyBtn.setAttribute('aria-hidden', visible ? 'false' : 'true')
        copyBtn.tabIndex = visible ? 0 : -1
    }

    function setupInitialUI() {
        document.getElementById('sidebar-title').textContent = 'Объекты OSM'
        document.getElementById('coords').textContent = 'Кликните на карту для поиска'
        setCopyButtonVisible(false)
        document.getElementById('object-list').innerHTML = '<div class="status-message">Кликните на карту для поиска</div>'
        const btn = document.getElementById('download-btn')
        if (window.OSM_VIEWER_HAS_ADVANCED_PREMIUM) {
            btn.textContent = 'Скачать GeoJSON'
        } else {
            btn.textContent = 'Нужен Premium'
        }
        btn.disabled = true
    }

    map.on('click', async (e) => {
        const { lat, lng } = e.latlng
        lastClickLat = lat
        lastClickLng = lng
        if (clickMarker) { map.removeLayer(clickMarker); clickMarker = null }
        clickMarker = L.marker([lat, lng], { icon: icon_click_pin, zIndexOffset: 1000 }).addTo(map)
        document.getElementById('coords').textContent = `Lat: ${lat.toFixed(6)} · Lon: ${lng.toFixed(6)}`
        setCopyButtonVisible(true)
        const list = document.getElementById('object-list')
        list.innerHTML = '<div class="loading"></div>'
        if (geojsonLayer) { map.removeLayer(geojsonLayer); geojsonLayer = null }
        selectedObject = null
        document.getElementById('download-btn').disabled = true
        if (window.OSM_VIEWER_HAS_ADVANCED_PREMIUM) {
            document.getElementById('download-btn').textContent = 'Скачать GeoJSON'
        } else {
            document.getElementById('download-btn').textContent = 'Нужен Premium'
        }
        try {
            const isInResult = await queryOverpassIsIn(lat, lng)
            let adminBoundaries = []
            const seen = new Set()
            if (isInResult) {
                isInResult.forEach((area, idx) => {
                    if (area.tags && area.id > 3600000000) {
                        const name = area.tags.name || area.tags['name:en'] || area.tags['name:ru'] || area.tags.ref
                        if (!name) return
                        const adminLevel = area.tags.admin_level ? String(area.tags.admin_level) : null
                        const { adminType, categoryKey, categoryValue } = resolveAreaType(area.tags)
                        const uniqueKey = area.id
                        if (!seen.has(uniqueKey)) {
                            seen.add(uniqueKey)
                            adminBoundaries.push({
                                _adminType: adminType,
                                _adminLevel: adminLevel || 'unknown',
                                _categoryKey: categoryKey,
                                _categoryValue: categoryValue,
                                _relationId: area.id - 3600000000,
                                _originalIndex: idx,
                                id: `area-${area.id}`,
                                type: 'admin',
                                tags: { name, type: adminType, admin_level: adminLevel || 'unknown' }
                            })
                        }
                    }
                })
            }
            adminBoundaries.sort((a, b) => b._originalIndex - a._originalIndex)
            adminBoundaries.forEach(o => delete o._originalIndex)
            displayObjects(adminBoundaries)
        } catch (error) {
            list.innerHTML = '<div class="status-message error">Ошибка загрузки данных</div>'
        }
    })

    document.getElementById('download-btn').addEventListener('click', downloadGeoJSON)

    setupInitialUI()

    const copyBtn = document.getElementById('copy-btn')
    copyBtn.addEventListener('click', async () => {
        if (lastClickLat === null) return
        const text = `${lastClickLat.toFixed(6)}, ${lastClickLng.toFixed(6)}`
        try {
            await navigator.clipboard.writeText(text)
            copyBtn.classList.remove('btn-ghost')
            copyBtn.classList.add('btn-ghost-success')
            setTimeout(() => {
                copyBtn.classList.remove('btn-ghost-success')
                copyBtn.classList.add('btn-ghost')
            }, 1500)
        } catch {
            const input = document.createElement('input')
            input.value = text
            document.body.appendChild(input)
            input.select()
            document.execCommand('copy')
            document.body.removeChild(input)
            copyBtn.classList.remove('btn-ghost')
            copyBtn.classList.add('btn-ghost-success')
            setTimeout(() => {
                copyBtn.classList.remove('btn-ghost-success')
                copyBtn.classList.add('btn-ghost')
            }, 1500)
        }
    })

    return map
}
