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
    html: '<i class="fa-solid fa-location-dot fs-3 text-success" style="text-shadow: 0 0 2px #333333;"></i>',
    iconSize: [21, 28],
    anchor: [10.5, 28]
});

// Иконка для города, который не посетил ни пользователь, ни те, на кого он подписан
export const icon_not_visited_pin = L.divIcon({
    className: 'custom-icon-not_visited-pin',
    html: '<i class="fa-solid fa-location-dot fs-3 text-danger" style="text-shadow: 0 0 2px #333333;"></i>',
    iconSize: [21, 28],
    anchor: [10.5, 28]
});

// Иконка для города, который был посещён пользователем и кем-то из тех, на кого он подписан
export const icon_together_pin = L.divIcon({
    className: 'custom-icon-together-pin',
    html: '<i class="fa-solid fa-location-dot fs-3 text-primary" style="text-shadow: 0 0 2px #333333;"></i>',
    iconSize: [21, 28],
    anchor: [10.5, 28]
});

// Иконка для города, который не был посещён пользователя, но посещён кем-то из тех, на кого он подписан
export const icon_subscription_pin = L.divIcon({
    className: 'custom-icon-together-pin',
    html: '<i class="fa-solid fa-location-dot fs-3 text-secondary" style="text-shadow: 0 0 2px #333333;"></i>',
    iconSize: [21, 28],
    anchor: [10.5, 28]
});