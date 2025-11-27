import Choices from 'choices.js';

import {showDangerToast} from "../components/toast";

document.addEventListener('DOMContentLoaded', () => {
    const countrySelect = document.getElementById('id_country');
    const regionSelect = document.getElementById('id_region');
    const citySelect = document.getElementById('id_city');
    const submitButton = document.getElementById('submit-button');
    const ratingInput = document.querySelector('input[name="rating"]');

    const choicesCountry = new Choices(countrySelect, {
        searchEnabled: true,
        shouldSort: false,
        placeholderValue: 'Выберите страну',
        noResultsText: 'Ничего не найдено',
        noChoicesText: 'Нет доступных вариантов',
        itemSelectText: 'Нажмите для выбора',
        loadingText: 'Загрузка...',
    });
    // Удаляем пустую опцию из regionSelect, чтобы Choices.js использовал placeholder
    const regionEmptyOption = regionSelect.querySelector('option[value=""]');
    if (regionEmptyOption) {
        regionEmptyOption.remove();
    }
    
    const choicesRegion = new Choices(regionSelect, {
        searchEnabled: true,
        shouldSort: false,
        placeholderValue: 'Выберите регион',
        noResultsText: 'Ничего не найдено',
        noChoicesText: 'Нет доступных вариантов',
        itemSelectText: 'Нажмите для выбора',
        loadingText: 'Загрузка...',
    });
    // Удаляем пустую опцию из citySelect, чтобы Choices.js использовал placeholder
    const cityEmptyOption = citySelect.querySelector('option[value=""]');
    if (cityEmptyOption) {
        cityEmptyOption.remove();
    }
    
    const choicesCity = new Choices(citySelect, {
        searchEnabled: true,
        shouldSort: false,
        placeholderValue: 'Выберите город',
        noResultsText: 'Ничего не найдено',
        noChoicesText: 'Нет доступных вариантов',
        itemSelectText: 'Нажмите для выбора',
        loadingText: 'Загрузка...',
    });
    
    // Проверяем начальные значения для определения состояния поля города
    const initialRegionValue = regionSelect.value;
    const initialCountryValue = countrySelect.value;
    const initialCityValue = citySelect.value;
    
    // Если город уже выбран (режим редактирования) - поле должно быть активным
    if (initialCityValue) {
        // Город уже выбран, поле активно и обязательно
        citySelect.setAttribute('required', 'required');
    } else if (initialCountryValue && !initialRegionValue) {
        // Если страна выбрана, но регион нет - проверяем, есть ли у страны регионы
        // Это будет обработано при загрузке регионов
        choicesCity.disable();
        citySelect.removeAttribute('required');
    } else if (!initialRegionValue) {
        // Если регион не выбран вообще - отключаем поле города
        choicesCity.disable();
        citySelect.removeAttribute('required');
    } else {
        // Если регион выбран - поле города активно и обязательно
        citySelect.setAttribute('required', 'required');
    }

    // При изменении страны делаем запрос и обновляем регионы
    countrySelect.addEventListener('change', async (event) => {
        choicesRegion.enable();
        choicesCity.enable();

        const countryId = event.target.value;

        if (!countryId) {
            // Очистить регионы и города, если страна не выбрана
            choicesRegion.clearStore();
            choicesRegion.disable();
            choicesCity.clearStore();
            choicesCity.disable();
            citySelect.removeAttribute('required');
            validateForm();
            return;
        }

        try {
            // Загрузка регионов страны
            const response = await fetch(`/api/region/list?country_id=${countryId}`);
            if (!response.ok) throw new Error('Ошибка загрузки регионов');

            const regions = await response.json();

            // Очистить старые опции
            choicesRegion.clearStore();
            choicesCity.clearStore();

            // В ситуации, когда у страны нет региона - загружаем все города
            if (regions.length === 0) {
                choicesRegion.disable();
                const cityResponse = await fetch(`/api/city/list_by_country?country_id=${countryId}`);
                if (!cityResponse.ok) throw new Error('Ошибка загрузки городов');

                const cities = await cityResponse.json();

                if (cities.length === 0) {
                    choicesCity.disable();
                    citySelect.removeAttribute('required');
                    showDangerToast('Ошибка', 'Для выбранной страны нет городов');
                    validateForm();
                    return;
                }

                choicesCity.setChoices(
                    cities.map((city, index) => ({
                        value: city.id,
                        label: city.title,
                        selected: index === 0, // Делаем первый город выбранным
                        disabled: false,
                    })),
                    'value',
                    'label',
                    true
                );
                choicesCity.enable();
                citySelect.setAttribute('required', 'required');
                // Небольшая задержка для обновления значения после setChoices
                setTimeout(() => {
                    // Убеждаемся, что значение установлено
                    if (cities.length > 0 && !citySelect.value) {
                        citySelect.value = cities[0].id;
                        citySelect.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                    validateForm();
                }, 100);
            } else {
                // Добавить новые опции без автоматического выбора первого региона
                choicesRegion.setChoices(
                    regions.map((region) => ({
                        value: region.id,
                        label: region.title,
                        selected: false, // Не выбираем регион автоматически
                        disabled: false,
                    })),
                    'value',
                    'label',
                    true,
                );

                // Отключаем поле города, пока регион не выбран явно
                choicesCity.disable();
                choicesCity.clearStore();
                citySelect.removeAttribute('required');
                validateForm();
            }
        } catch (error) {
            console.error('Ошибка при загрузке регионов:', error);
            showDangerToast('Ошибка', 'Произошла ошибка при загрузке списка регионов. Пожалуйста, перезагрузите страницу и попробуйте ещё раз.')
        }
    });

    regionSelect.addEventListener('change', async (event) => {
        const regionId = event.target.value;

        if (!regionId) {
            // Если регион не выбран, отключаем поле города
            choicesCity.disable();
            choicesCity.clearStore();
            citySelect.removeAttribute('required');
            validateForm();
            return;
        }

        choicesCity.enable();
        choicesCity.clearStore();
        citySelect.setAttribute('required', 'required');

        try {
            const cityResponse = await fetch(`/api/city/list_by_region?region_id=${regionId}`);
            if (!cityResponse.ok) throw new Error('Ошибка загрузки городов');

            const cities = await cityResponse.json();

            if (cities.length === 0) {
                choicesCity.disable();
                citySelect.removeAttribute('required');
                showDangerToast('Ошибка', 'Для выбранного региона нет городов');
                return;
            }

            choicesCity.setChoices(
                cities.map((city, index) => ({
                    value: city.id,
                    label: city.title,
                    selected: index === 0, // Делаем первый город выбранным
                    disabled: false,
                })),
                'value',
                'label',
                true
            );
            // Небольшая задержка для обновления значения после setChoices
            setTimeout(() => {
                // Убеждаемся, что значение установлено
                if (cities.length > 0 && !citySelect.value) {
                    citySelect.value = cities[0].id;
                    citySelect.dispatchEvent(new Event('change', { bubbles: true }));
                }
                validateForm();
            }, 100);
        } catch (error) {
            console.error('Ошибка при загрузке городов:', error);
            choicesCity.disable();
            citySelect.removeAttribute('required');
            showDangerToast('Ошибка', 'Произошла ошибка при загрузке списка городов. Пожалуйста, попробуйте ещё раз.');
            validateForm();
        }
    });

    function setTodayDate() {
            const today = new Date();
            const day = String(today.getDate()).padStart(2, '0');
            const month = String(today.getMonth() + 1).padStart(2, '0');
            const year = today.getFullYear();
            const formattedDate = `${year}-${month}-${day}`;

            // Устанавливаем текущую дату в поле ввода
            document.getElementById('id_date_of_visit').value = formattedDate;
        }

        function setYesterdayDate() {
            const today = new Date();
            today.setDate(today.getDate() - 1);  // Уменьшаем на 1 день, чтобы получить вчерашнюю дату

            const day = String(today.getDate()).padStart(2, '0');
            const month = String(today.getMonth() + 1).padStart(2, '0');
            const year = today.getFullYear();
            const formattedDate = `${year}-${month}-${day}`;

            // Устанавливаем вчерашнюю дату в поле ввода
            document.getElementById('id_date_of_visit').value = formattedDate;
        }

        document.getElementById('today-button').addEventListener('click', setTodayDate);
        document.getElementById('yesterday-button').addEventListener('click', setYesterdayDate);

    // Функция проверки обязательных полей и управления кнопкой
    function validateForm() {
        if (!submitButton) return;
        
        // Получаем значения напрямую из select элементов (Choices.js обновляет их)
        const countryValue = countrySelect?.value || '';
        const cityValue = citySelect?.value || '';
        const ratingValue = ratingInput?.value || '';
        
        // Проверяем, отключено ли поле города через Choices.js
        const cityChoicesElement = citySelect?.closest('.choices');
        const isCityDisabled = cityChoicesElement?.classList.contains('is-disabled') || false;
        
        // Проверяем, есть ли у страны регионы
        const regionValue = regionSelect?.value || '';
        const regionChoicesElement = regionSelect?.closest('.choices');
        const isRegionDisabled = regionChoicesElement?.classList.contains('is-disabled') || false;
        
        // Если регион отключен, значит у страны нет регионов
        // Проверяем количество опций в регионе (больше 1, т.к. есть пустая опция)
        const regionOptions = regionSelect?.querySelectorAll('option');
        const countryHasRegions = !isRegionDisabled && regionOptions && regionOptions.length > 1;
        
        let isFormValid = true;
        
        // Страна обязательна всегда
        if (!countryValue) {
            isFormValid = false;
        }
        
        // Город обязателен, если:
        // 1. У страны есть регионы И регион выбран И город не выбран И поле города не отключено
        // 2. У страны нет регионов И поле города активно (не отключено) И город не выбран
        if (countryHasRegions) {
            if (regionValue && !isCityDisabled && !cityValue) {
                isFormValid = false;
            }
        } else if (countryValue && !isCityDisabled && !cityValue) {
            // Если у страны нет регионов, но поле города активно и пустое
            isFormValid = false;
        }
        
        // Рейтинг обязателен всегда
        if (!ratingValue) {
            isFormValid = false;
        }
        
        // Обновляем состояние кнопки
        submitButton.disabled = !isFormValid;
    }
    
    // Rating stars handler
    const ratingContainer = document.getElementById('rating-container');
    if (ratingContainer && ratingInput) {
        const ratingStars = ratingContainer.querySelectorAll('.rating-star');

        if (ratingStars && ratingStars.length > 0) {

    // Define functions first
    const updateRatingStars = (rating) => {
        ratingStars.forEach((star) => {
            const starRating = parseInt(star.dataset.rating);
            if (starRating <= rating && rating > 0) {
                star.classList.remove('text-gray-300', 'dark:text-neutral-600');
                star.classList.add('text-yellow-400', 'dark:text-yellow-500');
            } else {
                star.classList.remove('text-yellow-400', 'dark:text-yellow-500');
                star.classList.add('text-gray-300', 'dark:text-neutral-600');
            }
        });
    };

    const highlightStars = (rating) => {
        ratingStars.forEach((star) => {
            const starRating = parseInt(star.dataset.rating);
            if (starRating <= rating) {
                star.classList.remove('text-gray-300', 'dark:text-neutral-600');
                star.classList.add('text-yellow-400', 'dark:text-yellow-500');
            } else {
                star.classList.remove('text-yellow-400', 'dark:text-yellow-500');
                star.classList.add('text-gray-300', 'dark:text-neutral-600');
            }
        });
    };

    // Initialize rating from form value
    const currentRating = parseInt(ratingInput.value) || 0;
    updateRatingStars(currentRating);

    // Add event listeners
    ratingStars.forEach((star) => {
        star.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const rating = parseInt(star.dataset.rating);
            ratingInput.value = rating;
            updateRatingStars(rating);
            validateForm();
        });

        star.addEventListener('mouseenter', () => {
            const hoverRating = parseInt(star.dataset.rating);
            highlightStars(hoverRating);
        });
    });

            ratingContainer.addEventListener('mouseleave', () => {
                const currentRating = parseInt(ratingInput.value) || 0;
                updateRatingStars(currentRating);
            });
            
            // Обновляем состояние кнопки при изменении рейтинга
            ratingInput.addEventListener('change', validateForm);
            ratingInput.addEventListener('input', validateForm);
        }
    }
    
    // Добавляем обработчики событий для проверки формы
    // Используем события Choices.js для более надежной работы
    if (choicesCountry) {
        countrySelect.addEventListener('change', validateForm);
        // Также слушаем события Choices.js
        countrySelect.addEventListener('choice', validateForm);
    }
    if (choicesRegion) {
        regionSelect.addEventListener('change', validateForm);
        regionSelect.addEventListener('choice', validateForm);
    }
    if (choicesCity) {
        citySelect.addEventListener('change', validateForm);
        citySelect.addEventListener('choice', validateForm);
    }
    
    // Проверяем форму при загрузке страницы с небольшой задержкой
    // для инициализации всех Choices.js элементов
    setTimeout(() => {
        validateForm();
    }, 200);
});
