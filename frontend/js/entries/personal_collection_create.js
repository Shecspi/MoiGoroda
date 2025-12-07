import L from 'leaflet';
import {create_map} from '../components/map.js';
import {icon_visited_pin, icon_not_visited_pin} from '../components/icons.js';
import {buildPopupContent} from '../components/city_popup.js';
import {showDangerToast} from "../components/toast";

window.addEventListener('load', () => requestAnimationFrame(async () => {
    (function() {
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
                
                // Обновляем содержимое попапа, если он открыт
                if (window.MG_MAIN_MAP) {
                    const openPopup = window.MG_MAIN_MAP._popup;
                    if (openPopup && openPopup._source) {
                        const marker = openPopup._source;
                        // Находим соответствующий маркер и обновляем его попап
                        const markerCityId = marker._cityId;
                        if (markerCityId === cityId && marker._updatePopupContent) {
                            // Обновляем содержимое попапа
                            marker.setPopupContent(marker._updatePopupContent());
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
                
                // Удаляем все существующие маркеры
                allMarkers.forEach(marker => map.removeLayer(marker));
                allMarkers.length = 0;
                
                if (cities.length === 0) {
                    showDangerToast('Информация', 'Для выбранных регионов нет городов');
                    loadCitiesButton.disabled = false;
                    loadCitiesButton.innerHTML = originalText;
                    return;
                }
                
                // Получаем базовые URL для ссылок
                const countryCitiesBaseUrl = window.COUNTRY_CITIES_BASE_URL || '';
                const isAuthenticated = typeof window.IS_AUTHENTICATED !== 'undefined' && window.IS_AUTHENTICATED === true;
                
                // Отображаем города на карте
                for (let i = 0; i < cities.length; i++) {
                    const city = cities[i];
                    const lat = parseFloat(city.lat);
                    const lon = parseFloat(city.lon);
                    
                    if (isNaN(lat) || isNaN(lon)) {
                        continue;
                    }
                    
                    // Выбираем иконку в зависимости от статуса посещения
                    const icon = city.isVisited ? icon_visited_pin : icon_not_visited_pin;
                    const marker = L.marker([lat, lon], {icon: icon}).addTo(map);
                    
                    // Формируем ссылки на регион и страну
                    const regionLink = city.regionId ? `/region/${city.regionId}/list` : null;
                    const countryLink = city.countryCode ? `${countryCitiesBaseUrl}?country=${encodeURIComponent(city.countryCode)}` : null;
                    
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
                    
                    // Базовые опции для попапа (без addButtonText, он будет обновляться динамически)
                    const basePopupOptions = {
                        regionName: city.region || null,
                        countryName: city.country || null,
                        regionLink: regionLink,
                        countryLink: countryLink,
                        isAuthenticated: isAuthenticated
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
            saveCollectionButton.addEventListener('click', () => {
                console.log('Выбранные города для коллекции:', selectedCities);
            });
        }
    })();
}));

