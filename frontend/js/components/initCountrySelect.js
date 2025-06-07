import Choices from "choices.js";
import 'choices.js/public/assets/styles/choices.min.css';

export async function initCountrySelect({
    selectId = 'id_country',
    apiUrl = '/api/country/list_by_cities',
    redirectBaseUrl = window.location.pathname,
    urlParamName = 'country'
} = {}) {
    const urlParams = new URLSearchParams(window.location.search);
    const selectedCountryId = urlParams.get(urlParamName);

    const countrySelect = document.getElementById(selectId);
    if (!countrySelect) return;

    const choices = new Choices(countrySelect, {
        searchEnabled: true,
        shouldSort: false,
        placeholderValue: 'Загрузка...',
        noResultsText: 'Ничего не найдено',
        noChoicesText: 'Нет доступных вариантов',
        itemSelectText: 'Нажмите для выбора',
        loadingText: 'Загрузка...',
    });
    choices.disable();

    try {
        const response = await fetch(apiUrl);
        if (!response.ok) throw new Error('Ошибка загрузки списка стран');
        const countries = await response.json();

        choices.setChoices(
            [
                {
                    value: '',
                    label: 'Все страны',
                    selected: !selectedCountryId,
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
        choices.enable();
    } catch (error) {
        console.error(error);
        choices.clearChoices();
        choices.setChoices(
            [{ value: '', label: 'Ошибка загрузки', disabled: true }],
            'value',
            'label',
            true
        );
    }

    // Обработка выбора
    countrySelect.addEventListener('change', (event) => {
        const selectedValue = event.target.value;
        const query = new URLSearchParams(window.location.search);
        if (selectedValue) {
            query.set(urlParamName, selectedValue);
        } else {
            query.delete(urlParamName);
        }

        window.location.href = `${redirectBaseUrl}?${query.toString()}`;
    });
}
