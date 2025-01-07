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

// Иконка для посещённого пользователем города
export const icon_visited_pin = L.divIcon({
    className: 'custom-icon-visited-pin',
    html: '<i class="fa-solid fa-location-dot fs-3 icon-visited-pin" style="color: rgb(90, 170, 90) !important; text-shadow: 0 0 2px #333333;"></i>',
    iconSize: [21, 28],
    iconAnchor: [10.5, 28],
    popupAnchor: [0, -28],
    tooltipAnchor: [0, -28]
});

// Иконка для города, который не посетил ни пользователь, ни те, на кого он подписан
export const icon_not_visited_pin = L.divIcon({
    className: 'custom-icon-not_visited-pin',
    html: '<i class="fa-solid fa-location-dot fs-3 icon-not-visited-pin" style="color: rgb(210, 90, 90) !important; text-shadow: 0 0 2px #333333;"></i>',
    iconSize: [21, 28],
    anchor: [10.5, 28],
    iconAnchor: [10.5, 28],
    popupAnchor: [0, -28],
    tooltipAnchor: [0, -28]
});

// Иконка для города, который был посещён пользователем и кем-то из тех, на кого он подписан
export const icon_together_pin = L.divIcon({
    className: 'custom-icon-together-pin',
    html: '<i class="fa-solid fa-location-dot fs-3 icon-together-pin" style="color: rgb(40, 130, 10) !important; text-shadow: 0 0 2px #333333;"></i>',
    iconSize: [21, 28],
    anchor: [10.5, 28],
    iconAnchor: [10.5, 28],
    popupAnchor: [0, -28],
    tooltipAnchor: [0, -28]
});

// Иконка для города, который не был посещён пользователя, но посещён кем-то из тех, на кого он подписан
export const icon_subscripticon_visited_pinion_pin = L.divIcon({
    className: 'custom-icon-subscription-pin',
    html: '<i class="fa-solid fa-location-dot fs-3  icon-subscription-pin" style="color: rgb(230, 150, 30) !important; text-shadow: 0 0 2px #333333;"></i>',
    iconSize: [21, 28],
    anchor: [10.5, 28],
    iconAnchor: [10.5, 28],
    popupAnchor: [0, -28],
    tooltipAnchor: [0, -28]
});

export const icon_blue_pin = L.divIcon({
    className: 'custom-icon-place-pin',
    html: '<i class="fa-solid fa-location-dot fs-3  icon-subscription-pin" style="color: rgb(12,87,225) !important; text-shadow: 0 0 2px #333333;"></i>',
    iconSize: [21, 28],
    anchor: [10.5, 28],
    iconAnchor: [10.5, 28],
    popupAnchor: [0, -28],
    tooltipAnchor: [0, -28]
});

export const icon_purple_pin = L.divIcon({
    className: 'custom-icon-place-pin',
    html: '<i class="fa-solid fa-location-dot fs-3  icon-subscription-pin" style="color: rgb(220,66,217) !important; text-shadow: 0 0 2px #333333;"></i>',
    iconSize: [21, 28],
    anchor: [10.5, 28],
    iconAnchor: [10.5, 28],
    popupAnchor: [0, -28],
    tooltipAnchor: [0, -28]
});