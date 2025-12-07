import L from 'leaflet';
import {create_map} from '../components/map.js';
import {icon_visited_pin, icon_not_visited_pin} from '../components/icons.js';
import {bindPopupToMarker} from '../components/city_popup.js';
import {showDangerToast} from "../components/toast";

window.addEventListener('load', () => requestAnimationFrame(async () => {
    (function() {
        // Получаем экземпляры Preline Select (они уже инициализированы автоматически через data-hs-select)
        const countrySelect = window.HSSelect.getInstance('#country_select');
        const countrySelectElement = document.getElementById('country_select');
        const regionSelect = window.HSSelect.getInstance('#region_select');
        const regionSelectElement = document.getElementById('region_select');
        const loadCitiesButton = document.getElementById('load_cities_button');
        
        if (!countrySelect || !countrySelectElement || !regionSelect || !regionSelectElement || !loadCitiesButton) {
            console.error('Не найдены необходимые элементы формы');
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
                    
                    const popupOptions = {
                        regionName: city.region || null,
                        countryName: city.country || null,
                        regionLink: regionLink,
                        countryLink: countryLink,
                        isAuthenticated: isAuthenticated
                    };
                    
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
                    
                    bindPopupToMarker(marker, cityData, popupOptions);
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
    })();
}));

