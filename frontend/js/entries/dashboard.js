import {getCookie} from '../components/get_cookie.js';
import ApexCharts from 'apexcharts';

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
    getAddedVisitedCitiesByRange: '/api/dashboard/visited_cities/added/range/',
    getAddedVisitedCitiesCompare: '/api/dashboard/visited_cities/added/compare/',
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
    const chartContainer = document.getElementById('chart_qty_visited_cities');
    const loadingElement = document.getElementById('chart_qty_visited_citiesLoading');

    if (!chartContainer || !loadingElement) {
        return;
    }

    fetchChartData(DASHBOARD_ROUTES.getVisitedCitiesByUserChart)
        .then((data) => {
            const labels = data.map((item) => item.label);
            const values = data.map((item) => item.count);
            const chartLabels = labels.length === 1 ? [labels[0], labels[0]] : labels;
            const chartValues = values.length === 1 ? [values[0], values[0]] : values;

            loadingElement.classList.add('hidden');
            chartContainer.classList.remove('hidden');
            chartContainer.innerHTML = '';

            const chart = new ApexCharts(chartContainer, {
                series: [
                    {
                        name: 'Посещения',
                        data: chartValues,
                    },
                ],
                chart: {
                    type: 'area',
                    height: '100%',
                    toolbar: {
                        show: false,
                    },
                    sparkline: {
                        enabled: true,
                    },
                },
                stroke: {
                    curve: 'straight',
                    width: 2,
                    colors: ['#16a34a'],
                },
                colors: ['#16a34a'],
                fill: {
                    type: 'gradient',
                    gradient: {
                        shade: 'dark',
                        gradientToColors: ['#16a34a'],
                        shadeIntensity: 1,
                        opacityFrom: 0.6,
                        opacityTo: 0,
                        stops: [0, 100],
                    },
                },
                states: {
                    normal: {
                        filter: {
                            type: 'none',
                        },
                    },
                    hover: {
                        filter: {
                            type: 'none',
                        },
                    },
                    active: {
                        filter: {
                            type: 'none',
                        },
                    },
                },
                xaxis: {
                    categories: chartLabels,
                },
                tooltip: {
                    custom({series, seriesIndex, dataPointIndex}) {
                        const userLabel = chartLabels[dataPointIndex] || 'Пользователь';
                        const value = series[seriesIndex][dataPointIndex];
                        return `
                            <div class="px-2 py-1 text-sm text-gray-700 dark:text-neutral-200">
                                ${userLabel}: <span class="font-semibold">${value}</span>
                            </div>
                        `;
                    },
                },
            });
            chart.render();
        })
        .catch((error) => {
            console.error('Failed to fetch visited cities by user chart', error);
            loadingElement.innerHTML =
                '<p class="text-gray-600 dark:text-neutral-400">Не удалось загрузить данные графика</p>';
        });
}

function loadUniqueVisitedCitiesByUserChart() {
    const chartContainer = document.getElementById('chart_unique_visited_cities');
    const loadingElement = document.getElementById('chart_unique_visited_citiesLoading');

    if (!chartContainer || !loadingElement) {
        return;
    }

    fetchChartData(DASHBOARD_ROUTES.getUniqueVisitedCitiesByUserChart)
        .then((data) => {
            const labels = data.map((item) => item.label);
            const values = data.map((item) => item.count);
            const chartLabels = labels.length === 1 ? [labels[0], labels[0]] : labels;
            const chartValues = values.length === 1 ? [values[0], values[0]] : values;

            loadingElement.classList.add('hidden');
            chartContainer.classList.remove('hidden');
            chartContainer.innerHTML = '';

            const chart = new ApexCharts(chartContainer, {
                series: [
                    {
                        name: 'Уникальные города',
                        data: chartValues,
                    },
                ],
                chart: {
                    type: 'area',
                    height: '100%',
                    toolbar: {
                        show: false,
                    },
                    sparkline: {
                        enabled: true,
                    },
                },
                stroke: {
                    curve: 'straight',
                    width: 2,
                    colors: ['#f59e0b'],
                },
                colors: ['#f59e0b'],
                fill: {
                    type: 'gradient',
                    gradient: {
                        shade: 'dark',
                        gradientToColors: ['#f59e0b'],
                        shadeIntensity: 1,
                        opacityFrom: 0.6,
                        opacityTo: 0,
                        stops: [0, 100],
                    },
                },
                states: {
                    normal: {
                        filter: {
                            type: 'none',
                        },
                    },
                    hover: {
                        filter: {
                            type: 'none',
                        },
                    },
                    active: {
                        filter: {
                            type: 'none',
                        },
                    },
                },
                xaxis: {
                    categories: chartLabels,
                },
                tooltip: {
                    custom({series, seriesIndex, dataPointIndex}) {
                        const userLabel = chartLabels[dataPointIndex] || 'Пользователь';
                        const value = series[seriesIndex][dataPointIndex];
                        return `
                            <div class="px-2 py-1 text-sm text-gray-700 dark:text-neutral-200">
                                ${userLabel}: <span class="font-semibold">${value}</span>
                            </div>
                        `;
                    },
                },
            });
            chart.render();
        })
        .catch((error) => {
            console.error('Failed to fetch unique visited cities by user chart', error);
            loadingElement.innerHTML =
                '<p class="text-gray-600 dark:text-neutral-400">Не удалось загрузить данные графика</p>';
        });
}

function updateCompareCardValue(elementId, value, isDelta = false, deltaNumber = 0) {
    const element = document.getElementById(elementId);
    if (!element) {
        return;
    }
    const isCurrentMetric = elementId.endsWith('-current');
    const baseMetricClass = isCurrentMetric
        ? 'dashboard-metric-number text-5xl font-extrabold leading-none text-gray-900 dark:text-white'
        : 'dashboard-metric-number text-base font-semibold text-gray-900 dark:text-white';

    if (!isDelta) {
        element.innerHTML = `<span class="${baseMetricClass}">${value}</span>`;
        return;
    }

    const deltaClass = deltaNumber >= 0
        ? 'text-emerald-600 dark:text-emerald-400'
        : 'text-red-600 dark:text-red-400';
    const trendIcon = deltaNumber >= 0
        ? `
            <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M7 17L17 7M17 7H9M17 7v8"/>
            </svg>
        `
        : `
            <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M7 7l10 10M17 17H9M17 17V9"/>
            </svg>
        `;
    element.innerHTML = `
        <span class="dashboard-metric-number inline-flex items-center gap-1 text-base font-semibold ${deltaClass}">
            ${trendIcon}
            <span>${value}</span>
        </span>
    `;
}

function loadRegistrationsComparisonCards(days, idPrefix) {
    const {dateFrom, dateTo} = getLastDaysRange(days);
    const url = buildRegistrationsQueryUrl(DASHBOARD_ROUTES.getRegistrationsCompare, {
        date_from: dateFrom,
        date_to: dateTo,
    });

    fetchComparisonData(url)
        .then((data) => {
            const absDelta = Math.abs(data.delta);
            const absPercent = Math.abs(data.delta_percent);
            updateCompareCardValue(`${idPrefix}-current`, data.current_count);
            updateCompareCardValue(`${idPrefix}-previous`, data.previous_count);
            updateCompareCardValue(
                `${idPrefix}-delta`,
                `${absDelta} (${absPercent}%)`,
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

function loadAddedVisitedCitiesComparisonCards(days, idPrefix) {
    const {dateFrom, dateTo} = getLastDaysRange(days);
    const url = buildRegistrationsQueryUrl(DASHBOARD_ROUTES.getAddedVisitedCitiesCompare, {
        date_from: dateFrom,
        date_to: dateTo,
    });

    fetchComparisonData(url)
        .then((data) => {
            const absDelta = Math.abs(data.delta);
            const absPercent = Math.abs(data.delta_percent);
            updateCompareCardValue(`${idPrefix}-current`, data.current_count);
            updateCompareCardValue(`${idPrefix}-previous`, data.previous_count);
            updateCompareCardValue(
                `${idPrefix}-delta`,
                `${absDelta} (${absPercent}%)`,
                true,
                data.delta,
            );
        })
        .catch((error) => {
            console.error('Failed to fetch added visited cities comparison', error);
            showCardFallback(`${idPrefix}-current`);
            showCardFallback(`${idPrefix}-previous`);
            showCardFallback(`${idPrefix}-delta`);
        });
}

function loadRegistrationsTrendCardChart(canvasId, days, groupBy, tooltipMetricLabel, color) {
    const chartContainer = document.getElementById(canvasId);
    if (!chartContainer) {
        return;
    }
    const dayMonthYearFormatter = new Intl.DateTimeFormat('ru-RU', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
        timeZone: 'UTC',
    });
    const monthYearFormatter = new Intl.DateTimeFormat('ru-RU', {
        month: 'long',
        year: 'numeric',
        timeZone: 'UTC',
    });

    function parseIsoWeekStart(week, year) {
        const jan4 = new Date(Date.UTC(year, 0, 4));
        const jan4Day = jan4.getUTCDay() || 7;
        const mondayOfWeekOne = new Date(jan4);
        mondayOfWeekOne.setUTCDate(jan4.getUTCDate() - (jan4Day - 1));
        const target = new Date(mondayOfWeekOne);
        target.setUTCDate(mondayOfWeekOne.getUTCDate() + (week - 1) * 7);
        return target;
    }

    function formatPeriodValue(rawValue) {
        const value = String(rawValue ?? '').trim();
        if (!value) {
            return '—';
        }

        if (groupBy === 'day') {
            const dayMatch = /^(\d{2})\.(\d{2})\.(\d{4})$/.exec(value);
            if (!dayMatch) {
                return value;
            }
            const [, day, month, year] = dayMatch;
            const date = new Date(Date.UTC(Number(year), Number(month) - 1, Number(day)));
            return dayMonthYearFormatter.format(date);
        }

        if (groupBy === 'week') {
            const weekMatch = /^(\d{2})\.(\d{4})$/.exec(value);
            if (!weekMatch) {
                return value;
            }
            const [, week, year] = weekMatch;
            const weekStart = parseIsoWeekStart(Number(week), Number(year));
            return `неделя с ${dayMonthYearFormatter.format(weekStart)}`;
        }

        if (groupBy === 'month') {
            const monthMatch = /^(\d{2})\.(\d{4})$/.exec(value);
            if (!monthMatch) {
                return value;
            }
            const [, month, year] = monthMatch;
            const date = new Date(Date.UTC(Number(year), Number(month) - 1, 1));
            return monthYearFormatter.format(date);
        }

        return value;
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
            const chartLabels = labels.length === 1 ? [labels[0], labels[0]] : labels;
            const chartValues = values.length === 1 ? [values[0], values[0]] : values;
            chartContainer.innerHTML = '';

            const chart = new ApexCharts(chartContainer, {
                series: [
                    {
                        name: tooltipMetricLabel,
                        data: chartValues,
                    },
                ],
                chart: {
                    type: 'area',
                    height: '100%',
                    toolbar: {
                        show: false,
                    },
                    sparkline: {
                        enabled: true,
                    },
                },
                stroke: {
                    curve: 'straight',
                    width: 2,
                    colors: [color],
                },
                colors: [color],
                fill: {
                    type: 'gradient',
                    gradient: {
                        shade: 'dark',
                        gradientToColors: [color],
                        shadeIntensity: 1,
                        opacityFrom: 0.6,
                        opacityTo: 0,
                        stops: [0, 100],
                    },
                },
                states: {
                    normal: {
                        filter: {
                            type: 'none',
                        },
                    },
                    hover: {
                        filter: {
                            type: 'none',
                        },
                    },
                    active: {
                        filter: {
                            type: 'none',
                        },
                    },
                },
                xaxis: {
                    categories: chartLabels,
                },
                tooltip: {
                    custom({series, seriesIndex, dataPointIndex}) {
                        const rawLabel = chartLabels[dataPointIndex] || '';
                        const formattedDate = formatPeriodValue(rawLabel);
                        const value = series[seriesIndex][dataPointIndex];
                        return `
                            <div class="px-2 py-1 text-sm text-gray-700 dark:text-neutral-200">
                                ${formattedDate}: <span class="font-semibold">${value}</span>
                            </div>
                        `;
                    },
                },
            });
            chart.render();
        })
        .catch((error) => {
            console.error('Failed to fetch registrations trend chart', error);
        });
}

function loadAddedVisitedCitiesTrendCardChart(canvasId, days, groupBy, tooltipMetricLabel, color) {
    const chartContainer = document.getElementById(canvasId);
    if (!chartContainer) {
        return;
    }
    const dayMonthYearFormatter = new Intl.DateTimeFormat('ru-RU', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
        timeZone: 'UTC',
    });
    const monthYearFormatter = new Intl.DateTimeFormat('ru-RU', {
        month: 'long',
        year: 'numeric',
        timeZone: 'UTC',
    });

    function parseIsoWeekStart(week, year) {
        const jan4 = new Date(Date.UTC(year, 0, 4));
        const jan4Day = jan4.getUTCDay() || 7;
        const mondayOfWeekOne = new Date(jan4);
        mondayOfWeekOne.setUTCDate(jan4.getUTCDate() - (jan4Day - 1));
        const target = new Date(mondayOfWeekOne);
        target.setUTCDate(mondayOfWeekOne.getUTCDate() + (week - 1) * 7);
        return target;
    }

    function formatPeriodValue(rawValue) {
        const value = String(rawValue ?? '').trim();
        if (!value) {
            return '—';
        }

        if (groupBy === 'day') {
            const dayMatch = /^(\d{2})\.(\d{2})\.(\d{4})$/.exec(value);
            if (!dayMatch) {
                return value;
            }
            const [, day, month, year] = dayMatch;
            const date = new Date(Date.UTC(Number(year), Number(month) - 1, Number(day)));
            return dayMonthYearFormatter.format(date);
        }

        if (groupBy === 'week') {
            const weekMatch = /^(\d{2})\.(\d{4})$/.exec(value);
            if (!weekMatch) {
                return value;
            }
            const [, week, year] = weekMatch;
            const weekStart = parseIsoWeekStart(Number(week), Number(year));
            return `неделя с ${dayMonthYearFormatter.format(weekStart)}`;
        }

        if (groupBy === 'month') {
            const monthMatch = /^(\d{2})\.(\d{4})$/.exec(value);
            if (!monthMatch) {
                return value;
            }
            const [, month, year] = monthMatch;
            const date = new Date(Date.UTC(Number(year), Number(month) - 1, 1));
            return monthYearFormatter.format(date);
        }

        return value;
    }

    const {dateFrom, dateTo} = getLastDaysRange(days);
    const url = buildRegistrationsQueryUrl(DASHBOARD_ROUTES.getAddedVisitedCitiesByRange, {
        date_from: dateFrom,
        date_to: dateTo,
        group_by: groupBy,
    });

    fetchChartData(url)
        .then((data) => {
            const labels = data.map((item) => item.label);
            const values = data.map((item) => item.count);
            const chartLabels = labels.length === 1 ? [labels[0], labels[0]] : labels;
            const chartValues = values.length === 1 ? [values[0], values[0]] : values;
            chartContainer.innerHTML = '';

            const chart = new ApexCharts(chartContainer, {
                series: [
                    {
                        name: tooltipMetricLabel,
                        data: chartValues,
                    },
                ],
                chart: {
                    type: 'area',
                    height: '100%',
                    toolbar: {
                        show: false,
                    },
                    sparkline: {
                        enabled: true,
                    },
                },
                stroke: {
                    curve: 'straight',
                    width: 2,
                    colors: [color],
                },
                colors: [color],
                fill: {
                    type: 'gradient',
                    gradient: {
                        shade: 'dark',
                        gradientToColors: [color],
                        shadeIntensity: 1,
                        opacityFrom: 0.6,
                        opacityTo: 0,
                        stops: [0, 100],
                    },
                },
                states: {
                    normal: {
                        filter: {
                            type: 'none',
                        },
                    },
                    hover: {
                        filter: {
                            type: 'none',
                        },
                    },
                    active: {
                        filter: {
                            type: 'none',
                        },
                    },
                },
                xaxis: {
                    categories: chartLabels,
                },
                tooltip: {
                    custom({series, seriesIndex, dataPointIndex}) {
                        const rawLabel = chartLabels[dataPointIndex] || '';
                        const formattedDate = formatPeriodValue(rawLabel);
                        const value = series[seriesIndex][dataPointIndex];
                        return `
                            <div class="px-2 py-1 text-sm text-gray-700 dark:text-neutral-200">
                                ${formattedDate}: <span class="font-semibold">${value}</span>
                            </div>
                        `;
                    },
                },
            });
            chart.render();
        })
        .catch((error) => {
            console.error('Failed to fetch added visited cities trend chart', error);
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
        loadAddedVisitedCitiesComparisonCards(30, 'added-cities-30');
        loadAddedVisitedCitiesComparisonCards(183, 'added-cities-6m');
        loadAddedVisitedCitiesComparisonCards(365, 'added-cities-1y');
        loadRegistrationsTrendCardChart(
            'registrations-30-trend-chart',
            30,
            'day',
            'За день',
            '#2563eb'
        );
        loadRegistrationsTrendCardChart(
            'registrations-6m-trend-chart',
            183,
            'week',
            'За неделю',
            '#8b5cf6'
        );
        loadRegistrationsTrendCardChart(
            'registrations-1y-trend-chart',
            365,
            'month',
            'За месяц',
            '#f59e0b'
        );
        loadAddedVisitedCitiesTrendCardChart(
            'added-cities-30-trend-chart',
            30,
            'day',
            'За день',
            '#0ea5e9'
        );
        loadAddedVisitedCitiesTrendCardChart(
            'added-cities-6m-trend-chart',
            183,
            'week',
            'За неделю',
            '#10b981'
        );
        loadAddedVisitedCitiesTrendCardChart(
            'added-cities-1y-trend-chart',
            365,
            'month',
            'За месяц',
            '#f97316'
        );
    });
} else {
    loadVisitedCountriesChart();
    loadVisitedCitiesByUserChart();
    loadUniqueVisitedCitiesByUserChart();
    loadRegistrationsComparisonCards(30, 'registrations-30');
    loadRegistrationsComparisonCards(183, 'registrations-6m');
    loadRegistrationsComparisonCards(365, 'registrations-1y');
    loadAddedVisitedCitiesComparisonCards(30, 'added-cities-30');
    loadAddedVisitedCitiesComparisonCards(183, 'added-cities-6m');
    loadAddedVisitedCitiesComparisonCards(365, 'added-cities-1y');
    loadRegistrationsTrendCardChart(
        'registrations-30-trend-chart',
        30,
        'day',
        'За день',
        '#2563eb'
    );
    loadRegistrationsTrendCardChart(
        'registrations-6m-trend-chart',
        183,
        'week',
        'За неделю',
        '#8b5cf6'
    );
    loadRegistrationsTrendCardChart(
        'registrations-1y-trend-chart',
        365,
        'month',
        'За месяц',
        '#f59e0b'
    );
    loadAddedVisitedCitiesTrendCardChart(
        'added-cities-30-trend-chart',
        30,
        'day',
        'За день',
        '#0ea5e9'
    );
    loadAddedVisitedCitiesTrendCardChart(
        'added-cities-6m-trend-chart',
        183,
        'week',
        'За неделю',
        '#10b981'
    );
    loadAddedVisitedCitiesTrendCardChart(
        'added-cities-1y-trend-chart',
        365,
        'month',
        'За месяц',
        '#f97316'
    );
}

function updateNumberOnCard(element_id, newNumber) {
    const el = document.getElementById(element_id);
    if (!el) {
        return;
    }
    const halfUserCardsIds = new Set([
        'number-total_users',
        'number-number_of_users_without_visited_cities',
        'number-total_visited_cities_visits',
        'number-unique_visited_cities',
    ]);
    const numberClass = halfUserCardsIds.has(element_id)
        ? 'dashboard-metric-number text-4xl font-bold leading-none text-gray-900 dark:text-white'
        : 'dashboard-metric-number text-2xl font-bold text-gray-900 dark:text-white';
    el.innerHTML = `<span class="${numberClass}">${newNumber}</span>`;
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