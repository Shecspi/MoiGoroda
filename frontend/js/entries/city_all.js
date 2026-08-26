// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import {initCountrySelect} from "../components/initCountrySelect";

async function initCityListPage() {
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
}

document.addEventListener('DOMContentLoaded', initCityListPage);
document.addEventListener('visited-city-list-refreshed', initCityListPage);
