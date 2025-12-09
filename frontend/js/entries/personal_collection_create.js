import L from 'leaflet';
import {create_map} from '../components/map.js';
import {icon_visited_pin, icon_not_visited_pin, icon_blue_pin} from '../components/icons.js';
import {buildPopupContent} from '../components/city_popup.js';
import {showDangerToast, showSuccessToast} from "../components/toast";
import {getCookie} from '../components/get_cookie.js';

window.addEventListener('load', () => requestAnimationFrame(async () => {
    (function() {
        // Проверяем, находимся ли мы в режиме редактирования
        const isEditMode = window.COLLECTION_ID !== null && window.COLLECTION_ID !== undefined;
        
        // Получаем экземпляры Preline Select (они уже инициализированы автоматически через data-hs-select)
        const countrySelect = window.HSSelect.getInstance('#country_select');
        const countrySelectElement = document.getElementById('country_select');
        const regionSelect = window.HSSelect.getInstance('#region_select');
        const regionSelectElement = document.getElementById('region_select');
        const loadCitiesButton = document.getElementById('load_cities_button');
        const saveCollectionButton = document.getElementById('save_collection_button');
        
        if (!countrySelect || !countrySelectElement || !regionSelect || !regionSelectElement || !loadCitiesButton) {
            console.error('Не найдены необходимые элементы формы', {
                countrySelect: !!countrySelect,
                countrySelectElement: !!countrySelectElement,
                regionSelect: !!regionSelect,
                regionSelectElement: !!regionSelectElement,
                loadCitiesButton: !!loadCitiesButton
            });
            return;
        }

        // Изначально отключаем регионы
        regionSelectElement.disabled = true;
        
        // Храним информацию о странах без регионов
        const countriesWithoutRegions = new Set();
        // Храним информацию о странах с регионами
        const countriesWithRegions = new Set();
        
        // Функция для обновления состояния кнопки загрузки городов
        const updateLoadCitiesButton = () => {
            const selectedOptions = Array.from(regionSelectElement.selectedOptions);
            const selectedRegionIds = selectedOptions
                .map(option => option.value)
                .filter(value => value !== '');
            
            // Получаем выбранные страны
            const selectedCountryOptions = Array.from(countrySelectElement.selectedOptions);
            const selectedCountryIds = selectedCountryOptions
                .map(option => option.value)
                .filter(value => value !== '');
            
            // Кнопка активна, если выбраны страны (независимо от наличия регионов)
            if (selectedCountryIds.length > 0) {
                loadCitiesButton.disabled = false;
            } else {
                loadCitiesButton.disabled = true;
            }
        };

        // Загружаем страны и добавляем опции через метод addOption
        (async () => {
            try {
                const response = await fetch('/api/city/country/list_by_cities');
                if (response.ok) {
                    const countries = await response.json();
                    
                    if (countries.length > 0) {
                        // Добавляем опции через метод addOption Preline Select
                        const optionsToAdd = countries.map((country) => ({
                            title: country.name,
                            val: country.id.toString(),
                        }));
                        
                        countrySelect.addOption(optionsToAdd);
                    }
                }
            } catch (error) {
                console.error('Ошибка при загрузке стран:', error);
            }
        })();

        // Обработчик изменения выбора стран
        countrySelectElement.addEventListener('change', async (event) => {
            // Получаем все выбранные страны
            const selectedOptions = Array.from(event.target.selectedOptions);
            const selectedCountryIds = selectedOptions
                .map(option => option.value)
                .filter(value => value !== '');

            if (selectedCountryIds.length === 0) {
                // Очистить регионы, если страны не выбраны
                // Удаляем все опции кроме placeholder
                const regionOptions = regionSelectElement.querySelectorAll('option:not([value=""])');
                regionOptions.forEach(option => option.remove());
                regionSelectElement.disabled = true;
                countriesWithoutRegions.clear();
                updateLoadCitiesButton();
                return;
            }

            // Включаем регионы
            regionSelectElement.disabled = false;

            try {
                // Загрузка регионов для выбранных стран
                const countryIdsParam = selectedCountryIds.join(',');
                const response = await fetch(`/api/region/list?country_ids=${countryIdsParam}`);
                
                if (!response.ok) {
                    throw new Error('Ошибка загрузки регионов');
                }

                const regions = await response.json();

                // Удаляем все существующие опции кроме placeholder
                const existingOptions = regionSelectElement.querySelectorAll('option:not([value=""])');
                existingOptions.forEach(option => option.remove());

                // Определяем, какие страны имеют регионы
                const countriesWithRegionsInResponse = new Set();
                regions.forEach(region => {
                    if (region.country_id) {
                        countriesWithRegionsInResponse.add(region.country_id.toString());
                    }
                });

                // Обновляем множества стран с регионами и без регионов
                countriesWithRegions.clear();
                countriesWithoutRegions.clear();
                selectedCountryIds.forEach(countryId => {
                    if (countriesWithRegionsInResponse.has(countryId)) {
                        countriesWithRegions.add(countryId);
                    } else {
                        countriesWithoutRegions.add(countryId);
                    }
                });

                if (regions.length === 0) {
                    regionSelectElement.disabled = true;
                    // Не показываем toast, так как это нормальная ситуация для стран без регионов
                    updateLoadCitiesButton();
                    return;
                }

                // Добавляем регионы через метод addOption Preline Select
                // Формируем полное название с названием страны для отображения
                const optionsToAdd = regions.map((region) => ({
                    title: `${region.title}, ${region.country_name}`,
                    val: region.id.toString(),
                }));
                
                regionSelect.addOption(optionsToAdd);
                updateLoadCitiesButton();
            } catch (error) {
                console.error('Ошибка при загрузке регионов:', error);
                showDangerToast('Ошибка', 'Не удалось загрузить регионы');
                regionSelectElement.disabled = true;
                countriesWithoutRegions.clear();
                updateLoadCitiesButton();
            }
        });
        
        // Обработчик изменения выбора регионов
        regionSelectElement.addEventListener('change', () => {
            updateLoadCitiesButton();
        });
        
        // Инициализация пустой карты
        const map = create_map();
        window.MG_MAIN_MAP = map;
        // Устанавливаем центр карты на Россию
        map.setView([55.7522, 37.6156], 6);
        
        // Массив для хранения всех маркеров
        const allMarkers = [];
        
        // Массив для хранения выбранных городов для коллекции
        const selectedCities = [];
        
        // Предзаполнение формы при редактировании
        if (isEditMode) {
            // Предзаполняем название коллекции
            const collectionNameInput = document.getElementById('collection_name');
            if (collectionNameInput && window.COLLECTION_TITLE) {
                collectionNameInput.value = window.COLLECTION_TITLE;
            }
            
            // Предзаполняем switch для публичной коллекции
            const isPublicSwitch = document.getElementById('is_public_switch');
            if (isPublicSwitch && window.COLLECTION_IS_PUBLIC !== undefined) {
                isPublicSwitch.checked = window.COLLECTION_IS_PUBLIC;
            }
            
            // Предзаполняем selectedCities и загружаем города на карту
            if (window.COLLECTION_CITY_IDS && Array.isArray(window.COLLECTION_CITY_IDS) && window.COLLECTION_CITY_IDS.length > 0) {
                // Загружаем города по их ID
                (async () => {
                    try {
                        // Загружаем города через API
                        const cityIdsParam = window.COLLECTION_CITY_IDS.join(',');
                        const response = await fetch(`/api/city/list_by_ids?city_ids=${cityIdsParam}`);
                        
                        if (!response.ok) {
                            throw new Error('Ошибка загрузки городов коллекции');
                        }
                        
                        const cities = await response.json();
                        
                        // Добавляем города в selectedCities
                        cities.forEach(city => {
                            selectedCities.push({
                                id: city.id,
                                name: city.title
                            });
                        });
                        
                        // Получаем базовые URL для ссылок
                        const countryCitiesBaseUrl = window.COUNTRY_CITIES_BASE_URL || '';
                        const isAuthenticated = typeof window.IS_AUTHENTICATED !== 'undefined' && window.IS_AUTHENTICATED === true;
                        
                        // Отображаем города на карте
                        cities.forEach(city => {
                            const lat = parseFloat(city.lat.toString().replace(',', '.'));
                            const lon = parseFloat(city.lon.toString().replace(',', '.'));
                            
                            if (isNaN(lat) || isNaN(lon)) {
                                return;
                            }
                            
                            // Формируем данные города для попапа
                            const cityData = {
                                id: city.id,
                                name: city.title,
                                isVisited: city.isVisited || false,
                                firstVisitDate: city.firstVisitDate || null,
                                lastVisitDate: city.lastVisitDate || null,
                                numberOfVisits: city.numberOfVisits || 0,
                                // Явно устанавливаем null, чтобы не показывать информацию о количестве пользователей
                                numberOfUsersWhoVisitCity: null,
                                numberOfVisitsAllUsers: null
                            };
                            
                            // Формируем ссылки на регион и страну
                            const regionName = city.region || '';
                            const countryName = city.country || '';
                            const regionId = city.regionId || null;
                            const countryCode = city.countryCode || null;
                            
                            let regionLink = '';
                            let countryLink = '';
                            
                            if (regionId && countryCitiesBaseUrl) {
                                regionLink = `${countryCitiesBaseUrl}?region_id=${regionId}`;
                            }
                            
                            if (countryCode && countryCitiesBaseUrl) {
                                countryLink = `${countryCitiesBaseUrl}?country_code=${countryCode}`;
                            }
                            
                            const marker = L.marker([lat, lon], {
                                icon: icon_blue_pin
                            });
                            
                            marker._cityId = cityData.id;
                            marker._cityData = cityData;
                            
                            // Функция для обновления содержимого попапа с проверкой актуального состояния коллекции
                            const updatePopupContent = () => {
                                // Проверяем актуальное состояние коллекции
                                const isInCollection = selectedCities.some(selectedCity => selectedCity.id === cityData.id);
                                return buildPopupContent(cityData, {
                                    regionName: regionName,
                                    countryName: countryName,
                                    regionLink: regionLink,
                                    countryLink: countryLink,
                                    isAuthenticated: isAuthenticated,
                                    isCollectionOwner: true,
                                    collectionOwnerUsername: null,
                                    addButtonText: isInCollection ? 'Удалить из коллекции' : 'Добавить в коллекцию'
                                });
                            };
                            
                            // Сохраняем функцию обновления в маркере для последующего использования
                            marker._updatePopupContent = updatePopupContent;
                            
                            marker.bindPopup(updatePopupContent, {maxWidth: 400, minWidth: 280});
                            
                            marker.on('popupopen', () => {
                                marker.setPopupContent(updatePopupContent());
                                if (window.HSStaticMethods && typeof window.HSStaticMethods.autoInit === 'function') {
                                    window.HSStaticMethods.autoInit();
                                }
                            });
                            
                            marker.bindTooltip(cityData.name, {direction: 'top'});
                            marker.on('mouseover', function () {
                                const tooltip = this.getTooltip();
                                if (this.isPopupOpen()) {
                                    tooltip.setOpacity(0.0);
                                } else {
                                    tooltip.setOpacity(0.9);
                                }
                            });
                            marker.on('click', function () {
                                this.getTooltip().setOpacity(0.0);
                            });
                            
                            marker.addTo(map);
                            allMarkers.push(marker);
                        });
                        
                        // Центрируем и масштабируем карту по маркерам
                        if (allMarkers.length > 0) {
                            const group = new L.featureGroup([...allMarkers]);
                            map.fitBounds(group.getBounds());
                        }
                    } catch (error) {
                        console.error('Ошибка при загрузке городов коллекции:', error);
                        showDangerToast('Ошибка', 'Не удалось загрузить города коллекции');
                    }
                })();
            }
        }
        
        // Функция для обновления иконки маркера в зависимости от статуса в коллекции
        const updateMarkerIcon = (marker, cityData) => {
            const isInCollection = selectedCities.some(city => city.id === cityData.id);
            
            if (isInCollection) {
                // Если город в коллекции - используем синюю иконку
                marker.setIcon(icon_blue_pin);
            } else {
                // Если город не в коллекции - используем стандартную иконку в зависимости от статуса посещения
                const icon = cityData.isVisited ? icon_visited_pin : icon_not_visited_pin;
                marker.setIcon(icon);
            }
        };
        
        // Обработчик клика на кнопку "Добавить в коллекцию" / "Удалить из коллекции" в попапах
        // Используем делегирование событий для обработки динамически созданных элементов
        // Добавляем обработчик один раз, вне обработчика загрузки городов
        document.addEventListener('click', (event) => {
            const button = event.target.closest('a[data-hs-overlay="#addCityModal"][data-city-id]');
            if (button && (button.textContent.trim() === 'Добавить в коллекцию' || button.textContent.trim() === 'Удалить из коллекции')) {
                event.preventDefault();
                event.stopPropagation();
                
                const cityId = parseInt(button.getAttribute('data-city-id'), 10);
                const cityName = button.getAttribute('data-city-name');
                
                if (!cityId || !cityName) {
                    return;
                }
                
                // Проверяем, есть ли город уже в массиве
                const existingIndex = selectedCities.findIndex(city => city.id === cityId);
                
                if (existingIndex !== -1) {
                    // Удаляем город из массива, если он уже есть
                    selectedCities.splice(existingIndex, 1);
                } else {
                    // Добавляем город в массив
                    selectedCities.push({
                        id: cityId,
                        name: cityName
                    });
                }
                
                // Обновляем текст кнопки в попапе
                const isInCollection = selectedCities.some(city => city.id === cityId);
                button.textContent = isInCollection ? 'Удалить из коллекции' : 'Добавить в коллекцию';
                
                // Находим маркер для этого города и обновляем его иконку
                const marker = allMarkers.find(m => m._cityId === cityId);
                if (marker && marker._cityData) {
                    updateMarkerIcon(marker, marker._cityData);
                }
                
                // Обновляем содержимое попапа, если он открыт
                if (window.MG_MAIN_MAP) {
                    const openPopup = window.MG_MAIN_MAP._popup;
                    if (openPopup && openPopup._source) {
                        const popupMarker = openPopup._source;
                        // Находим соответствующий маркер и обновляем его попап
                        const markerCityId = popupMarker._cityId;
                        if (markerCityId === cityId && popupMarker._updatePopupContent) {
                            // Обновляем содержимое попапа
                            popupMarker.setPopupContent(popupMarker._updatePopupContent());
                        }
                    }
                }
            }
        });
        
        // Обработчик клика на кнопку "Загрузить города"
        loadCitiesButton.addEventListener('click', async () => {
            const selectedOptions = Array.from(regionSelectElement.selectedOptions);
            const selectedRegionIds = selectedOptions
                .map(option => option.value)
                .filter(value => value !== '');
            
            // Получаем выбранные страны
            const selectedCountryOptions = Array.from(countrySelectElement.selectedOptions);
            const selectedCountryIds = selectedCountryOptions
                .map(option => option.value)
                .filter(value => value !== '');
            
            if (selectedCountryIds.length === 0) {
                showDangerToast('Ошибка', 'Не выбраны страны');
                return;
            }
            
            // Отключаем кнопку на время загрузки
            loadCitiesButton.disabled = true;
            const originalText = loadCitiesButton.innerHTML;
            loadCitiesButton.innerHTML = '<span class="inline-block animate-spin rounded-full border-2 border-solid border-current border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]"></span> Загрузка...';
            
            try {
                // Формируем параметры запроса
                const params = new URLSearchParams();
                
                // Если выбраны регионы - загружаем по регионам
                if (selectedRegionIds.length > 0) {
                    params.append('region_ids', selectedRegionIds.join(','));
                }
                
                // Определяем, какие страны нужно загрузить:
                // 1. Страны без регионов - всегда загружаем
                // 2. Страны с регионами, но регионы не выбраны - загружаем все города этих стран
                const selectedCountriesWithoutRegions = selectedCountryIds.filter(countryId => 
                    countriesWithoutRegions.has(countryId)
                );
                
                // Для стран с регионами: если регионы не выбраны вообще, загружаем все города этих стран
                // Если регионы выбраны, не загружаем города по странам (только по регионам)
                const selectedCountriesWithRegionsButNoRegionsSelected = selectedCountryIds.filter(countryId => {
                    // Страна с регионами, но регионы не выбраны вообще
                    return countriesWithRegions.has(countryId) && 
                           selectedRegionIds.length === 0;
                });
                
                // Объединяем страны для загрузки
                const countriesToLoad = [
                    ...selectedCountriesWithoutRegions,
                    ...selectedCountriesWithRegionsButNoRegionsSelected
                ];
                
                if (countriesToLoad.length > 0) {
                    params.append('country_ids', countriesToLoad.join(','));
                }
                
                const response = await fetch(`/api/city/list_by_regions?${params.toString()}`);
                
                if (!response.ok) {
                    throw new Error('Ошибка загрузки городов');
                }
                
                const cities = await response.json();
                
                if (cities.length === 0) {
                    showDangerToast('Информация', 'Для выбранных регионов нет городов');
                    loadCitiesButton.disabled = false;
                    loadCitiesButton.innerHTML = originalText;
                    return;
                }
                
                // Удаляем только маркеры городов, которые НЕ в коллекции
                // Маркеры городов из коллекции должны оставаться на карте
                const collectionCityIds = new Set(selectedCities.map(city => city.id));
                const markersToRemove = [];
                const markersToKeep = [];
                
                allMarkers.forEach(marker => {
                    if (marker._cityId && collectionCityIds.has(marker._cityId)) {
                        // Маркер города из коллекции - оставляем
                        markersToKeep.push(marker);
                    } else {
                        // Маркер города не из коллекции - удаляем
                        markersToRemove.push(marker);
                    }
                });
                
                // Удаляем маркеры, которые не в коллекции
                markersToRemove.forEach(marker => {
                    map.removeLayer(marker);
                    const index = allMarkers.indexOf(marker);
                    if (index > -1) {
                        allMarkers.splice(index, 1);
                    }
                });
                
                // Получаем базовые URL для ссылок
                const countryCitiesBaseUrl = window.COUNTRY_CITIES_BASE_URL || '';
                const isAuthenticated = typeof window.IS_AUTHENTICATED !== 'undefined' && window.IS_AUTHENTICATED === true;
                
                // Создаём Set с ID городов, для которых уже есть маркеры
                const existingMarkerCityIds = new Set(allMarkers.map(marker => marker._cityId).filter(id => id !== undefined));
                
                // Отображаем города на карте
                for (let i = 0; i < cities.length; i++) {
                    const city = cities[i];
                    
                    // Пропускаем города, для которых уже есть маркер
                    if (existingMarkerCityIds.has(city.id)) {
                        continue;
                    }
                    
                    const lat = parseFloat(city.lat);
                    const lon = parseFloat(city.lon);
                    
                    if (isNaN(lat) || isNaN(lon)) {
                        continue;
                    }
                    
                    // Формируем данные города для попапа
                    const cityData = {
                        id: city.id,
                        name: city.title,
                        isVisited: city.isVisited || false,
                        firstVisitDate: city.firstVisitDate || null,
                        lastVisitDate: city.lastVisitDate || null,
                        numberOfVisits: city.numberOfVisits || 0,
                        // Явно устанавливаем null, чтобы не показывать информацию о количестве пользователей
                        numberOfUsersWhoVisitCity: null,
                        numberOfVisitsAllUsers: null
                    };
                    
                    // Выбираем иконку в зависимости от статуса посещения и наличия в коллекции
                    const isInCollection = selectedCities.some(selectedCity => selectedCity.id === city.id);
                    let icon;
                    if (isInCollection) {
                        // Если город уже в коллекции - используем синюю иконку
                        icon = icon_blue_pin;
                    } else {
                        // Иначе используем стандартную иконку в зависимости от статуса посещения
                        icon = city.isVisited ? icon_visited_pin : icon_not_visited_pin;
                    }
                    const marker = L.marker([lat, lon], {icon: icon}).addTo(map);
                    
                    // Формируем ссылки на регион и страну
                    const regionLink = city.regionId ? `/region/${city.regionId}/list` : null;
                    const countryLink = city.countryCode ? `${countryCitiesBaseUrl}?country=${encodeURIComponent(city.countryCode)}` : null;
                    
                    // Базовые опции для попапа (без addButtonText, он будет обновляться динамически)
                    const basePopupOptions = {
                        regionName: city.region || null,
                        countryName: city.country || null,
                        regionLink: regionLink,
                        countryLink: countryLink,
                        isAuthenticated: isAuthenticated,
                        isCollectionOwner: true // На странице создания коллекции пользователь всегда является создателем
                    };
                    
                    // Сохраняем ID города в маркере для последующего использования
                    marker._cityId = city.id;
                    marker._cityData = cityData;
                    marker._basePopupOptions = basePopupOptions;
                    
                    // Функция для обновления содержимого попапа
                    const updatePopupContent = () => {
                        // Проверяем актуальное состояние коллекции
                        const isInCollection = selectedCities.some(selectedCity => selectedCity.id === city.id);
                        const popupOptions = {
                            regionName: basePopupOptions.regionName,
                            countryName: basePopupOptions.countryName,
                            regionLink: basePopupOptions.regionLink,
                            countryLink: basePopupOptions.countryLink,
                            isAuthenticated: basePopupOptions.isAuthenticated,
                            isCollectionOwner: basePopupOptions.isCollectionOwner,
                            addButtonText: isInCollection ? 'Удалить из коллекции' : 'Добавить в коллекцию'
                        };
                        return buildPopupContent(cityData, popupOptions);
                    };
                    
                    // Сохраняем функцию обновления в маркере
                    marker._updatePopupContent = updatePopupContent;
                    
                    // Привязываем попап с функцией обновления
                    marker.bindPopup(updatePopupContent, {maxWidth: 400, minWidth: 280});
                    
                    // Обновляем содержимое попапа при каждом открытии
                    marker.on('popupopen', () => {
                        // Обновляем содержимое попапа с актуальным состоянием
                        marker.setPopupContent(updatePopupContent());
                        if (window.HSStaticMethods && typeof window.HSStaticMethods.autoInit === 'function') {
                            window.HSStaticMethods.autoInit();
                        }
                    });
                    
                    marker.bindTooltip(cityData.name, {direction: 'top'});
                    marker.on('mouseover', function () {
                        const tooltip = this.getTooltip();
                        if (this.isPopupOpen()) {
                            tooltip.setOpacity(0.0);
                        } else {
                            tooltip.setOpacity(0.9);
                        }
                    });
                    marker.on('click', function () {
                        this.getTooltip().setOpacity(0.0);
                    });
                    
                    allMarkers.push(marker);
                    // Добавляем ID города в Set, чтобы не создавать дубликаты при последующих загрузках
                    existingMarkerCityIds.add(city.id);
                }
                
                // Центрируем и масштабируем карту по маркерам
                if (allMarkers.length > 0) {
                    const group = new L.featureGroup([...allMarkers]);
                    map.fitBounds(group.getBounds());
                }
                
            } catch (error) {
                console.error('Ошибка при загрузке городов:', error);
                showDangerToast('Ошибка', 'Не удалось загрузить города');
            } finally {
                loadCitiesButton.disabled = false;
                loadCitiesButton.innerHTML = originalText;
                updateLoadCitiesButton();
            }
        });
        
        // Обработчик клика на кнопку "Сохранить коллекцию"
        if (saveCollectionButton) {
            saveCollectionButton.addEventListener('click', async () => {
                // Получаем название коллекции
                const collectionNameInput = document.getElementById('collection_name');
                if (!collectionNameInput) {
                    showDangerToast('Ошибка', 'Поле названия коллекции не найдено');
                    return;
                }

                const collectionName = collectionNameInput.value.trim();
                if (!collectionName) {
                    showDangerToast('Ошибка', 'Необходимо указать название коллекции');
                    collectionNameInput.focus();
                    return;
                }

                // Проверяем, что выбраны города
                if (selectedCities.length === 0) {
                    showDangerToast('Ошибка', 'Необходимо добавить хотя бы один город в коллекцию');
                    return;
                }

                // Отключаем кнопку на время отправки
                saveCollectionButton.disabled = true;
                const originalText = saveCollectionButton.innerHTML;
                saveCollectionButton.innerHTML = '<span class="inline-block animate-spin rounded-full border-2 border-solid border-current border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]"></span> Сохранение...';

                try {
                    // Получаем значение switch для публичной коллекции
                    const isPublicSwitch = document.getElementById('is_public_switch');
                    const isPublic = isPublicSwitch ? isPublicSwitch.checked : false;

                    // Формируем данные для отправки
                    const requestData = {
                        title: collectionName,
                        city_ids: selectedCities.map(city => city.id),
                        is_public: isPublic,
                    };

                    // Определяем URL и метод запроса в зависимости от режима
                    let apiUrl;
                    let method;
                    if (isEditMode) {
                        // Режим редактирования - обновляем существующую коллекцию
                        apiUrl = `/api/collection/personal/${window.COLLECTION_ID}/update`;
                        method = 'PUT';
                    } else {
                        // Режим создания - создаём новую коллекцию
                        apiUrl = '/api/collection/personal/create';
                        method = 'POST';
                    }

                    // Отправляем запрос на API
                    const response = await fetch(apiUrl, {
                        method: method,
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken'),
                        },
                        body: JSON.stringify(requestData),
                    });

                    if (!response.ok) {
                        const errorData = await response.json().catch(() => ({ detail: 'Неизвестная ошибка' }));
                        throw new Error(errorData.detail || `Не удалось ${isEditMode ? 'обновить' : 'создать'} коллекцию`);
                    }

                    const data = await response.json();

                    // Показываем сообщение об успехе
                    showSuccessToast('Успешно', `Коллекция успешно ${isEditMode ? 'обновлена' : 'создана'}`);

                    // Перенаправляем на страницу коллекции
                    const collectionId = isEditMode ? window.COLLECTION_ID : data.id;
                    window.location.href = `/collection/personal/${collectionId}/list`;

                } catch (error) {
                    console.error('Ошибка при сохранении коллекции:', error);
                    showDangerToast('Ошибка', error.message || 'Не удалось сохранить коллекцию. Попробуйте ещё раз.');
                } finally {
                    saveCollectionButton.disabled = false;
                    saveCollectionButton.innerHTML = originalText;
                }
            });
        }
    })();
}));

