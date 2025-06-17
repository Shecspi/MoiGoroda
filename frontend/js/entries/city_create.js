import Choices from 'choices.js';
import 'choices.js/public/assets/styles/choices.min.css';
import {showDangerToast} from "../components/toast";

document.addEventListener('DOMContentLoaded', () => {
    const countrySelect = document.getElementById('id_country');
    const regionSelect = document.getElementById('id_region');
    const citySelect = document.getElementById('id_city');

    const choicesCountry = new Choices(countrySelect, {
        searchEnabled: true,
        shouldSort: false,
        placeholderValue: 'Выберите страну',
        noResultsText: 'Ничего не найдено',
        noChoicesText: 'Нет доступных вариантов',
        itemSelectText: 'Нажмите для выбора',
        loadingText: 'Загрузка...',
    });
    const choicesRegion = new Choices(regionSelect, {
        searchEnabled: true,
        shouldSort: false,
        placeholderValue: 'Выберите регион',
        noResultsText: 'Ничего не найдено',
        noChoicesText: 'Нет доступных вариантов',
        itemSelectText: 'Нажмите для выбора',
        loadingText: 'Загрузка...',
    });
    const choicesCity = new Choices(citySelect, {
        searchEnabled: true,
        shouldSort: false,
        placeholderValue: 'Выберите город',
        noResultsText: 'Ничего не найдено',
        noChoicesText: 'Нет доступных вариантов',
        itemSelectText: 'Нажмите для выбора',
        loadingText: 'Загрузка...',
    });

    // При изменении страны делаем запрос и обновляем регионы
    countrySelect.addEventListener('change', async (event) => {
        choicesRegion.enable();
        choicesCity.enable();

        const countryId = event.target.value;

        if (!countryId) {
            // Очистить регионы и города, если страна не выбрана
            choicesRegion.clearStore();
            choicesCity.clearStore();
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
                    showDangerToast('Ошибка', 'Для выбранной страны нет городов');
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
            } else {
                // Добавить новые опции
                choicesRegion.setChoices(
                    regions.map((region, index) => ({
                        value: region.id,
                        label: region.title,
                        selected: index === 0, // Делаем первый регион выбранным
                        disabled: false,
                    })),
                    'value',
                    'label',
                    true,
                );

                // Загружаем города для первого региона
                const cityResponse = await fetch(`/api/city/list_by_region?region_id=${regions[0].id}`);
                if (!cityResponse.ok) throw new Error('Ошибка загрузки городов');

                const cities = await cityResponse.json();
                choicesCity.setChoices(
                    cities.map((city, index) => ({
                        value: city.id,
                        label: city.title,
                        selected: index === 0,
                        disabled: false,
                    })),
                    'value',
                    'label',
                    true
                );
            }
        } catch (error) {
            console.error('Ошибка при загрузке регионов:', error);
            showDangerToast('Ошибка', 'Произошла ошибка при загрузке списка регионов. Пожалуйста, перезагрузите страницу и попробуйте ещё раз.')
        }
    });

    regionSelect.addEventListener('change', async (event) => {
        choicesCity.enable();
        choicesCity.clearStore();

        const regionId = event.target.value;

        const cityResponse = await fetch(`/api/city/list_by_region?region_id=${regionId}`);
        if (!cityResponse.ok) throw new Error('Ошибка загрузки городов');

        const cities = await cityResponse.json();

        if (cities.length === 0) {
            choicesCity.disable();
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
});
