import Choices from "choices.js";
import 'choices.js/public/assets/styles/choices.min.css';

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

        const countryChoices = [];
        let separatorAdded = false;

        countries.forEach((country) => {
            if (!separatorAdded && country.number_of_visited_cities === 0) {
                // Вставляем разделитель перед первой страной с 0 посещённых городов
                countryChoices.push({
                    value: '',
                    label: 'Непосещённые страны', // или любой другой разделитель
                    disabled: true,
                });
                separatorAdded = true;
            }

            countryChoices.push({
                value: country.code,
                label: (country.number_of_visited_cities === undefined || country.number_of_cities === undefined)
                    ? country.name
                    : `${country.name} (${country.number_of_visited_cities} из ${country.number_of_cities})`,
                selected: selectedCountryCode === country.code,
                disabled: false,
            });
        });

        // const countryChoices = countries.map((country) => ({
        //     value: country.code,
        //     label: `${country.name} (${country.number_of_visited_cities} из ${country.number_of_cities})`,
        //     selected: selectedCountryCode === country.code,
        //     disabled: false,
        // }));

        if (showAllOption) {
            countryChoices.unshift({
                value: '',
                label: 'Все страны',
                selected: !selectedCountryCode,
                disabled: false,
            });
        }

        choices.setChoices(countryChoices, 'value', 'label', true);
        choices.enable();
    } catch (error) {
        console.error(error);
        choices.clearChoices();
        choices.setChoices(
            [{value: '', label: 'Ошибка загрузки', disabled: true}],
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
