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

function loadRegistrationsComparisonCards(days, idPrefix) {
    const {dateFrom, dateTo} = getLastDaysRange(days);
    const url = buildRegistrationsQueryUrl(DASHBOARD_ROUTES.getRegistrationsCompare, {
        date_from: dateFrom,
        date_to: dateTo,
    });

    fetchComparisonData(url)
        .then((data) => {
            updateCompareCardValue(`${idPrefix}-current`, data.current_count);
            updateCompareCardValue(`${idPrefix}-previous`, data.previous_count);
            updateCompareCardValue(
                `${idPrefix}-delta`,
                `${data.delta} (${data.delta_percent}%)`,
                true,
                data.delta,
            );
        })
        .catch((error) => {
            console.error('Failed to fetch registrations comparison', error);
            showCardFallback(`${idPrefix}-current`);
            showCardFallback(`${idPrefix}-previous`);
            showCardFallback(`${idPrefix}-delta`);
        });
}

function loadRegistrationsTrendCardChart(canvasId, days, groupBy, tooltipMetricLabel) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        return;
    }

    const {dateFrom, dateTo} = getLastDaysRange(days);
    const url = buildRegistrationsQueryUrl(DASHBOARD_ROUTES.getRegistrationsByRange, {
        date_from: dateFrom,
        date_to: dateTo,
        group_by: groupBy,
    });

    fetchChartData(url)
        .then((data) => {
            const labels = data.map((item) => item.label);
            const values = data.map((item) => item.count);
            const context = canvas.getContext('2d');
            if (!context) {
                return;
            }

            new Chart(context, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            data: values,
                            borderColor: 'rgba(37,99,235,0.9)',
                            backgroundColor: 'rgba(37,99,235,0.15)',
                            fill: true,
                            borderWidth: 2,
                            pointRadius: 0,
                            pointHoverRadius: 3,
                            tension: 0.35,
                        },
                    ],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        mode: 'index',
                        intersect: false,
                    },
                    plugins: {
                        legend: {
                            display: false,
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            callbacks: {
                                label(context) {
                                    return `${tooltipMetricLabel}: ${context.parsed.y}`;
                                },
                            },
                        },
                    },
                    scales: {
                        x: {
                            display: false,
                            grid: {
                                display: false,
                            },
                        },
                        y: {
                            display: false,
                            grid: {
                                display: false,
                            },
                            beginAtZero: true,
                        },
                    },
                },
            });
        })
        .catch((error) => {
            console.error('Failed to fetch registrations trend chart', error);
        });
}

function loadTotalUsersComparisonChart() {
    const canvas = document.getElementById('total-users-compare-chart');
    if (!canvas) {
        return;
    }

    Promise.all([
        fetchQuantity(DASHBOARD_ROUTES.getNumberOfUsers),
        fetchQuantity(DASHBOARD_ROUTES.getNumberOfUsersWithoutVisitedCities),
    ])
        .then(([totalUsersQty, inactiveUsersQty]) => {
            const context = canvas.getContext('2d');
            if (!context) {
                return;
            }
            const activeUsersQty = Math.max(totalUsersQty - inactiveUsersQty, 0);

            new Chart(context, {
                type: 'bar',
                data: {
                    labels: ['Пользователи'],
                    datasets: [
                        {
                            label: 'Активные',
                            data: [activeUsersQty],
                            borderColor: 'rgba(59,130,246,1)',
                            backgroundColor: 'rgba(59,130,246,0.75)',
                            borderWidth: 0,
                            borderRadius: 8,
                            borderSkipped: false,
                            barThickness: 22,
                            stack: 'users',
                        },
                        {
                            label: 'Неактивные',
                            data: [inactiveUsersQty],
                            borderColor: 'rgba(124,58,237,1)',
                            backgroundColor: 'rgba(124,58,237,0.85)',
                            borderWidth: 0,
                            borderRadius: 8,
                            borderSkipped: false,
                            barThickness: 22,
                            stack: 'users',
                        },
                    ],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    indexAxis: 'y',
                    plugins: {
                        legend: {
                            display: true,
                            position: 'bottom',
                            labels: {
                                boxWidth: 10,
                                boxHeight: 10,
                                usePointStyle: true,
                                pointStyle: 'circle',
                            },
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            callbacks: {
                                label(context) {
                                    return `${context.dataset.label}: ${context.parsed.x}`;
                                },
                                afterBody() {
                                    return `Всего пользователей: ${totalUsersQty}`;
                                },
                            },
                        },
                    },
                    scales: {
                        x: {
                            stacked: true,
                            display: false,
                            beginAtZero: true,
                            grid: {
                                display: false,
                            },
                        },
                        y: {
                            stacked: true,
                            grid: {
                                display: false,
                            },
                            ticks: {
                                display: false,
                            },
                        },
                    },
                },
            });
        })
        .catch((error) => {
            console.error('Failed to fetch total users comparison chart', error);
        });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        loadVisitedCountriesChart();
        loadVisitedCitiesByUserChart();
        loadUniqueVisitedCitiesByUserChart();
        loadRegistrationsComparisonCards(30, 'registrations-30');
        loadRegistrationsComparisonCards(183, 'registrations-6m');
        loadRegistrationsComparisonCards(365, 'registrations-1y');
        loadRegistrationsTrendCardChart(
            'registrations-30-trend-chart',
            30,
            'day',
            'Регистраций за день'
        );
        loadRegistrationsTrendCardChart(
            'registrations-6m-trend-chart',
            183,
            'week',
            'Регистраций за неделю'
        );
        loadRegistrationsTrendCardChart(
            'registrations-1y-trend-chart',
            365,
            'month',
            'Регистраций за месяц'
        );
        loadTotalUsersComparisonChart();
    });
} else {
    loadVisitedCountriesChart();
    loadVisitedCitiesByUserChart();
    loadUniqueVisitedCitiesByUserChart();
    loadRegistrationsComparisonCards(30, 'registrations-30');
    loadRegistrationsComparisonCards(183, 'registrations-6m');
    loadRegistrationsComparisonCards(365, 'registrations-1y');
    loadRegistrationsTrendCardChart(
        'registrations-30-trend-chart',
        30,
        'day',
        'Регистраций за день'
    );
    loadRegistrationsTrendCardChart(
        'registrations-6m-trend-chart',
        183,
        'week',
        'Регистраций за неделю'
    );
    loadRegistrationsTrendCardChart(
        'registrations-1y-trend-chart',
        365,
        'month',
        'Регистраций за месяц'
    );
    loadTotalUsersComparisonChart();
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