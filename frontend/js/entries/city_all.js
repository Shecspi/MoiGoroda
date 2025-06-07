import Choices from "choices.js";
import 'choices.js/public/assets/styles/choices.min.css';

document.addEventListener('DOMContentLoaded', async (event) => {
    const urlParams = new URLSearchParams(window.location.search);
    const selectedCountryId = urlParams.get('country');

    const countrySelect = document.getElementById('id_country');
    const choicesCountry = new Choices(countrySelect, {
        searchEnabled: true,
        shouldSort: false,
        placeholderValue: 'Загрузка...',
        noResultsText: 'Ничего не найдено',
        noChoicesText: 'Нет доступных вариантов',
        itemSelectText: 'Нажмите для выбора',
        loadingText: 'Загрузка...',
    });
    choicesCountry.disable();

    // Загрузка списка стран
    try {
        const response = await fetch(`/api/country/list_by_cities`);
        if (!response.ok) throw new Error('Ошибка загрузки списка стран');
        const countries = await response.json();

        choicesCountry.setChoices(
            [
                {
                    value: '', // или 'all', если ты так обрабатываешь на сервере
                    label: 'Все страны',
                    selected: !selectedCountryId, // можно false, если хочешь, чтобы пользователь явно выбрал
                    disabled: false,
                },
                ...countries.map((city) => ({
                    value: city.id,
                    label: city.name,
                    selected: Number(selectedCountryId) === Number(city.id),
                    disabled: false,
                })),
            ],
            'value',
            'label',
            true
        );
        choicesCountry.enable();
    } catch (error) {
        console.error(error);
        choicesCountry.clearChoices();
        choicesCountry.setChoices(
            [{value: '', label: 'Ошибка загрузки', disabled: true}],
            'value',
            'label',
            true
        );
    }

    // Обработка выбора страны
    countrySelect.addEventListener('change', (event) => {
        const selectedValue = event.target.value;

        if (selectedValue !== '') {
            window.location.href = `/city/all/list?country=${selectedValue}`
        } else {
            window.location.href = `/city/all/list`
        }
    });
});