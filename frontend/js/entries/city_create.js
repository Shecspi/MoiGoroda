import {showDangerToast} from "../components/toast";
import {initVisitDatePickers, setVisitDateInputValue} from "../components/visit_date_picker.js";

/**
 * Переинициализация Preline HSSelect после изменения опций в нативном select.
 * @param {string} selectId — атрибут id без #
 */
function destroyHsSelect(selectId) {
    const inst = window.HSSelect?.getInstance?.(`#${selectId}`);
    if (inst && typeof inst.destroy === 'function') {
        inst.destroy();
    }
}

/**
 * Сразу после обновления DOM опций — без отложенных кадров, иначе после destroy()
 * на долю секунды виден «пустой» интерфейс или нативный select (моргание).
 */
function reinitHsSelectSync(selectId) {
    try {
        if (window.HSSelect) {
            new window.HSSelect(`#${selectId}`);
        }
    } catch (e) {
        if (window.HSStaticMethods && typeof window.HSStaticMethods.autoInit === 'function') {
            window.HSStaticMethods.autoInit();
        }
    }
}

/**
 * Серый «пустой» вид для type=date: класс синхронизируется с input.value.
 */
function bindDateInputEmptyAppearance(input) {
    if (!input) {
        return () => {};
    }
    const sync = () => {
        input.classList.toggle('form-input-date-empty', !input.value);
    };
    sync();
    input.addEventListener('input', sync);
    input.addEventListener('change', sync);
    return sync;
}

/** Пока ждём API регионов — одна опция, поле неактивно (не показываем список прошлой страны). */
function setRegionSelectLoading() {
    const sel = document.getElementById('id_region');
    if (!sel) {
        return;
    }
    destroyHsSelect('id_region');
    sel.innerHTML = '';
    const opt = document.createElement('option');
    opt.value = '';
    opt.textContent = 'Загрузка...';
    sel.appendChild(opt);
    sel.value = '';
    sel.disabled = true;
    reinitHsSelectSync('id_region');
}

/**
 * @param {Array<{ id: number|string, title: string }>} regions
 * @param {{ disabled: boolean, emptyLabel?: string }} options
 */
function setRegionSelectOptions(regions, { disabled, emptyLabel = 'Выберите регион' }) {
    const sel = document.getElementById('id_region');
    if (!sel) {
        return;
    }
    destroyHsSelect('id_region');
    sel.innerHTML = '';
    const empty = document.createElement('option');
    empty.value = '';
    empty.textContent = emptyLabel;
    sel.appendChild(empty);
    regions.forEach((r) => {
        const o = document.createElement('option');
        o.value = String(r.id);
        o.textContent = r.title;
        sel.appendChild(o);
    });
    sel.value = '';
    sel.disabled = disabled;
    reinitHsSelectSync('id_region');
}

function setCitySelectLoading() {
    const sel = document.getElementById('id_city');
    if (!sel) {
        return;
    }
    destroyHsSelect('id_city');
    sel.innerHTML = '';
    const opt = document.createElement('option');
    opt.value = '';
    opt.textContent = 'Загрузка...';
    sel.appendChild(opt);
    sel.value = '';
    sel.disabled = true;
    reinitHsSelectSync('id_city');
}

/**
 * @param {Array<{ id: number|string, title: string }>} cities
 * @param {{ disabled: boolean, emptyLabel?: string, selectFirst?: boolean }} options
 */
function setCitySelectOptions(cities, { disabled, emptyLabel = 'Выберите город', selectFirst = false }) {
    const sel = document.getElementById('id_city');
    if (!sel) {
        return;
    }
    destroyHsSelect('id_city');
    sel.innerHTML = '';
    const empty = document.createElement('option');
    empty.value = '';
    empty.textContent = emptyLabel;
    sel.appendChild(empty);
    cities.forEach((c) => {
        const o = document.createElement('option');
        o.value = String(c.id);
        o.textContent = c.title;
        sel.appendChild(o);
    });
    if (selectFirst && cities.length > 0) {
        sel.value = String(cities[0].id);
    } else {
        sel.value = '';
    }
    sel.disabled = disabled;
    reinitHsSelectSync('id_city');
    if (selectFirst && cities.length > 0) {
        sel.dispatchEvent(new Event('change', { bubbles: true }));
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // После city_create.js подключается preline.js (autoInit HSSelect). Откладываем привязку обработчиков формы.
    setTimeout(() => {
        initCityCreateForm();
    }, 0);
});

function initCityCreateForm() {
    const countrySelect = document.getElementById('id_country');
    const regionSelect = document.getElementById('id_region');
    const citySelect = document.getElementById('id_city');
    const submitButton = document.getElementById('submit-button');
    const ratingInput = document.querySelector('input[name="rating"]');

    if (!countrySelect || !regionSelect || !citySelect) {
        return;
    }

    initVisitDatePickers();

    const dateOfVisitInput = document.getElementById('id_date_of_visit');
    const syncDateInputAppearance = bindDateInputEmptyAppearance(dateOfVisitInput);

    // Проверяем начальные значения для определения состояния поля города
    const initialRegionValue = regionSelect.value;
    const initialCityValue = citySelect.value;

    if (initialCityValue) {
        citySelect.setAttribute('required', 'required');
    } else if (!initialRegionValue) {
        setCitySelectOptions([], { disabled: true });
        citySelect.removeAttribute('required');
    } else {
        citySelect.setAttribute('required', 'required');
    }

    let countryFetchController = null;
    let regionFetchController = null;

    // При изменении страны делаем запрос и обновляем регионы
    countrySelect.addEventListener('change', async (event) => {
        const countryId = event.target.value;

        if (countryFetchController) {
            countryFetchController.abort();
        }
        countryFetchController = null;

        if (regionFetchController) {
            regionFetchController.abort();
        }
        regionFetchController = null;

        if (!countryId) {
            setRegionSelectOptions([], { disabled: true });
            setCitySelectOptions([], { disabled: true });
            citySelect.removeAttribute('required');
            validateForm();
            return;
        }

        countryFetchController = new AbortController();
        const { signal } = countryFetchController;

        setRegionSelectLoading();

        try {
            const response = await fetch(`/api/region/list?country_id=${countryId}`, { signal });
            if (countrySelect.value !== countryId) {
                return;
            }
            if (!response.ok) throw new Error('Ошибка загрузки регионов');

            const regions = await response.json();
            if (countrySelect.value !== countryId) {
                return;
            }

            if (regions.length === 0) {
                setRegionSelectOptions([], { disabled: true });
                setCitySelectLoading();
                const cityResponse = await fetch(`/api/city/list_by_country?country_id=${countryId}`, { signal });
                if (countrySelect.value !== countryId) {
                    return;
                }
                if (!cityResponse.ok) throw new Error('Ошибка загрузки городов');

                const cities = await cityResponse.json();
                if (countrySelect.value !== countryId) {
                    return;
                }

                if (cities.length === 0) {
                    setCitySelectOptions([], { disabled: true });
                    citySelect.removeAttribute('required');
                    showDangerToast('Ошибка', 'Для выбранной страны нет городов');
                    validateForm();
                    return;
                }

                setCitySelectOptions(cities, { disabled: false, selectFirst: true });
                citySelect.setAttribute('required', 'required');
                validateForm();
            } else {
                setRegionSelectOptions(regions, { disabled: false });
                setCitySelectOptions([], { disabled: true });
                citySelect.removeAttribute('required');
                validateForm();
            }
        } catch (error) {
            if (error.name === 'AbortError') {
                return;
            }
            console.error('Ошибка при загрузке регионов:', error);
            setRegionSelectOptions([], { disabled: true });
            setCitySelectOptions([], { disabled: true });
            showDangerToast('Ошибка', 'Произошла ошибка при загрузке списка регионов. Пожалуйста, перезагрузите страницу и попробуйте ещё раз.');
            validateForm();
        }
    });

    regionSelect.addEventListener('change', async (event) => {
        const regionId = event.target.value;

        if (regionFetchController) {
            regionFetchController.abort();
        }
        regionFetchController = null;

        if (!regionId) {
            setCitySelectOptions([], { disabled: true });
            citySelect.removeAttribute('required');
            validateForm();
            return;
        }

        regionFetchController = new AbortController();
        const { signal } = regionFetchController;

        setCitySelectLoading();
        citySelect.setAttribute('required', 'required');

        try {
            const cityResponse = await fetch(`/api/city/list_by_region?region_id=${regionId}`, { signal });
            if (regionSelect.value !== regionId) {
                return;
            }
            if (!cityResponse.ok) throw new Error('Ошибка загрузки городов');

            const cities = await cityResponse.json();
            if (regionSelect.value !== regionId) {
                return;
            }

            if (cities.length === 0) {
                setCitySelectOptions([], { disabled: true });
                citySelect.removeAttribute('required');
                showDangerToast('Ошибка', 'Для выбранного региона нет городов');
                validateForm();
                return;
            }

            setCitySelectOptions(cities, { disabled: false, selectFirst: true });
            validateForm();
        } catch (error) {
            if (error.name === 'AbortError') {
                return;
            }
            console.error('Ошибка при загрузке городов:', error);
            setCitySelectOptions([], { disabled: true });
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

        if (dateOfVisitInput) {
            setVisitDateInputValue('#id_date_of_visit', formattedDate);
            syncDateInputAppearance();
        }
    }

    function setYesterdayDate() {
        const today = new Date();
        today.setDate(today.getDate() - 1); // Уменьшаем на 1 день, чтобы получить вчерашнюю дату

        const day = String(today.getDate()).padStart(2, '0');
        const month = String(today.getMonth() + 1).padStart(2, '0');
        const year = today.getFullYear();
        const formattedDate = `${year}-${month}-${day}`;

        if (dateOfVisitInput) {
            setVisitDateInputValue('#id_date_of_visit', formattedDate);
            syncDateInputAppearance();
        }
    }

    document.getElementById('today-button')?.addEventListener('click', setTodayDate);
    document.getElementById('yesterday-button')?.addEventListener('click', setYesterdayDate);

    // Функция проверки обязательных полей и управления кнопкой
    function validateForm() {
        if (!submitButton) return;
        
        // Получаем значения напрямую из select (Preline синхронизирует native select)
        const countryValue = countrySelect?.value || '';
        const cityValue = citySelect?.value || '';
        const ratingValue = ratingInput?.value || '';
        
        const isCityDisabled = citySelect?.disabled ?? false;
        
        // Проверяем, есть ли у страны регионы
        const regionValue = regionSelect?.value || '';
        const isRegionDisabled = regionSelect?.disabled ?? false;
        
        // Если регион отключен, значит у страны нет регионов
        // Проверяем количество опций в регионе (больше 1, т.к. есть пустая опция)
        const regionOptions = regionSelect?.querySelectorAll('option');
        const countryHasRegions = !isRegionDisabled && regionOptions && regionOptions.length > 1;
        
        let isFormValid = true;
        
        // Страна обязательна всегда
        if (!countryValue) {
            isFormValid = false;
        }
        
        // У страны есть регионы: нужны регион, затем город (пока города грузятся — поле города disabled).
        if (countryHasRegions) {
            if (!regionValue) {
                isFormValid = false;
            } else if (!isCityDisabled && !cityValue) {
                isFormValid = false;
            }
        } else if (countryValue && !isCityDisabled && !cityValue) {
            // У страны нет регионов: город обязателен, когда селект города активен
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

            const currentRating = parseInt(ratingInput.value) || 0;
            updateRatingStars(currentRating);

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
                const current = parseInt(ratingInput.value) || 0;
                updateRatingStars(current);
            });

            ratingInput.addEventListener('change', validateForm);
            ratingInput.addEventListener('input', validateForm);
        }
    }
    
    // validateForm для страны вызывается из обработчика смены страны (после обновления DOM).
    regionSelect.addEventListener('change', validateForm);
    citySelect.addEventListener('change', validateForm);
    
    // Проверяем форму при загрузке страницы с небольшой задержкой
    // для инициализации Preline (страна, регион, город)
    setTimeout(() => {
        validateForm();
    }, 200);
}
