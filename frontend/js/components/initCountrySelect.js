/** Значение служебной опции до прихода данных (не конфликтует с кодами стран ISO). */
export const COUNTRY_SELECT_LOADING_VALUE = '__mg_country_loading__';

/** Разделитель «Непосещённые страны» — уникальный value, чтобы не совпадать с loading. */
const COUNTRY_SELECT_SEPARATOR_VALUE = '__mg_sep_unvisited__';

const COUNTRY_SELECT_ERROR_VALUE = '__mg_country_error__';

/**
 * Backward-compatible shim for legacy imports.
 * Select search is now rendered by our own ui-lib component.
 */
export function waitForHSSelect() {
    return Promise.resolve();
}

function ensureLoadingOption(countrySelect) {
    if (countrySelect.querySelector(`option[value="${COUNTRY_SELECT_LOADING_VALUE}"]`)) {
        return;
    }
    const opt = document.createElement('option');
    opt.value = COUNTRY_SELECT_LOADING_VALUE;
    opt.textContent = 'Загрузка...';
    opt.selected = true;
    countrySelect.appendChild(opt);
}

/** Backward-compatible helper for legacy callers. */
export function attachCountrySelectHSSelect(countrySelect) {
    if (!countrySelect) {
        return null;
    }
    countrySelect.dispatchEvent(new Event('change', { bubbles: true }));
    return null;
}

function buildCountryOptionsNative(countrySelect, countries, selectedCountryCode, showAllOption) {
    countrySelect.textContent = '';

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

    countries.forEach((country) => {
        if (!separatorAdded && country.number_of_visited_cities === 0) {
            const separatorOption = document.createElement('option');
            separatorOption.value = COUNTRY_SELECT_SEPARATOR_VALUE;
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
}

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

    ensureLoadingOption(countrySelect);

    async function loadCountriesJson() {
        const response = await fetch(apiUrl);
        if (!response.ok) {
            let errorMessage = 'Ошибка загрузки списка стран';
            try {
                const errorData = await response.json();
                if (errorData.detail) {
                    errorMessage = errorData.detail;
                } else if (errorData.message) {
                    errorMessage = errorData.message;
                }
            } catch (e) {
                if (response.status === 401) {
                    errorMessage = 'Требуется авторизация';
                } else if (response.status >= 500) {
                    errorMessage = 'Ошибка сервера. Попробуйте позже';
                }
            }
            throw new Error(errorMessage);
        }
        return response.json();
    }

    try {
        const countries = await loadCountriesJson();
        buildCountryOptionsNative(countrySelect, countries, selectedCountryCode, showAllOption);
        countrySelect.removeAttribute('disabled');
    } catch (error) {
        console.error('Ошибка при загрузке списка стран:', error);

        if (typeof window.showDangerToast === 'function') {
            const errorMessage = error.message || 'Не удалось загрузить список стран';
            window.showDangerToast('Ошибка загрузки', errorMessage);
        }

        countrySelect.textContent = '';
        const errOpt = document.createElement('option');
        errOpt.value = COUNTRY_SELECT_ERROR_VALUE;
        errOpt.textContent = 'Ошибка загрузки';
        errOpt.disabled = true;
        errOpt.selected = true;
        countrySelect.appendChild(errOpt);
    }

    if (!countrySelect.dataset.mgCountryChangeBound) {
        countrySelect.dataset.mgCountryChangeBound = '1';
        countrySelect.addEventListener('change', (event) => {
            const selectedValue = event.target.value;

            if (typeof window.updateNotVisitedCitiesButtonState === 'function') {
                window.updateNotVisitedCitiesButtonState();
            }

            const query = new URLSearchParams(window.location.search);
            if (selectedValue && selectedValue !== 'all') {
                query.set(urlParamName, selectedValue);
            } else {
                query.delete(urlParamName);
            }

            window.location.href = `${redirectBaseUrl}?${query.toString()}`;
        });
    }
}
