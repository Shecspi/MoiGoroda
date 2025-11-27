import {initCountrySelect} from "../components/initCountrySelect";

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