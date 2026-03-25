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
    getAddedVisitedCountriesByRange: '/api/dashboard/visited_countries/added/range/',
    getAddedVisitedCountriesCompare: '/api/dashboard/visited_countries/added/compare/',
    // Места
    getTotalVisitedPlaces: '/api/dashboard/places/visited/total/',
    getTotalVisitedOnlyPlaces: '/api/dashboard/places/visited/visited_only_total/',
    getPlacesByRange: '/api/dashboard/places/visited/range/',
    getPlacesCompare: '/api/dashboard/places/visited/compare/',
    getTotalPersonalCollections: '/api/dashboard/places/personal_collections/total/',
    getTotalPublicPersonalCollections: '/api/dashboard/places/personal_collections/public_total/',
    getPersonalCollectionsByRange: '/api/dashboard/places/personal_collections/range/',
    getPersonalCollectionsCompare: '/api/dashboard/places/personal_collections/compare/',
    // Блог
    getBlogLastAddedArticles: '/api/dashboard/blog/articles/last_added/',
    getBlogTopViewedArticles: '/api/dashboard/blog/articles/top_views/',
    getBlogAddedByRange: '/api/dashboard/blog/articles/added/range/',
    getBlogAddedCompare: '/api/dashboard/blog/articles/added/compare/',
    getBlogViewsByRange: '/api/dashboard/blog/articles/views/range/',
    getBlogViewsCompare: '/api/dashboard/blog/articles/views/compare/',
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
// Места
loadQuantityCard('number-total_visited_places', DASHBOARD_ROUTES.getTotalVisitedPlaces);
loadQuantityCard('number-total_visited_only_places', DASHBOARD_ROUTES.getTotalVisitedOnlyPlaces);
loadQuantityCard('number-total_personal_collections', DASHBOARD_ROUTES.getTotalPersonalCollections);
loadQuantityCard(
    'number-total_public_personal_collections',
    DASHBOARD_ROUTES.getTotalPublicPersonalCollections
);

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

function loadAddedVisitedCountriesComparisonCards(days, idPrefix) {
    const {dateFrom, dateTo} = getLastDaysRange(days);
    const url = buildRegistrationsQueryUrl(DASHBOARD_ROUTES.getAddedVisitedCountriesCompare, {
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
            console.error('Failed to fetch added visited countries comparison', error);
            showCardFallback(`${idPrefix}-current`);
            showCardFallback(`${idPrefix}-previous`);
            showCardFallback(`${idPrefix}-delta`);
        });
}

function loadPlacesComparisonCards(days, idPrefix) {
    const {dateFrom, dateTo} = getLastDaysRange(days);
    const url = buildRegistrationsQueryUrl(DASHBOARD_ROUTES.getPlacesCompare, {
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
            console.error('Failed to fetch places comparison', error);
            showCardFallback(`${idPrefix}-current`);
            showCardFallback(`${idPrefix}-previous`);
            showCardFallback(`${idPrefix}-delta`);
        });
}

function loadPersonalCollectionsComparisonCards(days, idPrefix) {
    const {dateFrom, dateTo} = getLastDaysRange(days);
    const url = buildRegistrationsQueryUrl(DASHBOARD_ROUTES.getPersonalCollectionsCompare, {
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
            console.error('Failed to fetch personal collections comparison', error);
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

function loadAddedVisitedCountriesTrendCardChart(canvasId, days, groupBy, tooltipMetricLabel, color) {
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
    const url = buildRegistrationsQueryUrl(DASHBOARD_ROUTES.getAddedVisitedCountriesByRange, {
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
            console.error('Failed to fetch added visited countries trend chart', error);
        });
}

function loadPlacesTrendCardChart(canvasId, days, groupBy, tooltipMetricLabel, color) {
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
    const url = buildRegistrationsQueryUrl(DASHBOARD_ROUTES.getPlacesByRange, {
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
            console.error('Failed to fetch places trend chart', error);
        });
}

function loadPersonalCollectionsTrendCardChart(canvasId, days, groupBy, tooltipMetricLabel, color) {
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
    const url = buildRegistrationsQueryUrl(DASHBOARD_ROUTES.getPersonalCollectionsByRange, {
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
            console.error('Failed to fetch personal collections trend chart', error);
        });
}

const BLOG_ARTICLES_PER_PAGE = 10;

function formatRuNumber(value) {
    return new Intl.NumberFormat('ru-RU').format(value ?? 0);
}

function escapeHtml(value) {
    return String(value ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
}

async function fetchBlogArticlesPage(page) {
    const url = buildRegistrationsQueryUrl(DASHBOARD_ROUTES.getBlogArticles, {
        page,
        per_page: BLOG_ARTICLES_PER_PAGE,
    });

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
        !data ||
        !Array.isArray(data.items) ||
        typeof data.page !== 'number' ||
        typeof data.total_pages !== 'number'
    ) {
        throw new Error('Unexpected response structure for blog articles page');
    }

    return data;
}

function buildBlogPageHref(targetPage) {
    const url = new URL(window.location.href);
    url.searchParams.set('blog_page', String(targetPage));
    return `${url.pathname}?${url.searchParams.toString()}`;
}

function renderBlogArticlesPagination(page, totalPages) {
    const container = document.getElementById('blog-articles-pagination');
    if (!container) {
        return;
    }

    if (!totalPages || totalPages <= 1) {
        container.innerHTML = '';
        return;
    }

    const prevDisabled = page <= 1;
    const nextDisabled = page >= totalPages;

    container.innerHTML = `
        <nav class="flex items-center justify-center gap-2 text-sm" aria-label="Пагинация статей блога">
            ${
                prevDisabled
                    ? `<span class="inline-flex items-center rounded-full bg-gray-100 px-3 py-1.5 text-gray-400 dark:bg-neutral-800 dark:text-neutral-500" aria-disabled="true">Назад</span>`
                    : `<a href="${buildBlogPageHref(page - 1)}" class="inline-flex items-center rounded-full bg-gray-100 px-3 py-1.5 text-gray-700 transition hover:bg-gray-200 dark:bg-neutral-800 dark:text-neutral-200 dark:hover:bg-neutral-700">Назад</a>`
            }
            <span class="inline-flex items-center rounded-full bg-gray-100 px-3 py-1.5 text-gray-700 font-medium dark:bg-neutral-800 dark:text-neutral-200">
                ${page} из ${totalPages}
            </span>
            ${
                nextDisabled
                    ? `<span class="inline-flex items-center rounded-full bg-gray-100 px-3 py-1.5 text-gray-400 dark:bg-neutral-800 dark:text-neutral-500" aria-disabled="true">Вперёд</span>`
                    : `<a href="${buildBlogPageHref(page + 1)}" class="inline-flex items-center rounded-full bg-gray-100 px-3 py-1.5 text-gray-700 transition hover:bg-gray-200 dark:bg-neutral-800 dark:text-neutral-200 dark:hover:bg-neutral-700">Вперёд</a>`
            }
        </nav>
    `;
}

function renderBlogArticlesTable(items) {
    const tbody = document.getElementById('blog-articles-table-body');
    if (!tbody) {
        return;
    }

    if (!items || items.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="3" class="py-4 text-center text-sm text-gray-600 dark:text-neutral-400">
                    На данный момент нет ни одной статьи.
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = items
        .map(
            (item) => `
            <tr class="border-t border-gray-200 hover:bg-gray-50 dark:border-neutral-700 dark:hover:bg-neutral-800">
                <td class="py-3 pr-3">
                    <a href="${item.detail_url}" class="font-medium text-blue-600 dark:text-blue-400 hover:underline">
                        ${escapeHtml(item.title)}
                    </a>
                </td>
                <td class="py-3 whitespace-nowrap text-gray-600 dark:text-neutral-400">
                    ${escapeHtml(item.published_date)}
                </td>
                <td class="py-3 whitespace-nowrap text-right text-gray-900 dark:text-white font-semibold">
                    ${formatRuNumber(item.view_count_total)}
                </td>
            </tr>
        `,
        )
        .join('');
}

function initBlogArticlesTable() {
    const tbody = document.getElementById('blog-articles-table-body');
    if (!tbody) {
        return;
    }

    const url = new URL(window.location.href);
    const rawPage = parseInt(url.searchParams.get('blog_page') ?? '1', 10);
    const page = Number.isFinite(rawPage) && rawPage > 0 ? rawPage : 1;

    tbody.innerHTML = `
        <tr>
            <td colspan="3" class="py-4 text-center text-sm text-gray-600 dark:text-neutral-400">
                Загрузка...
            </td>
        </tr>
    `;

    fetchBlogArticlesPage(page)
        .then((data) => {
            renderBlogArticlesTable(data.items);
            renderBlogArticlesPagination(data.page, data.total_pages);
        })
        .catch((error) => {
            console.error('Failed to fetch blog articles page', error);
            tbody.innerHTML = `
                <tr>
                    <td colspan="3" class="py-4 text-center text-sm text-gray-600 dark:text-neutral-400">
                        Не удалось загрузить список статей
                    </td>
                </tr>
            `;
        });
}

function loadBlogViewsTrendChart() {
    const chartContainer = document.getElementById('blog-articles-views-60d-trend-chart');
    if (!chartContainer) {
        return;
    }

    const dayMonthYearFormatter = new Intl.DateTimeFormat('ru-RU', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
        timeZone: 'UTC',
    });

    function formatDayLabel(rawValue) {
        const value = String(rawValue ?? '').trim();
        if (!value) {
            return '—';
        }
        const dayMatch = /^(\d{2})\.(\d{2})\.(\d{4})$/.exec(value);
        if (!dayMatch) {
            return value;
        }
        const [, day, month, year] = dayMatch;
        const date = new Date(Date.UTC(Number(year), Number(month) - 1, Number(day)));
        return dayMonthYearFormatter.format(date);
    }

    const {dateFrom, dateTo} = getLastDaysRange(60);
    const url = buildRegistrationsQueryUrl(DASHBOARD_ROUTES.getBlogViewsByRange, {
        date_from: dateFrom,
        date_to: dateTo,
        group_by: 'day',
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
                        name: 'Просмотры',
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
                    colors: ['#2563eb'],
                },
                colors: ['#2563eb'],
                fill: {
                    type: 'gradient',
                    gradient: {
                        shade: 'dark',
                        gradientToColors: ['#2563eb'],
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
                        const formattedDate = formatDayLabel(rawLabel);
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
            console.error('Failed to fetch blog views trend chart', error);
        });
}

async function fetchBlogArticlesList(url) {
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

function renderBlogArticlesTableBody(tbodyId, items) {
    const tbody = document.getElementById(tbodyId);
    if (!tbody) {
        return;
    }

    if (!items || items.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="3" class="py-4 text-center text-sm text-gray-600 dark:text-neutral-400">
                    На данный момент нет ни одной статьи.
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = items
        .map(
            (item) => `
            <tr class="border-t border-gray-200 hover:bg-gray-50 dark:border-neutral-700 dark:hover:bg-neutral-800">
                <td class="py-3 pr-3">
                    <a href="${item.detail_url}" class="font-medium text-blue-600 dark:text-blue-400 hover:underline">
                        ${escapeHtml(item.title)}
                    </a>
                </td>
                <td class="py-3 whitespace-nowrap text-gray-600 dark:text-neutral-400">
                    ${escapeHtml(item.published_date)}
                </td>
                <td class="py-3 whitespace-nowrap text-right text-gray-900 dark:text-white font-semibold">
                    ${formatRuNumber(item.view_count_total)}
                </td>
            </tr>
        `,
        )
        .join('');
}

async function loadBlogAddedCard(days) {
    const idPrefix = `blog-added-${days}`;
    const currentChartId = `blog-added-articles-${days}-trend-chart`;
    const tableBodyId = 'blog-added-articles-table-body';

    const {dateFrom, dateTo} = getLastDaysRange(days);
    const compareUrl = buildRegistrationsQueryUrl(DASHBOARD_ROUTES.getBlogAddedCompare, {
        date_from: dateFrom,
        date_to: dateTo,
    });

    fetchComparisonData(compareUrl)
        .then((data) => {
            const absDelta = Math.abs(data.delta);
            const absPercent = Math.abs(data.delta_percent);
            updateCompareCardValue(`${idPrefix}-current`, data.current_count);
            updateCompareCardValue(`${idPrefix}-previous`, data.previous_count);
            updateCompareCardValue(
                `${idPrefix}-delta`,
                `${absDelta} (${absPercent}%)`,
                true,
                data.delta
            );
        })
        .catch((error) => {
            console.error('Failed to fetch blog added comparison', error);
            showCardFallback(`${idPrefix}-current`);
            showCardFallback(`${idPrefix}-previous`);
            showCardFallback(`${idPrefix}-delta`);
        });

    fetchBlogArticlesList(DASHBOARD_ROUTES.getBlogLastAddedArticles)
        .then((items) => renderBlogArticlesTableBody(tableBodyId, items))
        .catch((error) => {
            console.error('Failed to fetch last added blog articles', error);
            renderBlogArticlesTableBody(tableBodyId, []);
        });

    const chartContainer = document.getElementById(currentChartId);
    if (!chartContainer) {
        return;
    }

    const dayMonthYearFormatter = new Intl.DateTimeFormat('ru-RU', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
        timeZone: 'UTC',
    });

    function formatDayLabel(rawValue) {
        const value = String(rawValue ?? '').trim();
        if (!value) {
            return '—';
        }
        const dayMatch = /^(\d{2})\.(\d{2})\.(\d{4})$/.exec(value);
        if (!dayMatch) {
            return value;
        }
        const [, day, month, year] = dayMatch;
        const date = new Date(Date.UTC(Number(year), Number(month) - 1, Number(day)));
        return dayMonthYearFormatter.format(date);
    }

    const chartUrl = buildRegistrationsQueryUrl(DASHBOARD_ROUTES.getBlogAddedByRange, {
        date_from: dateFrom,
        date_to: dateTo,
        group_by: 'day',
    });

    fetchChartData(chartUrl)
        .then((data) => {
            const labels = data.map((item) => item.label);
            const values = data.map((item) => item.count);
            const chartLabels = labels.length === 1 ? [labels[0], labels[0]] : labels;
            const chartValues = values.length === 1 ? [values[0], values[0]] : values;
            chartContainer.innerHTML = '';

            const chart = new ApexCharts(chartContainer, {
                series: [
                    {
                        name: 'Добавления',
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
                    colors: ['#06b6d4'],
                },
                colors: ['#06b6d4'],
                fill: {
                    type: 'gradient',
                    gradient: {
                        shade: 'dark',
                        gradientToColors: ['#06b6d4'],
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
                        const formattedDate = formatDayLabel(rawLabel);
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
            console.error('Failed to fetch blog added trend chart', error);
        });
}

async function loadBlogTopViewsCard(days) {
    const idPrefix = `blog-top-views-${days}`;
    const currentChartId = `blog-top-views-${days}-trend-chart`;
    const tableBodyId = 'blog-top-views-table-body';

    const {dateFrom, dateTo} = getLastDaysRange(days);
    const compareUrl = buildRegistrationsQueryUrl(DASHBOARD_ROUTES.getBlogViewsCompare, {
        date_from: dateFrom,
        date_to: dateTo,
    });

    fetchComparisonData(compareUrl)
        .then((data) => {
            const absDelta = Math.abs(data.delta);
            const absPercent = Math.abs(data.delta_percent);
            updateCompareCardValue(`${idPrefix}-current`, data.current_count);
            updateCompareCardValue(`${idPrefix}-previous`, data.previous_count);
            updateCompareCardValue(
                `${idPrefix}-delta`,
                `${absDelta} (${absPercent}%)`,
                true,
                data.delta
            );
        })
        .catch((error) => {
            console.error('Failed to fetch blog views comparison', error);
            showCardFallback(`${idPrefix}-current`);
            showCardFallback(`${idPrefix}-previous`);
            showCardFallback(`${idPrefix}-delta`);
        });

    fetchBlogArticlesList(DASHBOARD_ROUTES.getBlogTopViewedArticles)
        .then((items) => renderBlogArticlesTableBody(tableBodyId, items))
        .catch((error) => {
            console.error('Failed to fetch top viewed blog articles', error);
            renderBlogArticlesTableBody(tableBodyId, []);
        });

    const chartContainer = document.getElementById(currentChartId);
    if (!chartContainer) {
        return;
    }

    const dayMonthYearFormatter = new Intl.DateTimeFormat('ru-RU', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
        timeZone: 'UTC',
    });

    function formatDayLabel(rawValue) {
        const value = String(rawValue ?? '').trim();
        if (!value) {
            return '—';
        }
        const dayMatch = /^(\d{2})\.(\d{2})\.(\d{4})$/.exec(value);
        if (!dayMatch) {
            return value;
        }
        const [, day, month, year] = dayMatch;
        const date = new Date(Date.UTC(Number(year), Number(month) - 1, Number(day)));
        return dayMonthYearFormatter.format(date);
    }

    const chartUrl = buildRegistrationsQueryUrl(DASHBOARD_ROUTES.getBlogViewsByRange, {
        date_from: dateFrom,
        date_to: dateTo,
        group_by: 'day',
    });

    fetchChartData(chartUrl)
        .then((data) => {
            const labels = data.map((item) => item.label);
            const values = data.map((item) => item.count);
            const chartLabels = labels.length === 1 ? [labels[0], labels[0]] : labels;
            const chartValues = values.length === 1 ? [values[0], values[0]] : values;
            chartContainer.innerHTML = '';

            const chart = new ApexCharts(chartContainer, {
                series: [
                    {
                        name: 'Просмотры',
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
                    colors: ['#2563eb'],
                },
                colors: ['#2563eb'],
                fill: {
                    type: 'gradient',
                    gradient: {
                        shade: 'dark',
                        gradientToColors: ['#2563eb'],
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
                        const formattedDate = formatDayLabel(rawLabel);
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
            console.error('Failed to fetch blog views trend chart', error);
        });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        loadVisitedCitiesByUserChart();
        loadUniqueVisitedCitiesByUserChart();
        loadRegistrationsComparisonCards(30, 'registrations-30');
        loadRegistrationsComparisonCards(183, 'registrations-6m');
        loadRegistrationsComparisonCards(365, 'registrations-1y');
        loadAddedVisitedCitiesComparisonCards(30, 'added-cities-30');
        loadAddedVisitedCitiesComparisonCards(183, 'added-cities-6m');
        loadAddedVisitedCitiesComparisonCards(365, 'added-cities-1y');
        loadAddedVisitedCountriesComparisonCards(30, 'added-countries-30');
        loadAddedVisitedCountriesComparisonCards(183, 'added-countries-6m');
        loadAddedVisitedCountriesComparisonCards(365, 'added-countries-1y');
        loadPlacesComparisonCards(30, 'places-30');
        loadPlacesComparisonCards(183, 'places-6m');
        loadPlacesComparisonCards(365, 'places-1y');
        loadPersonalCollectionsComparisonCards(30, 'collections-30');
        loadPersonalCollectionsComparisonCards(183, 'collections-6m');
        loadPersonalCollectionsComparisonCards(365, 'collections-1y');
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
        loadAddedVisitedCountriesTrendCardChart(
            'added-countries-30-trend-chart',
            30,
            'day',
            'За день',
            '#2563eb'
        );
        loadAddedVisitedCountriesTrendCardChart(
            'added-countries-6m-trend-chart',
            183,
            'week',
            'За неделю',
            '#8b5cf6'
        );
        loadAddedVisitedCountriesTrendCardChart(
            'added-countries-1y-trend-chart',
            365,
            'month',
            'За месяц',
            '#f59e0b'
        );
        loadPlacesTrendCardChart('places-30-trend-chart', 30, 'day', 'За день', '#06b6d4');
        loadPlacesTrendCardChart('places-6m-trend-chart', 183, 'week', 'За неделю', '#22c55e');
        loadPlacesTrendCardChart('places-1y-trend-chart', 365, 'month', 'За месяц', '#f97316');
        loadPersonalCollectionsTrendCardChart(
            'collections-30-trend-chart',
            30,
            'day',
            'За день',
            '#2563eb'
        );
        loadPersonalCollectionsTrendCardChart(
            'collections-6m-trend-chart',
            183,
            'week',
            'За неделю',
            '#8b5cf6'
        );
        loadPersonalCollectionsTrendCardChart(
            'collections-1y-trend-chart',
            365,
            'month',
            'За месяц',
            '#f59e0b'
        );
        loadBlogAddedCard(30);
        loadBlogTopViewsCard(60);
    });
} else {
    loadVisitedCitiesByUserChart();
    loadUniqueVisitedCitiesByUserChart();
    loadRegistrationsComparisonCards(30, 'registrations-30');
    loadRegistrationsComparisonCards(183, 'registrations-6m');
    loadRegistrationsComparisonCards(365, 'registrations-1y');
    loadAddedVisitedCitiesComparisonCards(30, 'added-cities-30');
    loadAddedVisitedCitiesComparisonCards(183, 'added-cities-6m');
    loadAddedVisitedCitiesComparisonCards(365, 'added-cities-1y');
    loadAddedVisitedCountriesComparisonCards(30, 'added-countries-30');
    loadAddedVisitedCountriesComparisonCards(183, 'added-countries-6m');
    loadAddedVisitedCountriesComparisonCards(365, 'added-countries-1y');
    loadPlacesComparisonCards(30, 'places-30');
    loadPlacesComparisonCards(183, 'places-6m');
    loadPlacesComparisonCards(365, 'places-1y');
    loadPersonalCollectionsComparisonCards(30, 'collections-30');
    loadPersonalCollectionsComparisonCards(183, 'collections-6m');
    loadPersonalCollectionsComparisonCards(365, 'collections-1y');
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
    loadAddedVisitedCountriesTrendCardChart(
        'added-countries-30-trend-chart',
        30,
        'day',
        'За день',
        '#2563eb'
    );
    loadAddedVisitedCountriesTrendCardChart(
        'added-countries-6m-trend-chart',
        183,
        'week',
        'За неделю',
        '#8b5cf6'
    );
    loadAddedVisitedCountriesTrendCardChart(
        'added-countries-1y-trend-chart',
        365,
        'month',
        'За месяц',
        '#f59e0b'
    );
    loadPlacesTrendCardChart('places-30-trend-chart', 30, 'day', 'За день', '#06b6d4');
    loadPlacesTrendCardChart('places-6m-trend-chart', 183, 'week', 'За неделю', '#22c55e');
    loadPlacesTrendCardChart('places-1y-trend-chart', 365, 'month', 'За месяц', '#f97316');
    loadPersonalCollectionsTrendCardChart(
        'collections-30-trend-chart',
        30,
        'day',
        'За день',
        '#2563eb'
    );
    loadPersonalCollectionsTrendCardChart(
        'collections-6m-trend-chart',
        183,
        'week',
        'За неделю',
        '#8b5cf6'
    );
    loadPersonalCollectionsTrendCardChart(
        'collections-1y-trend-chart',
        365,
        'month',
        'За месяц',
        '#f59e0b'
    );
    loadBlogAddedCard(30);
    loadBlogTopViewsCard(60);
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
        'number-total_visited_countries',
        'number-user_with_visited_countries',
        'number-total_visited_places',
        'number-total_visited_only_places',
        'number-total_personal_collections',
        'number-total_public_personal_collections',
    ]);
    const numberClass = halfUserCardsIds.has(element_id)
        ? 'dashboard-metric-number text-5xl font-extrabold leading-none text-gray-900 dark:text-white'
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