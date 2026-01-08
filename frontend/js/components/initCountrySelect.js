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
        if (!response.ok) {
            // Пытаемся получить детали ошибки из ответа
            let errorMessage = 'Ошибка загрузки списка стран';
            try {
                const errorData = await response.json();
                if (errorData.detail) {
                    errorMessage = errorData.detail;
                } else if (errorData.message) {
                    errorMessage = errorData.message;
                }
            } catch (e) {
                // Если не удалось распарсить JSON, используем стандартное сообщение
                if (response.status === 401) {
                    errorMessage = 'Требуется авторизация';
                } else if (response.status >= 500) {
                    errorMessage = 'Ошибка сервера. Попробуйте позже';
                }
            }
            throw new Error(errorMessage);
        }
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

        // Убираем disabled и обновляем placeholder
        countrySelect.removeAttribute('disabled');
        
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
        console.error('Ошибка при загрузке списка стран:', error);
        
        // Показываем сообщение об ошибке пользователю, если функция доступна
        if (typeof window.showDangerToast === 'function') {
            const errorMessage = error.message || 'Не удалось загрузить список стран';
            window.showDangerToast('Ошибка загрузки', errorMessage);
        }
        
        // Обновляем placeholder для отображения ошибки
        const dataHsSelect = countrySelect.getAttribute('data-hs-select');
        if (dataHsSelect) {
            try {
                const config = JSON.parse(dataHsSelect);
                config.placeholder = 'Ошибка загрузки';
                countrySelect.setAttribute('data-hs-select', JSON.stringify(config));
            } catch (e) {
                console.error('Ошибка при обновлении конфигурации Preline UI:', e);
            }
        }
        
        // Переинициализируем компонент с обновлённым placeholder
        const hsSelectInstance = window.HSSelect && window.HSSelect.getInstance ? window.HSSelect.getInstance(`#${selectId}`) : null;
        if (hsSelectInstance && typeof hsSelectInstance.destroy === 'function') {
            hsSelectInstance.destroy();
        }
        
        requestAnimationFrame(() => {
            if (window.HSSelect) {
                try {
                    new window.HSSelect(`#${selectId}`);
                } catch (e) {
                    if (window.HSStaticMethods && typeof window.HSStaticMethods.autoInit === 'function') {
                        window.HSStaticMethods.autoInit();
                    }
                }
            }
        });
        
        // Компонент остаётся в disabled состоянии
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
