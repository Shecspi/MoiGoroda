/**
 * Реализует объекты иконок разного цвета для использования их в маркерах
 *
 * ----------------------------------------------
 *
 * Copyright © Egor Vavilov (Shecspi)
 * Licensed under the Apache License, Version 2.0
 *
 * ----------------------------------------------
 */

// SVG иконка локации для маркеров
const locationPinSvg = (color) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512" width="21" height="28" style="filter: drop-shadow(0 0 2px rgba(0, 0, 0, 0.5));">
    <path fill="${color}" stroke="rgba(0, 0, 0, 0.3)" stroke-width="1.5" stroke-linejoin="round" d="M215.7 499.2C267 435 384 279.4 384 192C384 86 298 0 192 0S0 86 0 192c0 87.4 117 243 168.3 307.2c12.3 15.3 35.1 15.3 47.4 0zM192 128a64 64 0 1 1 0 128 64 64 0 1 1 0-128z"/>
</svg>`;

// Иконка для посещённого пользователем города
export const icon_visited_pin = L.divIcon({
    className: 'custom-icon-visited-pin',
    html: locationPinSvg('rgb(66,178,66)'),
    iconSize: [21, 28],
    iconAnchor: [10.5, 28],
    popupAnchor: [0, -28],
    tooltipAnchor: [0, -28]
});

// Иконка для города, который не посетил ни пользователь, ни те, на кого он подписан
export const icon_not_visited_pin = L.divIcon({
    className: 'custom-icon-not_visited-pin',
    html: locationPinSvg('rgb(210, 90, 90)'),
    iconSize: [21, 28],
    anchor: [10.5, 28],
    iconAnchor: [10.5, 28],
    popupAnchor: [0, -28],
    tooltipAnchor: [0, -28]
});

// Иконка для города, который был посещён пользователем и кем-то из тех, на кого он подписан
export const icon_together_pin = L.divIcon({
    className: 'custom-icon-together-pin',
    html: locationPinSvg('rgb(38,122,10)'),
    iconSize: [21, 28],
    anchor: [10.5, 28],
    iconAnchor: [10.5, 28],
    popupAnchor: [0, -28],
    tooltipAnchor: [0, -28]
});

// Иконка для города, который не был посещён пользователя, но посещён кем-то из тех, на кого он подписан
export const icon_subscription_pin = L.divIcon({
    className: 'custom-icon-subscription-pin',
    html: locationPinSvg('rgb(230, 150, 30)'),
    iconSize: [21, 28],
    anchor: [10.5, 28],
    iconAnchor: [10.5, 28],
    popupAnchor: [0, -28],
    tooltipAnchor: [0, -28]
});

export const icon_blue_pin = L.divIcon({
    className: 'custom-icon-place-pin',
    html: locationPinSvg('rgb(79, 70, 229)'), // indigo-600
    iconSize: [21, 28],
    anchor: [10.5, 28],
    iconAnchor: [10.5, 28],
    popupAnchor: [0, -28],
    tooltipAnchor: [0, -28]
});

export const icon_purple_pin = L.divIcon({
    className: 'custom-icon-place-pin',
    html: locationPinSvg('rgb(107, 114, 128)'), // gray-500 — новое место при клике по карте
    iconSize: [21, 28],
    anchor: [10.5, 28],
    iconAnchor: [10.5, 28],
    popupAnchor: [0, -28],
    tooltipAnchor: [0, -28]
});

// Место добавлено, но не посещено (оранжевый, чтобы отличался от зелёного и розового)
export const icon_place_not_visited_pin = L.divIcon({
    className: 'custom-icon-place-not-visited-pin',
    html: locationPinSvg('rgb(234, 88, 12)'), // orange-600
    iconSize: [21, 28],
    iconAnchor: [10.5, 28],
    popupAnchor: [0, -28],
    tooltipAnchor: [0, -28]
});