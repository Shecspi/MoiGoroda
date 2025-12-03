/**
 * Открывает модальное окно добавления города (Preline UI)
 */
export function open_modal_for_add_city(city, city_id, region_title) {
    const el_city_title = document.getElementById('city-title-in-modal');
    const el_region_title = document.getElementById('region-title-in-modal');
    const el_city_id = document.getElementById('city-id');

    el_city_title.innerText = city;
    el_region_title.innerText = region_title;
    el_city_id.setAttribute('value', city_id);
    
    // Сбрасываем рейтинг при открытии модального окна
    const ratingInput = document.getElementById('id_rating');
    const ratingContainer = document.getElementById('rating-container');
    const addButton = document.getElementById('btn_add-visited-city');
    if (ratingInput) {
        ratingInput.value = '';
    }
    if (ratingContainer) {
        // Сбрасываем визуальное состояние звезд
        const stars = ratingContainer.querySelectorAll('.rating-star');
        stars.forEach((star) => {
            star.classList.remove('text-yellow-400', 'dark:text-yellow-500');
            star.classList.add('text-gray-300', 'dark:text-neutral-600');
        });
    }
    // Делаем кнопку "Добавить" неактивной при открытии модального окна
    if (addButton) {
        addButton.disabled = true;
    }
    
    // Сбрасываем дату посещения
    const dateInput = document.getElementById('date-of-visit');
    if (dateInput) {
        dateInput.value = '';
    }
    
    // Сбрасываем наличие сувенира (чекбокс)
    const magnetCheckbox = document.getElementById('magnet-checkbox');
    if (magnetCheckbox) {
        magnetCheckbox.checked = false;
    }

    // Открываем модальное окно через Preline UI
    const modalElement = document.getElementById('addCityModal');
    if (modalElement) {
        // Если модальное окно уже открыто, не делаем ничего
        if (!modalElement.classList.contains('hidden')) {
            return;
        }
        
        // Создаем или находим backdrop для модального окна
        let backdrop = document.querySelector('[data-hs-overlay-backdrop="#addCityModal"]');
        if (!backdrop) {
            // Создаем backdrop вручную, если Preline UI его не создал
            backdrop = document.createElement('div');
            backdrop.setAttribute('data-hs-overlay-backdrop', '#addCityModal');
            backdrop.className = 'hs-overlay-backdrop fixed inset-0 z-[1059] bg-gray-900/50 pointer-events-none';
            backdrop.setAttribute('aria-hidden', 'true');
            document.body.appendChild(backdrop);
        }
        
        // Открываем модальное окно
        modalElement.classList.remove('hidden');
        modalElement.classList.add('open');
        modalElement.classList.remove('pointer-events-none');
        
        // Показываем backdrop с быстрой анимацией
        // Сначала устанавливаем opacity: 0 и transition для анимации
        backdrop.style.transition = 'opacity 200ms';
        backdrop.style.opacity = '0';
        backdrop.style.pointerEvents = 'none';
        backdrop.classList.remove('opacity-100', 'pointer-events-auto');
        backdrop.classList.add('opacity-0', 'pointer-events-none');
        
        // Принудительно применяем стили
        backdrop.offsetHeight; // Force reflow
        
        // Затем анимируем появление backdrop
        requestAnimationFrame(() => {
            backdrop.style.opacity = '1';
            backdrop.style.pointerEvents = 'auto';
            backdrop.classList.remove('opacity-0', 'pointer-events-none');
            backdrop.classList.add('opacity-100', 'pointer-events-auto');
            backdrop.setAttribute('aria-hidden', 'false');
        });
        
        // Обновляем animation target для правильной анимации
        const animationTarget = modalElement.querySelector('.hs-overlay-animation-target');
        if (animationTarget) {
            animationTarget.style.marginTop = '1.75rem';
            animationTarget.style.opacity = '1';
            animationTarget.style.transition = 'all 500ms ease-out';
        }
        
        // Устанавливаем display: flex для модального окна
        modalElement.style.display = 'flex';
        
        // Добавляем обработчик клика на backdrop для закрытия модального окна
        const backdropClickHandler = function() {
            close_modal_for_add_city();
        };
        backdrop.removeEventListener('click', backdropClickHandler); // Удаляем старый обработчик, если есть
        backdrop.addEventListener('click', backdropClickHandler);
    }
}

/**
 * Закрывает модальное окно добавления города (Preline UI)
 */
export function close_modal_for_add_city() {
    const modalElement = document.getElementById('addCityModal');
    if (modalElement) {
        // Закрываем модальное окно
        modalElement.classList.add('hidden');
        modalElement.classList.remove('open');
        modalElement.classList.add('pointer-events-none');
        modalElement.style.display = '';
        
        // Скрываем backdrop
        const backdrop = document.querySelector('[data-hs-overlay-backdrop="#addCityModal"]');
        if (backdrop) {
            // Применяем transition для плавного скрытия
            backdrop.style.transition = 'opacity 500ms';
            // Устанавливаем opacity: 0 через inline стили для гарантированного скрытия
            backdrop.style.opacity = '0';
            backdrop.style.pointerEvents = 'none';
            backdrop.classList.remove('opacity-100', 'pointer-events-auto');
            backdrop.classList.add('opacity-0', 'pointer-events-none');
            backdrop.setAttribute('aria-hidden', 'true');
            
            // После завершения анимации сбрасываем inline стили
            setTimeout(() => {
                backdrop.style.transition = '';
                backdrop.style.opacity = '';
                backdrop.style.pointerEvents = '';
            }, 500);
        }
        
        // Сбрасываем animation target
        const animationTarget = modalElement.querySelector('.hs-overlay-animation-target');
        if (animationTarget) {
            animationTarget.style.marginTop = '';
            animationTarget.style.opacity = '';
            animationTarget.style.transition = '';
        }
    }
}

export function change_qty_of_visited_cities_in_toolbar(is_added_new_city) {
    /**
     * Производит замену текста, сообщающего о количестве посещённых городов, в информационной карточке тулбара.
     */
    const number_of_visited_cities = document.getElementById('number_of_visited_cities');
    if (!number_of_visited_cities) {
        // На этой странице нет тулбара с количеством посещённых городов (например, карта региона).
        // Просто выходим без ошибок, чтобы не ломать логику и не показывать лишний тост об ошибке.
        return;
    }

    const oldQty = number_of_visited_cities.textContent;
    const newQty = is_added_new_city === true ? Number(oldQty) + 1 : oldQty;
    number_of_visited_cities.innerText = newQty.toString();
}