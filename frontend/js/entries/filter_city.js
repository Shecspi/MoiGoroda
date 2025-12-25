// Управление панелью фильтрации
document.addEventListener('DOMContentLoaded', function () {
    const openBtn = document.getElementById('btnOpenFilterSortPanel');
    const offcanvas = document.getElementById('offcanvasRight');
    const backdrop = document.querySelector('[data-hs-overlay-backdrop="#offcanvasRight"]');
    const closeBtn = offcanvas?.querySelector('[data-hs-overlay="#offcanvasRight"]');

    function openOffcanvas() {
        if (offcanvas && backdrop) {
            offcanvas.classList.remove('translate-x-full');
            offcanvas.classList.add('translate-x-0');
            backdrop.classList.remove('opacity-0', 'pointer-events-none');
            backdrop.classList.add('opacity-100', 'pointer-events-auto');
            document.body.style.overflow = 'hidden';
        }
    }

    function closeOffcanvas() {
        if (offcanvas && backdrop) {
            offcanvas.classList.remove('translate-x-0');
            offcanvas.classList.add('translate-x-full');
            backdrop.classList.remove('opacity-100', 'pointer-events-auto');
            backdrop.classList.add('opacity-0', 'pointer-events-none');
            document.body.style.overflow = '';
        }
    }

    if (openBtn) {
        openBtn.addEventListener('click', function(e) {
            e.preventDefault();
            openOffcanvas();
        });
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', function(e) {
            e.preventDefault();
            closeOffcanvas();
        });
    }

    if (backdrop) {
        backdrop.addEventListener('click', function() {
            closeOffcanvas();
        });
    }

    // Закрытие по Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && offcanvas?.classList.contains('translate-x-0')) {
            closeOffcanvas();
        }
    });
});

// Управление переключателями фильтров
document.addEventListener('DOMContentLoaded', function () {
    const filterSwitches = document.querySelectorAll('.filter-switch');
    const offcanvas = document.getElementById('offcanvasRight');
    let defaultFilter = offcanvas?.dataset.defaultFilter || '';
    const saveFilterDefaultSwitch = document.getElementById('saveFilterDefault');
    
    // Функция для проверки совпадения фильтра с дефолтным и управления switch'ем
    function checkAndUpdateFilterSwitch(filterValue) {
        if (saveFilterDefaultSwitch && defaultFilter && filterValue === defaultFilter) {
            saveFilterDefaultSwitch.checked = true;
        } else if (saveFilterDefaultSwitch) {
            saveFilterDefaultSwitch.checked = false;
        }
    }
    
    // Функция для обновления звездочек фильтров
    function updateFilterStars() {
        // Удаляем все существующие звездочки фильтров
        document.querySelectorAll('[data-default-star^="filter-"]').forEach(star => {
            star.remove();
        });
        
        // Добавляем звездочку для текущего значения по умолчанию
        if (defaultFilter) {
            // Находим соответствующий switch и добавляем звездочку
            const filterSwitch = document.querySelector(`.filter-switch[value="${defaultFilter}"]`);
            if (filterSwitch) {
                const label = document.querySelector(`label[for="${filterSwitch.id}"]`);
                if (label) {
                    const star = document.createElement('span');
                    star.className = 'text-red-600 dark:text-red-500';
                    star.setAttribute('data-default-star', `filter-${defaultFilter}`);
                    star.textContent = '*';
                    label.appendChild(star);
                }
            }
        }
    }
    
    // Функция для обновления значения defaultFilter
    function updateDefaultFilter(newValue) {
        defaultFilter = newValue || '';
        // Обновляем звездочки
        updateFilterStars();
        // После обновления проверяем текущий выбранный фильтр
        const selectedFilter = document.querySelector('.filter-switch:checked')?.value;
        if (selectedFilter) {
            checkAndUpdateFilterSwitch(selectedFilter);
        }
    }
    
    // Экспортируем функцию для использования в других обработчиках
    window.updateDefaultFilter = updateDefaultFilter;
    
    // Инициализация звездочек при загрузке страницы
    updateFilterStars();
    
    // Функция для отключения всех переключателей фильтров кроме указанного
    function disableAllFilterSwitchesExcept(activeSwitch) {
        filterSwitches.forEach(switchEl => {
            if (switchEl !== activeSwitch) {
                switchEl.checked = false;
            }
        });
    }
    
    // Функция для обновления скрытой радиокнопки filter на основе переключателя
    function updateFilterRadio() {
        const selectedFilter = document.querySelector('.filter-switch:checked')?.value;
        
        if (selectedFilter) {
            // Отключаем все скрытые радиокнопки
            document.querySelectorAll('input[name="filter"].filter-radio').forEach(radio => {
                radio.checked = false;
            });
            
            // Включаем нужную радиокнопку
            const filterRadio = document.querySelector(`input[name="filter"].filter-radio[value="${selectedFilter}"]`);
            if (filterRadio) {
                filterRadio.checked = true;
            }
            
            // Проверяем совпадение с дефолтным значением
            checkAndUpdateFilterSwitch(selectedFilter);
        }
    }
    
    // Обработка изменения фильтров (переключатели работают как радиокнопки)
    filterSwitches.forEach(switchEl => {
        switchEl.addEventListener('change', function() {
            if (this.checked) {
                // Отключаем все остальные переключатели
                disableAllFilterSwitchesExcept(this);
                // Обновляем скрытую радиокнопку
                updateFilterRadio();
            } else {
                // Если пытаются отключить последний переключатель, не даем этого сделать
                const checkedSwitches = document.querySelectorAll('.filter-switch:checked');
                if (checkedSwitches.length === 0) {
                    this.checked = true;
                }
            }
        });
    });
    
    // Инициализация: если ни один фильтр не выбран, выбираем по умолчанию
    const checkedFilter = document.querySelector('.filter-switch:checked');
    if (!checkedFilter) {
        const defaultFilterSwitch = document.querySelector('.filter-switch[value="no_filter"]');
        if (defaultFilterSwitch) {
            defaultFilterSwitch.checked = true;
            disableAllFilterSwitchesExcept(defaultFilterSwitch);
        }
    } else {
        // Убеждаемся, что только один переключатель включен
        disableAllFilterSwitchesExcept(checkedFilter);
    }
    
    // Инициализация скрытых радиокнопок и проверка совпадения с дефолтным значением
    updateFilterRadio();
});

// Управление выбором типа и направления сортировки
document.addEventListener('DOMContentLoaded', function () {
    const sortTypeSwitches = document.querySelectorAll('.sort-type-switch');
    const sortDirectionSwitch = document.querySelector('.sort-direction-switch');
    const offcanvas = document.getElementById('offcanvasRight');
    let defaultSort = offcanvas?.dataset.defaultSort || '';
    const saveSortDefaultSwitch = document.getElementById('saveSortDefault');
    
    // Функция для проверки совпадения сортировки с дефолтной и управления switch'ем
    function checkAndUpdateSortSwitch() {
        const selectedType = document.querySelector('.sort-type-switch:checked')?.value;
        const selectedDirection = sortDirectionSwitch?.checked ? 'up' : 'down';
        
        if (selectedType && selectedDirection) {
            const sortValue = `${selectedType}_${selectedDirection}`;
            if (saveSortDefaultSwitch && defaultSort && sortValue === defaultSort) {
                saveSortDefaultSwitch.checked = true;
            } else if (saveSortDefaultSwitch) {
                saveSortDefaultSwitch.checked = false;
            }
        }
    }
    
    // Функция для обновления звездочек типов сортировки
    function updateSortStars() {
        // Удаляем все существующие звездочки сортировки
        document.querySelectorAll('[data-default-star^="sort-"]').forEach(star => {
            star.remove();
        });
        
        // Добавляем звездочку для текущего значения по умолчанию
        if (defaultSort) {
            // Определяем тип сортировки из значения (например, name_down -> name)
            // Удаляем суффикс _down или _up
            let sortType = defaultSort;
            if (defaultSort.endsWith('_down')) {
                sortType = defaultSort.slice(0, -5); // Удаляем '_down'
            } else if (defaultSort.endsWith('_up')) {
                sortType = defaultSort.slice(0, -3); // Удаляем '_up'
            }
            
            if (sortType) {
                // Находим соответствующий switch и добавляем звездочку
                const sortSwitch = document.querySelector(`.sort-type-switch[value="${sortType}"]`);
                if (sortSwitch) {
                    const label = document.querySelector(`label[for="${sortSwitch.id}"]`);
                    if (label) {
                        const star = document.createElement('span');
                        star.className = 'text-red-600 dark:text-red-500';
                        star.setAttribute('data-default-star', `sort-${sortType}`);
                        star.textContent = '*';
                        label.appendChild(star);
                    }
                }
            }
        }
    }
    
    // Функция для обновления значения defaultSort
    function updateDefaultSort(newValue) {
        defaultSort = newValue || '';
        // Обновляем звездочки
        updateSortStars();
        // После обновления проверяем текущую выбранную сортировку
        checkAndUpdateSortSwitch();
    }
    
    // Экспортируем функцию для использования в других обработчиках
    window.updateDefaultSort = updateDefaultSort;
    
    // Инициализация звездочек при загрузке страницы
    updateSortStars();
    
    // Функция для отключения всех переключателей типа кроме указанного
    function disableAllTypeSwitchesExcept(activeSwitch) {
        sortTypeSwitches.forEach(switchEl => {
            if (switchEl !== activeSwitch) {
                switchEl.checked = false;
            }
        });
    }
    
    // Функция для обновления скрытой радиокнопки sort на основе типа и направления
    function updateSortRadio() {
        const selectedType = document.querySelector('.sort-type-switch:checked')?.value;
        // Переключатель: unchecked = down, checked = up
        const selectedDirection = sortDirectionSwitch?.checked ? 'up' : 'down';
        
        if (selectedType && selectedDirection) {
            // Отключаем все скрытые радиокнопки
            document.querySelectorAll('input[name="sort"].sort-radio').forEach(radio => {
                radio.checked = false;
            });
            
            // Включаем нужную радиокнопку
            const sortValue = `${selectedType}_${selectedDirection}`;
            const sortRadio = document.querySelector(`input[name="sort"].sort-radio[value="${sortValue}"]`);
            if (sortRadio) {
                sortRadio.checked = true;
            }
            
            // Проверяем совпадение с дефолтным значением
            checkAndUpdateSortSwitch();
        }
    }
    
    // Обработка изменения типа сортировки (переключатели работают как радиокнопки)
    sortTypeSwitches.forEach(switchEl => {
        switchEl.addEventListener('change', function() {
            if (this.checked) {
                // Отключаем все остальные переключатели
                disableAllTypeSwitchesExcept(this);
                // Обновляем скрытую радиокнопку
                updateSortRadio();
            } else {
                // Если пытаются отключить последний переключатель, не даем этого сделать
                const checkedSwitches = document.querySelectorAll('.sort-type-switch:checked');
                if (checkedSwitches.length === 0) {
                    this.checked = true;
                }
            }
        });
    });
    
    // Обработка изменения направления сортировки (переключатель)
    if (sortDirectionSwitch) {
        sortDirectionSwitch.addEventListener('change', function() {
            updateSortRadio();
        });
    }
    
    // Инициализация: если ни один тип не выбран, выбираем по умолчанию
    const checkedType = document.querySelector('.sort-type-switch:checked');
    if (!checkedType) {
        const defaultTypeSwitch = document.querySelector('.sort-type-switch[value="last_visit_date"]');
        if (defaultTypeSwitch) {
            defaultTypeSwitch.checked = true;
            disableAllTypeSwitchesExcept(defaultTypeSwitch);
        }
    } else {
        // Убеждаемся, что только один переключатель включен
        disableAllTypeSwitchesExcept(checkedType);
    }
    
    // Инициализация скрытых радиокнопок и проверка совпадения с дефолтным значением
    updateSortRadio();
});

// Нажатие кнопки "Сбросить фильтры и сортировку"
document.addEventListener('DOMContentLoaded', function () {
    const resetBtn = document.getElementById('resetFilters');

    if (resetBtn) {
        resetBtn.addEventListener('click', function () {
            const filter = this.dataset.filter;
            const sort = this.dataset.sort;

            // Сброс фильтра
            if (filter) {
                const filterInput = document.querySelector(`input[name="filter"].filter-radio[value="${filter}"]`);
                if (filterInput) filterInput.checked = true;
                
                // Отключаем все переключатели фильтров
                document.querySelectorAll('.filter-switch').forEach(switchEl => {
                    switchEl.checked = false;
                });
                
                // Устанавливаем переключатель фильтра
                const filterSwitch = document.querySelector(`.filter-switch[value="${filter}"]`);
                if (filterSwitch) {
                    filterSwitch.checked = true;
                }
            }

            // Сброс сортировки
            if (sort) {
                const sortInput = document.querySelector(`input[name="sort"][value="${sort}"]`);
                if (sortInput) sortInput.checked = true;
                
                // Определяем тип и направление из значения sort
                const sortParts = sort.split('_');
                const direction = sortParts.pop(); // 'down' или 'up'
                const type = sortParts.join('_'); // остальное
                
                // Отключаем все переключатели типа
                document.querySelectorAll('.sort-type-switch').forEach(switchEl => {
                    switchEl.checked = false;
                });
                
                // Устанавливаем тип сортировки
                const typeSwitch = document.querySelector(`.sort-type-switch[value="${type}"]`);
                if (typeSwitch) {
                    typeSwitch.checked = true;
                }
                
                // Устанавливаем направление (переключатель: unchecked = down, checked = up)
                const directionSwitch = document.querySelector('.sort-direction-switch');
                if (directionSwitch) {
                    directionSwitch.checked = (direction === 'up');
                }
            }
        });
    }
});

// Нажатие кнопки "Применить фильтры и сортировку"
document.addEventListener('DOMContentLoaded', function () {
    const applyBtn = document.getElementById('applyFilters');
    
    if (applyBtn) {
        applyBtn.addEventListener('click', function () {
            const urlParams = new URLSearchParams(window.location.search);
            const selectedCountryCode = urlParams.get('country');

            // Обновляем скрытые радиокнопки перед чтением значений,
            // чтобы убедиться, что они синхронизированы с переключателями
            const selectedFilter = document.querySelector('.filter-switch:checked')?.value;
            if (selectedFilter) {
                document.querySelectorAll('input[name="filter"].filter-radio').forEach(radio => {
                    radio.checked = false;
                });
                const filterRadio = document.querySelector(`input[name="filter"].filter-radio[value="${selectedFilter}"]`);
                if (filterRadio) {
                    filterRadio.checked = true;
                }
            }

            const selectedType = document.querySelector('.sort-type-switch:checked')?.value;
            const sortDirectionSwitch = document.querySelector('.sort-direction-switch');
            const selectedDirection = sortDirectionSwitch?.checked ? 'up' : 'down';
            if (selectedType && selectedDirection) {
                document.querySelectorAll('input[name="sort"].sort-radio').forEach(radio => {
                    radio.checked = false;
                });
                const sortValue = `${selectedType}_${selectedDirection}`;
                const sortRadio = document.querySelector(`input[name="sort"].sort-radio[value="${sortValue}"]`);
                if (sortRadio) {
                    sortRadio.checked = true;
                }
            }

            const filter = document.querySelector('input[name="filter"].filter-radio:checked')?.value || '';
            const sort = document.querySelector('input[name="sort"].sort-radio:checked')?.value || '';

            const params = new URLSearchParams();

            // Всегда отправляем текущие значения фильтра и сортировки,
            // чтобы они не сбрасывались при изменении только одного параметра
            if (filter) params.set('filter', filter);
            if (sort) params.set('sort', sort);
            if (selectedCountryCode) params.set('country', selectedCountryCode);

            window.location.href = `${window.location.pathname}?${params.toString()}`;
        });
    }
});

// Обработка переключения switch'а "Сохранить фильтр по умолчанию"
document.addEventListener('DOMContentLoaded', function () {
    const saveFilterDefaultSwitch = document.getElementById('saveFilterDefault');
    
    if (saveFilterDefaultSwitch) {
        saveFilterDefaultSwitch.addEventListener('change', function() {
            if (this.checked) {
                // Получаем текущий выбранный фильтр
                const selectedFilter = document.querySelector('.filter-switch:checked')?.value;
                
                if (selectedFilter) {
                    // Сохраняем настройки фильтрации по умолчанию
                    fetch('/api/city/list/default_settings', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken'),
                        },
                        body: JSON.stringify({
                            parameter_type: 'filter',
                            parameter_value: selectedFilter,
                        }),
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            console.log('Настройки фильтрации сохранены:', data);
                            // Обновляем актуальное значение defaultFilter
                            if (window.updateDefaultFilter) {
                                window.updateDefaultFilter(selectedFilter);
                            }
                        }
                    })
                    .catch(error => {
                        console.error('Ошибка при сохранении настроек фильтрации:', error);
                    });
                }
            } else {
                // Удаляем настройки фильтрации по умолчанию
                fetch('/api/city/list/default_settings/delete', {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: JSON.stringify({
                        parameter_type: 'filter',
                    }),
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        console.log('Настройки фильтрации удалены:', data);
                        // Очищаем актуальное значение defaultFilter
                        if (window.updateDefaultFilter) {
                            window.updateDefaultFilter('');
                        }
                    }
                })
                .catch(error => {
                    console.error('Ошибка при удалении настроек фильтрации:', error);
                });
            }
        });
    }
});

// Обработка переключения switch'а "Сохранить сортировку по умолчанию"
document.addEventListener('DOMContentLoaded', function () {
    const saveSortDefaultSwitch = document.getElementById('saveSortDefault');
    const sortTypeSwitches = document.querySelectorAll('.sort-type-switch');
    const sortDirectionSwitch = document.querySelector('.sort-direction-switch');
    
    if (saveSortDefaultSwitch) {
        saveSortDefaultSwitch.addEventListener('change', function() {
            if (this.checked) {
                // Получаем текущую выбранную сортировку
                const selectedType = document.querySelector('.sort-type-switch:checked')?.value;
                const selectedDirection = sortDirectionSwitch?.checked ? 'up' : 'down';
                
                if (selectedType && selectedDirection) {
                    const sortValue = `${selectedType}_${selectedDirection}`;
                    
                    // Сохраняем настройки сортировки по умолчанию
                    fetch('/api/city/list/default_settings', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken'),
                        },
                        body: JSON.stringify({
                            parameter_type: 'sort',
                            parameter_value: sortValue,
                        }),
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            console.log('Настройки сортировки сохранены:', data);
                            // Обновляем актуальное значение defaultSort
                            if (window.updateDefaultSort) {
                                window.updateDefaultSort(sortValue);
                            }
                        }
                    })
                    .catch(error => {
                        console.error('Ошибка при сохранении настроек сортировки:', error);
                    });
                }
            } else {
                // Удаляем настройки сортировки по умолчанию
                fetch('/api/city/list/default_settings/delete', {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: JSON.stringify({
                        parameter_type: 'sort',
                    }),
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        console.log('Настройки сортировки удалены:', data);
                        // Очищаем актуальное значение defaultSort
                        if (window.updateDefaultSort) {
                            window.updateDefaultSort('');
                        }
                    }
                })
                .catch(error => {
                    console.error('Ошибка при удалении настроек сортировки:', error);
                });
            }
        });
    }
});

// Функция для получения CSRF токена из cookies
function getCookie(c_name) {
    if (document.cookie.length > 0) {
        let c_start = document.cookie.indexOf(c_name + "=");
        if (c_start != -1) {
            c_start = c_start + c_name.length + 1;
            let c_end = document.cookie.indexOf(";", c_start);
            if (c_end == -1) c_end = document.cookie.length;
            return unescape(document.cookie.substring(c_start, c_end));
        }
    }
    return "";
}