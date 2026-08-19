// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import {initCountrySelect} from "../components/initCountrySelect";
import {showDangerToast, showSuccessToast} from "../components/toast.js";

const CITY_ADDED_SUCCESS_MESSAGE = 'Город успешно добавлен как посещённый';

document.addEventListener('city-added', async (event) => {
    event.preventDefault();
    const cityName = event.detail?.city?.name;
    const successMessage = cityName
        ? `Город ${cityName} успешно добавлен как посещённый`
        : CITY_ADDED_SUCCESS_MESSAGE;
    showSuccessToast('Успешно', successMessage);

    try {
        const currentResults = document.getElementById('city-list-results');
        if (!currentResults) {
            throw new Error('City list results not found');
        }

        const fragmentUrl = new URL(currentResults.dataset.fragmentUrl, window.location.origin);
        fragmentUrl.search = window.location.search;
        const response = await fetch(fragmentUrl.toString());
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const updatedPage = new DOMParser().parseFromString(await response.text(), 'text/html');
        const updatedResults = updatedPage.getElementById('city-list-results');
        const updatedToolbarStats = updatedPage.querySelector('.toolbar-stats');
        const currentToolbarStats = document.querySelector('.toolbar-stats');
        if (!updatedResults || !updatedToolbarStats || !currentToolbarStats) {
            throw new Error('City list fragment is incomplete');
        }

        currentResults.replaceWith(updatedResults);
        currentToolbarStats.replaceWith(updatedToolbarStats);
    } catch (error) {
        console.error('Ошибка при обновлении списка городов:', error);
        showDangerToast('Ошибка', 'Не удалось обновить список городов. Обновите страницу вручную.');
    }
});

document.addEventListener('DOMContentLoaded', async (event) => {
    const toolbar = document.getElementById('toolbar');
    
    // Инициализируем селект страны
    await initCountrySelect();
    
    // После загрузки всех элементов показываем тулбар с анимацией
    if (toolbar) {
        // Небольшая задержка для гарантии, что все элементы отрендерены
        setTimeout(() => {
            toolbar.classList.add('toolbar-loaded');
        }, 50);
    }
});
