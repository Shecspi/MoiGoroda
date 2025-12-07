import {create_map} from '../components/map.js';

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
        
        // Функция для обновления состояния кнопки загрузки городов
        const updateLoadCitiesButton = () => {
            const selectedOptions = Array.from(regionSelectElement.selectedOptions);
            const selectedRegionIds = selectedOptions
                .map(option => option.value)
                .filter(value => value !== '');
            
            if (selectedRegionIds.length > 0 && !regionSelectElement.disabled) {
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

                if (regions.length === 0) {
                    regionSelectElement.disabled = true;
                    showDangerToast('Информация', 'Для выбранных стран нет регионов');
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
                updateLoadCitiesButton();
            }
        });
        
        // Обработчик изменения выбора регионов
        regionSelectElement.addEventListener('change', () => {
            updateLoadCitiesButton();
        });
    })();

    // // Инициализация пустой карты
    // const map = create_map();
    // window.MG_MAIN_MAP = map;
    // // Устанавливаем центр карты на Россию
    // map.setView([55.7522, 37.6156], 6);

    // // Удаляем пустую опцию из regionSelect, чтобы Choices.js использовал placeholder
    // const regionEmptyOption = regionSelect.querySelector('option[value=""]');
    // if (regionEmptyOption) {
    //     regionEmptyOption.remove();
    // }
    
    // const choicesRegion = new Choices(regionSelect, {
    //     searchEnabled: true,
    //     shouldSort: false,
    //     placeholderValue: 'Выберите регион',
    //     noResultsText: 'Ничего не найдено',
    //     noChoicesText: 'Нет доступных вариантов',
    //     itemSelectText: 'Нажмите для выбора',
    //     loadingText: 'Загрузка...',
    // });

    // // Удаляем пустую опцию из citySelect, чтобы Choices.js использовал placeholder
    // const cityEmptyOption = citySelect.querySelector('option[value=""]');
    // if (cityEmptyOption) {
    //     cityEmptyOption.remove();
    // }
    
    // const choicesCity = new Choices(citySelect, {
    //     searchEnabled: true,
    //     shouldSort: false,
    //     placeholderValue: 'Выберите город',
    //     noResultsText: 'Ничего не найдено',
    //     noChoicesText: 'Нет доступных вариантов',
    //     itemSelectText: 'Нажмите для выбора',
    //     loadingText: 'Загрузка...',
    // });
    
    // // Проверяем начальные значения для определения состояния поля города
    // const initialRegionValue = regionSelect.value;
    
    // // Если регион не выбран - отключаем поле города
    // if (!initialRegionValue) {
    //     choicesCity.disable();
    // }


    // // При изменении выбранных стран делаем запрос и обновляем регионы
    // countrySelect.addEventListener('change', async (event) => {
    //     choicesRegion.enable();
    //     choicesCity.enable();

    //     // Получаем все выбранные страны (для множественного выбора)
    //     const selectedCountries = Array.from(event.target.selectedOptions).map(option => option.value);

    //     if (selectedCountries.length === 0 || selectedCountries.includes('')) {
    //         // Очистить регионы и города, если страны не выбраны
    //         choicesRegion.clearStore();
    //         choicesRegion.disable();
    //         choicesCity.clearStore();
    //         choicesCity.disable();
    //         return;
    //     }

    //     // TODO: Обработка множественного выбора стран
    //     // Пока что используем первую выбранную страну
    //     const countryId = selectedCountries[0];

    //     try {
    //         // Загрузка регионов страны
    //         const response = await fetch(`/api/region/list?country_id=${countryId}`);
    //         if (!response.ok) throw new Error('Ошибка загрузки регионов');

    //         const regions = await response.json();

    //         // Очистить старые опции
    //         choicesRegion.clearStore();

    //         if (regions.length === 0) {
    //             choicesRegion.disable();
    //             choicesCity.clearStore();
    //             choicesCity.disable();
    //             showDangerToast('Ошибка', 'Для выбранной страны нет регионов');
    //             return;
    //         }

    //         choicesRegion.setChoices(
    //             regions.map((region) => ({
    //                 value: region.id,
    //                 label: region.title,
    //                 selected: false,
    //                 disabled: false,
    //             })),
    //             'value',
    //             'label',
    //             true
    //         );

    //         // Очищаем города при изменении страны
    //         choicesCity.clearStore();
    //         choicesCity.disable();
    //     } catch (error) {
    //         console.error('Ошибка при загрузке регионов:', error);
    //         showDangerToast('Ошибка', 'Не удалось загрузить регионы');
    //     }
    // });

    // // При изменении региона делаем запрос и обновляем города
    // regionSelect.addEventListener('change', async (event) => {
    //     const regionId = event.target.value;

    //     if (!regionId) {
    //         // Если регион не выбран, отключаем поле города
    //         choicesCity.disable();
    //         choicesCity.clearStore();
    //         return;
    //     }

    //     choicesCity.enable();
    //     choicesCity.clearStore();

    //     try {
    //         const cityResponse = await fetch(`/api/city/list_by_region?region_id=${regionId}`);
    //         if (!cityResponse.ok) throw new Error('Ошибка загрузки городов');

    //         const cities = await cityResponse.json();

    //         if (cities.length === 0) {
    //             choicesCity.disable();
    //             showDangerToast('Ошибка', 'Для выбранного региона нет городов');
    //             return;
    //         }

    //         choicesCity.setChoices(
    //             cities.map((city) => ({
    //                 value: city.id,
    //                 label: city.title,
    //                 selected: false,
    //                 disabled: false,
    //             })),
    //             'value',
    //             'label',
    //             true
    //         );
    //     } catch (error) {
    //         console.error('Ошибка при загрузке городов:', error);
    //         showDangerToast('Ошибка', 'Не удалось загрузить города');
    //     }
    // });
}));

