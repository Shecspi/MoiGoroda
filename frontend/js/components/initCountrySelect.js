/** Значение служебной опции до прихода данных (не конфликтует с кодами стран ISO). */
export const COUNTRY_SELECT_LOADING_VALUE = '__mg_country_loading__';

/** Разделитель «Непосещённые страны» — уникальный value, чтобы не совпадать с loading. */
const COUNTRY_SELECT_SEPARATOR_VALUE = '__mg_sep_unvisited__';

const COUNTRY_SELECT_ERROR_VALUE = '__mg_country_error__';

/**
 * Preline подключается в extra_js после entry; ждём появления HSSelect в window.
 */
export function waitForHSSelect() {
    return new Promise((resolve) => {
        if (window.HSSelect) {
            resolve();
            return;
        }
        const check = () => {
            if (window.HSSelect) {
                resolve();
            } else {
                requestAnimationFrame(check);
            }
        };
        check();
    });
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

/**
 * Первый и единственный вызов после того, как в &lt;select&gt; уже лежат нужные &lt;option&gt;.
 * До этого момента виден только нативный селект (стили из select-field.css) — без смены цвета на кнопку Preline.
 */
function initHSSelectFromPopulatedDom(countrySelect) {
    if (!countrySelect?.id) {
        return null;
    }

    if (typeof window.HSSelect.autoInit === 'function') {
        window.HSSelect.autoInit();
    }

    const sel = `#${countrySelect.id}`;
    if (!window.HSSelect.getInstance(sel)) {
        try {
            new window.HSSelect(countrySelect);
        } catch (e) {
            console.error('Ошибка инициализации HSSelect:', e);
            return null;
        }
    }

    countrySelect.classList.remove('--prevent-on-load-init');
    countrySelect.classList.remove('hidden');

    return window.HSSelect.getInstance(sel);
}

/** Для map_region и др.: после ручного заполнения &lt;option&gt; — один вызов HSSelect. */
export function attachCountrySelectHSSelect(countrySelect) {
    return initHSSelectFromPopulatedDom(countrySelect);
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

    function applyPlaceholderToDataAttr(placeholderText) {
        const dataHsSelect = countrySelect.getAttribute('data-hs-select');
        if (!dataHsSelect) return;
        try {
            const config = JSON.parse(dataHsSelect);
            config.placeholder = placeholderText;
            countrySelect.setAttribute('data-hs-select', JSON.stringify(config));
        } catch (e) {
            console.error('Ошибка при обновлении конфигурации Preline UI:', e);
        }
    }

    try {
        const [, countries] = await Promise.all([
            waitForHSSelect(),
            loadCountriesJson(),
        ]);

        applyPlaceholderToDataAttr(showAllOption ? 'Все страны' : 'Выберите страну...');
        buildCountryOptionsNative(countrySelect, countries, selectedCountryCode, showAllOption);
        countrySelect.removeAttribute('disabled');

        initHSSelectFromPopulatedDom(countrySelect);
    } catch (error) {
        console.error('Ошибка при загрузке списка стран:', error);

        if (typeof window.showDangerToast === 'function') {
            const errorMessage = error.message || 'Не удалось загрузить список стран';
            window.showDangerToast('Ошибка загрузки', errorMessage);
        }

        await waitForHSSelect();
        applyPlaceholderToDataAttr('Ошибка загрузки');
        countrySelect.textContent = '';
        const errOpt = document.createElement('option');
        errOpt.value = COUNTRY_SELECT_ERROR_VALUE;
        errOpt.textContent = 'Ошибка загрузки';
        errOpt.disabled = true;
        errOpt.selected = true;
        countrySelect.appendChild(errOpt);

        initHSSelectFromPopulatedDom(countrySelect);
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
