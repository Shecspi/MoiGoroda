import {getCookie} from '../components/get_cookie.js';

const DASHBOARD_ROUTES = Object.freeze({
    // Пользователи
    getNumberOfUsers: '/api/dashboard/users/',
    getNumberOfUsersWithoutVisitedCities: '/api/dashboard/users/without_visited_cities/',
    // Города
    getTotalVisitedCitiesVisits: '/api/dashboard/visited_cities/total/',
    getUniqueVisitedCities: '/api/dashboard/visited_cities/unique/',
    getMaxQtyUniqueVisitedCities: '/api/dashboard/visited_cities/max_unique/',
    getMaxQtyVisitedCities: '/api/dashboard/visited_cities/max/',
    getAverageQtyVisitedCities: '/api/dashboard/visited_cities/average/',
    getAverageQtyUniqueVisitedCities: '/api/dashboard/visited_cities/average_unique/',
    // Страны
    getTotalVisitedCountries: '/api/dashboard/visited_countries/total/',
    getUsersWithVisitedCountries: '/api/dashboard/visited_countries/users/',
    getAverageQtyVisitedCountries: '/api/dashboard/visited_countries/average/',
    getMaxQtyVisitedCountries: '/api/dashboard/visited_countries/max/',
    // Добавленные страны
    getAddedVisitedCountryYeterday: '/api/dashboard/visited_countries/added/1/',
    getAddedVisitedCountriesByWeek: '/api/dashboard/visited_countries/added/7/',
    getAddedVisitedCountriesByMonth: '/api/dashboard/visited_countries/added/30/',
    getAddedVisitedCountriesByYear: '/api/dashboard/visited_countries/added/365/',
    getAddedVisitedCountriesChart: '/api/dashboard/visited_countries/added/chart/',
    // Графики
    getRegistrationsByRange: '/api/dashboard/users/registrations/range/',
    getRegistrationsCompare: '/api/dashboard/users/registrations/compare/',
    getRegistrationsCumulativeChart: '/api/dashboard/users/registrations/chart/cumulative/',
    getVisitedCitiesByUserChart: '/api/dashboard/visited_cities/by_user/chart/',
    getUniqueVisitedCitiesByUserChart: '/api/dashboard/visited_cities/unique_by_user/chart/',
});

function formatDate(date) {
    return date.toISOString().slice(0, 10);
}

function getLastDaysRange(days) {
    const dateTo = new Date();
    const dateFrom = new Date();
    dateFrom.setDate(dateTo.getDate() - (days - 1));
    return {
        dateFrom: formatDate(dateFrom),
        dateTo: formatDate(dateTo),
    };
}

function buildRegistrationsQueryUrl(baseUrl, params) {
    const searchParams = new URLSearchParams(params);
    return `${baseUrl}?${searchParams.toString()}`;
}

// Пользователи
loadQuantityCard('number-total_users', DASHBOARD_ROUTES.getNumberOfUsers);
loadQuantityCard('number-number_of_users_without_visited_cities', DASHBOARD_ROUTES.getNumberOfUsersWithoutVisitedCities);
// Города
loadQuantityCard('number-total_visited_cities_visits', DASHBOARD_ROUTES.getTotalVisitedCitiesVisits);
loadQuantityCard('number-unique_visited_cities', DASHBOARD_ROUTES.getUniqueVisitedCities);
loadQuantityCard('number-average_qty_visited_cities', DASHBOARD_ROUTES.getAverageQtyVisitedCities);
loadQuantityCard('number-average_qty_unique_visited_cities', DASHBOARD_ROUTES.getAverageQtyUniqueVisitedCities);
loadQuantityCard(
    'number-max_qty_unique_visited_cities',
    DASHBOARD_ROUTES.getMaxQtyUniqueVisitedCities,
);
loadQuantityCard('number-max_qty_visited_cities', DASHBOARD_ROUTES.getMaxQtyVisitedCities);
// Страны
loadQuantityCard('number-total_visited_countries', DASHBOARD_ROUTES.getTotalVisitedCountries);
loadQuantityCard('number-user_with_visited_countries', DASHBOARD_ROUTES.getUsersWithVisitedCountries);
loadQuantityCard('number-average_qty_visited_countries', DASHBOARD_ROUTES.getAverageQtyVisitedCountries);
loadQuantityCard('number-max_qty_visited_countries', DASHBOARD_ROUTES.getMaxQtyVisitedCountries);
// Добавленные страны
loadQuantityCard('number-qty_of_added_visited_countries_yesterday', DASHBOARD_ROUTES.getAddedVisitedCountryYeterday);
loadQuantityCard('number-qty_of_added_visited_countries_week', DASHBOARD_ROUTES.getAddedVisitedCountriesByWeek);
loadQuantityCard('number-qty_of_added_visited_countries_month', DASHBOARD_ROUTES.getAddedVisitedCountriesByMonth);
loadQuantityCard('number-qty_of_added_visited_countries_year', DASHBOARD_ROUTES.getAddedVisitedCountriesByYear);

async function fetchChartData(url) {
    const response = await fetch(url, {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            Accept: 'application/json',
        },
        credentials: 'same-origin',
    });

    if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
    }

    const data = await response.json();

    if (!Array.isArray(data)) {
        throw new Error('Unexpected response structure: expected array');
    }

    return data;
}

async function fetchComparisonData(url) {
    const response = await fetch(url, {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            Accept: 'application/json',
        },
        credentials: 'same-origin',
    });

    if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
    }

    const data = await response.json();
    if (
        typeof data.current_count !== 'number' ||
        typeof data.previous_count !== 'number' ||
        typeof data.delta !== 'number' ||
        typeof data.delta_percent !== 'number'
    ) {
        throw new Error('Unexpected response structure');
    }
    return data;
}

/**
 * Универсальная функция для загрузки и отображения графика
 * @param {string} canvasId - ID элемента canvas
 * @param {string} loadingElementId - ID элемента загрузки
 * @param {string} url - URL для получения данных
 * @param {string} label - Метка для набора данных
 * @param {string} borderColor - Цвет границы
 * @param {string} backgroundColor - Цвет фона
 * @param {number} borderWidth - Ширина границы (по умолчанию 2)
 */
function loadChart(canvasId, loadingElementId, url, label, borderColor, backgroundColor, borderWidth = 2) {
    const canvas = document.getElementById(canvasId);
    const loadingElement = document.getElementById(loadingElementId);
    
    if (!canvas || !loadingElement) {
        return;
    }

    fetchChartData(url)
        .then((data) => {
            const chartData = {};
            data.forEach((item) => {
                chartData[item.label] = item.count;
            });

            // Скрываем спиннер и показываем canvas
            loadingElement.classList.add('hidden');
            canvas.classList.remove('hidden');

            const ctx = canvas.getContext('2d');

            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: Object.keys(chartData),
                    datasets: [
                        {
                            label: label,
                            data: Object.values(chartData),
                            borderColor: borderColor,
                            backgroundColor: backgroundColor,
                            borderWidth: borderWidth,
                            borderRadius: 5,
                            borderSkipped: false,
                        },
                    ],
                },
            });
        })
        .catch((error) => {
            console.error('Failed to fetch chart data', error);
            loadingElement.innerHTML = '<p class="text-gray-600 dark:text-neutral-400">Не удалось загрузить данные графика</p>';
        });
}

function loadVisitedCountriesChart() {
    loadChart(
        'visitedCountriesChart',
        'visitedCountriesChartLoading',
        DASHBOARD_ROUTES.getAddedVisitedCountriesChart,
        'Количество добавленных посещённых стран за 1 день',
        'rgba(7,54,0,0.2)',
        'rgba(58,255,51,0.2)',
        2
    );
}

function loadRegistrationsChart() {
    const {dateFrom, dateTo} = getLastDaysRange(35);
    const url = buildRegistrationsQueryUrl(DASHBOARD_ROUTES.getRegistrationsByRange, {
        date_from: dateFrom,
        date_to: dateTo,
        group_by: 'day',
    });

    loadChart(
        'myChart',
        'myChartLoading',
        url,
        'Количество регистраций',
        'rgba(51,171,255,0.5)',
        'rgba(51,171,255,0.2)',
        2
    );
}

function loadRegistrationsByMonthChart() {
    const {dateFrom, dateTo} = getLastDaysRange(730);
    const url = buildRegistrationsQueryUrl(DASHBOARD_ROUTES.getRegistrationsByRange, {
        date_from: dateFrom,
        date_to: dateTo,
        group_by: 'month',
    });

    loadChart(
        'myChartMonth',
        'myChartMonthLoading',
        url,
        'Количество регистраций',
        'rgba(139,92,246,0.5)',
        'rgba(139,92,246,0.2)',
        2.5
    );
}

function loadVisitedCitiesByUserChart() {
    loadChart(
        'chart_qty_visited_cities',
        'chart_qty_visited_citiesLoading',
        DASHBOARD_ROUTES.getVisitedCitiesByUserChart,
        'Общее количество посещений городов',
        'rgba(52,0,0,0.2)',
        'rgba(255,115,115,0.2)',
        2
    );
}

function loadUniqueVisitedCitiesByUserChart() {
    loadChart(
        'chart_unique_visited_cities',
        'chart_unique_visited_citiesLoading',
        DASHBOARD_ROUTES.getUniqueVisitedCitiesByUserChart,
        'Количество уникальных городов',
        'rgba(0,52,104,0.2)',
        'rgba(115,184,255,0.2)',
        2
    );
}

function updateCompareCardValue(elementId, value, isDelta = false, deltaNumber = 0) {
    const element = document.getElementById(elementId);
    if (!element) {
        return;
    }

    if (!isDelta) {
        element.innerHTML = `<span class="text-2xl font-bold text-gray-900 dark:text-white">${value}</span>`;
        return;
    }

    const deltaClass = deltaNumber >= 0
        ? 'text-emerald-600 dark:text-emerald-400'
        : 'text-red-600 dark:text-red-400';
    const sign = deltaNumber > 0 ? '+' : '';
    element.innerHTML = `<span class="text-2xl font-bold ${deltaClass}">${sign}${value}</span>`;
}

function loadRegistrationsComparisonCards() {
    const {dateFrom, dateTo} = getLastDaysRange(30);
    const url = buildRegistrationsQueryUrl(DASHBOARD_ROUTES.getRegistrationsCompare, {
        date_from: dateFrom,
        date_to: dateTo,
    });

    fetchComparisonData(url)
        .then((data) => {
            updateCompareCardValue('registrations-compare-current', data.current_count);
            updateCompareCardValue('registrations-compare-previous', data.previous_count);
            updateCompareCardValue(
                'registrations-compare-delta',
                `${data.delta} (${data.delta_percent}%)`,
                true,
                data.delta,
            );
        })
        .catch((error) => {
            console.error('Failed to fetch registrations comparison', error);
            showCardFallback('registrations-compare-current');
            showCardFallback('registrations-compare-previous');
            showCardFallback('registrations-compare-delta');
        });
}

function loadRegistrationsRangeChart() {
    const {dateFrom, dateTo} = getLastDaysRange(84);
    const url = buildRegistrationsQueryUrl(DASHBOARD_ROUTES.getRegistrationsByRange, {
        date_from: dateFrom,
        date_to: dateTo,
        group_by: 'week',
    });

    loadChart(
        'registrationsRangeChart',
        'registrationsRangeChartLoading',
        url,
        'Регистрации по неделям',
        'rgba(14,165,233,0.5)',
        'rgba(14,165,233,0.2)',
        2
    );
}

function loadRegistrationsCumulativeChart() {
    const {dateFrom, dateTo} = getLastDaysRange(90);
    const url = buildRegistrationsQueryUrl(DASHBOARD_ROUTES.getRegistrationsCumulativeChart, {
        date_from: dateFrom,
        date_to: dateTo,
        group_by: 'day',
    });

    loadChart(
        'registrationsCumulativeChart',
        'registrationsCumulativeChartLoading',
        url,
        'Накопительное количество регистраций',
        'rgba(139,92,246,0.5)',
        'rgba(139,92,246,0.2)',
        2
    );
}

async function fetchRegistrationsByRangeTotal(days) {
    const {dateFrom, dateTo} = getLastDaysRange(days);
    const url = buildRegistrationsQueryUrl(DASHBOARD_ROUTES.getRegistrationsByRange, {
        date_from: dateFrom,
        date_to: dateTo,
        group_by: 'day',
    });

    const data = await fetchChartData(url);
    return data.reduce((total, item) => total + item.count, 0);
}

function loadRegistrationRangeCards() {
    Promise.all([
        fetchRegistrationsByRangeTotal(1),
        fetchRegistrationsByRangeTotal(7),
        fetchRegistrationsByRangeTotal(30),
    ])
        .then(([todayQty, weekQty, monthQty]) => {
            updateNumberOnCard('number-registrations_yesterday', todayQty);
            updateNumberOnCard('number-registrations_week', weekQty);
            updateNumberOnCard('number-registrations_month', monthQty);
        })
        .catch((error) => {
            console.error('Failed to fetch registrations cards by range', error);
            showCardFallback('number-registrations_yesterday');
            showCardFallback('number-registrations_week');
            showCardFallback('number-registrations_month');
        });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        loadVisitedCountriesChart();
        loadRegistrationsChart();
        loadRegistrationsByMonthChart();
        loadVisitedCitiesByUserChart();
        loadUniqueVisitedCitiesByUserChart();
        loadRegistrationsComparisonCards();
        loadRegistrationsRangeChart();
        loadRegistrationsCumulativeChart();
        loadRegistrationRangeCards();
    });
} else {
    loadVisitedCountriesChart();
    loadRegistrationsChart();
    loadRegistrationsByMonthChart();
    loadVisitedCitiesByUserChart();
    loadUniqueVisitedCitiesByUserChart();
    loadRegistrationsComparisonCards();
    loadRegistrationsRangeChart();
    loadRegistrationsCumulativeChart();
    loadRegistrationRangeCards();
}

function updateNumberOnCard(element_id, newNumber) {
    const el = document.getElementById(element_id);
    if (!el) {
        return;
    }
    el.innerHTML = `<span class="text-2xl font-bold text-gray-900 dark:text-white">${newNumber}</span>`;
}

export async function fetchQuantity(url) {
    const response = await fetch(url, {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            Accept: 'application/json',
        },
        credentials: 'same-origin',
    });

    if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
    }

    const data = await response.json();

    if (typeof data.count !== 'number') {
        throw new Error('Unexpected response structure');
    }

    return data.count;
}

function showCardFallback(elementId) {
    const container = document.getElementById(elementId);
    if (container) {
        container.textContent = '—';
    }
}

function loadQuantityCard(elementId, url) {
    if (!url) {
        return;
    }

    fetchQuantity(url)
        .then((quantity) => {
            updateNumberOnCard(elementId, quantity);
        })
        .catch((error) => {
            console.error('Failed to fetch dashboard metric', error);
            showCardFallback(elementId);
        });
}