export async function initCountrySelect({
                                            selectId = 'id_country',
                                            apiUrl = '/api/country/list_by_cities',
                                            redirectBaseUrl = window.location.pathname,
                                            urlParamName = 'country',
                                            showAllOption = true
                                        } = {}) {
    const urlParams = new URLSearchParams(window.location.search);
    const selectedCountryCode = urlParams.get(urlParamName);

    const countrySelect = document.getElementById(selectId);
    if (!countrySelect) return;

    // Убираем класс hidden перед инициализацией Preline UI
    if (countrySelect.classList.contains('hidden')) {
        countrySelect.classList.remove('hidden');
    }

    // Инициализируем Preline UI компонент с disabled состоянием
    requestAnimationFrame(() => {
        if (window.HSStaticMethods && typeof window.HSStaticMethods.autoInit === 'function') {
            window.HSStaticMethods.autoInit();
        }
    });

    try {
        const response = await fetch(apiUrl);
        if (!response.ok) throw new Error('Ошибка загрузки списка стран');
        const countries = await response.json();

        // Очищаем существующие опции
        countrySelect.textContent = '';

        // Добавляем опцию "Все страны" первой, если нужно
        if (showAllOption) {
            const allOption = document.createElement('option');
            allOption.value = 'all';
            allOption.textContent = 'Все страны';
            if (!selectedCountryCode) {
                allOption.selected = true;
            }
            countrySelect.appendChild(allOption);
        }

        let separatorAdded = false;

        // Добавляем опции стран
        countries.forEach((country) => {
            if (!separatorAdded && country.number_of_visited_cities === 0) {
                // Вставляем разделитель перед первой страной с 0 посещённых городов
                const separatorOption = document.createElement('option');
                separatorOption.value = '';
                separatorOption.textContent = 'Непосещённые страны';
                separatorOption.disabled = true;
                countrySelect.appendChild(separatorOption);
                separatorAdded = true;
            }

            const option = document.createElement('option');
            option.value = country.code;
            option.textContent = (country.number_of_visited_cities === undefined || country.number_of_cities === undefined)
                ? country.name
                : `${country.name} (${country.number_of_visited_cities} из ${country.number_of_cities})`;
            if (selectedCountryCode === country.code) {
                option.selected = true;
            }
            countrySelect.appendChild(option);
        });

        // Обновляем placeholder в data-hs-select
        const dataHsSelect = countrySelect.getAttribute('data-hs-select');
        if (dataHsSelect) {
            try {
                const config = JSON.parse(dataHsSelect);
                config.placeholder = showAllOption ? 'Все страны' : 'Выберите страну...';
                countrySelect.setAttribute('data-hs-select', JSON.stringify(config));
            } catch (e) {
                console.error('Ошибка при обновлении конфигурации Preline UI:', e);
            }
        }

        // Если компонент уже был инициализирован, переинициализируем его
        const hsSelectInstance = window.HSSelect && window.HSSelect.getInstance ? window.HSSelect.getInstance(`#${selectId}`) : null;
        if (hsSelectInstance && typeof hsSelectInstance.destroy === 'function') {
            hsSelectInstance.destroy();
        }

        // Убеждаемся, что select не скрыт перед переинициализацией
        if (countrySelect.classList.contains('hidden')) {
            countrySelect.classList.remove('hidden');
        }

        // Переинициализируем компонент с новыми опциями
        // Используем двойной requestAnimationFrame для гарантии, что DOM обновлен
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                if (window.HSSelect) {
                    try {
                        new window.HSSelect(`#${selectId}`);
                    } catch (e) {
                        // Если не получилось, используем autoInit
                        if (window.HSStaticMethods && typeof window.HSStaticMethods.autoInit === 'function') {
                            window.HSStaticMethods.autoInit();
                        }
                    }
                }
            });
        });
    } catch (error) {
        console.error(error);
        countrySelect.textContent = '';
        const errorOption = document.createElement('option');
        errorOption.value = '';
        errorOption.textContent = 'Ошибка загрузки';
        errorOption.disabled = true;
        countrySelect.appendChild(errorOption);
    }

    // Обработка выбора
    countrySelect.addEventListener('change', (event) => {
        const selectedValue = event.target.value;
        
        // Обновляем состояние кнопки "Показать непосещённые города" перед редиректом
        if (typeof window.updateNotVisitedCitiesButtonState === 'function') {
            window.updateNotVisitedCitiesButtonState();
        }
        
        const query = new URLSearchParams(window.location.search);
        // Если выбрано "all", удаляем параметр country из URL
        if (selectedValue && selectedValue !== 'all') {
            query.set(urlParamName, selectedValue);
        } else {
            query.delete(urlParamName);
        }

        window.location.href = `${redirectBaseUrl}?${query.toString()}`;
    });
}
