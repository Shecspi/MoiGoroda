/**
 * Загрузка статистики публичных коллекций.
 *
 * ----------------------------------------------
 *
 * Copyright © Egor Vavilov (Shecspi)
 * Licensed under the Apache License, Version 2.0
 *
 * ----------------------------------------------
 */

import {pluralize} from '../components/search_services.js';

document.addEventListener('DOMContentLoaded', () => {
    // Элементы для отображения статистики
    const collectionsCountElement = document.getElementById('statistics-collections-count');
    const usersCountElement = document.getElementById('statistics-users-count');
    const citiesCountElement = document.getElementById('statistics-cities-count');
    const collectionsWordElement = document.getElementById('statistics-collections-word');
    const usersWordElement = document.getElementById('statistics-users-word');
    const citiesWordElement = document.getElementById('statistics-cities-word');

    // Проверяем, что элементы существуют
    if (!collectionsCountElement || !usersCountElement || !citiesCountElement ||
        !collectionsWordElement || !usersWordElement || !citiesWordElement) {
        return;
    }

    // Функция для форматирования чисел (добавление пробелов для тысяч)
    const formatNumber = (num) => {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
    };

    // Загружаем статистику
    const loadStatistics = async () => {
        try {
            const response = await fetch('/api/collection/personal/public/statistics', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error('Не удалось загрузить статистику');
            }

            const data = await response.json();

            // Обновляем значения в DOM (заменяем спиннер на данные)
            collectionsCountElement.innerHTML = formatNumber(data.collections_count);
            usersCountElement.innerHTML = formatNumber(data.users_count);
            citiesCountElement.innerHTML = formatNumber(data.cities_count);

            // Обновляем склонение слов с развернутыми фразами
            collectionsWordElement.textContent = pluralize(
                data.collections_count,
                'Коллекция',
                'Коллекции',
                'Коллекций'
            );
            usersWordElement.textContent = pluralize(
                data.users_count,
                'Пользователь с коллекциями',
                'Пользователя с коллекциями',
                'Пользователей с коллекциями'
            );
            citiesWordElement.textContent = pluralize(
                data.cities_count,
                'Город в коллекциях',
                'Города в коллекциях',
                'Городов в коллекциях'
            );
        } catch (error) {
            console.error('Ошибка при загрузке статистики:', error);
            // Оставляем прочерки при ошибке
            collectionsCountElement.innerHTML = '—';
            usersCountElement.innerHTML = '—';
            citiesCountElement.innerHTML = '—';
        }
    };

    // Загружаем статистику при загрузке страницы
    loadStatistics();
});
