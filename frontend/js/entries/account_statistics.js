import ApexCharts from 'apexcharts';
import {getCookie} from '../components/get_cookie.js';

const ACCOUNT_STATS_ROUTES = Object.freeze({
    getVisitedCitiesOverview: '/api/account/stats/visited_cities/overview/',
    getVisitedCitiesCountriesCoverage: '/api/account/stats/visited_cities/countries_coverage/',
    getVisitedCitiesCountriesVisits: '/api/account/stats/visited_cities/countries_visits/',
    getVisitedRegionsCountriesCoverage: '/api/account/stats/regions/countries_coverage/',
    getRegionsVisitedCitiesTreemap: '/api/account/stats/regions/visited_cities_treemap/',
    getRegionsCountries: '/api/country/list_by_cities',
});

const treemapState = {
    selectedCountryCode: 'RU',
    requestId: 0,
    fetchController: null,
    chartInstance: null,
};
const TREEMAP_LABEL_MAX = 28;
const TREEMAP_COLOR_BY_TEN_PERCENT = [
    '#b91c1c', // 0-9%
    '#dc2626', // 10-19%
    '#ea580c', // 20-29%
    '#f59e0b', // 30-39%
    '#eab308', // 40-49%
    '#84cc16', // 50-59%
    '#22c55e', // 60-69%
    '#14b8a6', // 70-79%
    '#06b6d4', // 80-89%
    '#3b82f6', // 90-99%
];
const TREEMAP_FULL_COVERAGE_COLOR = '#8b5cf6'; // 100%
const TREEMAP_LOADING_HTML = `
    <div class="animate-spin inline-block h-7 w-7 rounded-full border-[3px] border-current border-t-transparent text-blue-600 dark:text-blue-400" role="status" aria-label="loading">
        <span class="sr-only">Загрузка...</span>
    </div>
`;

async function apiGet(url, {signal} = {}) {
    const response = await fetch(url, {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            Accept: 'application/json',
        },
        credentials: 'same-origin',
        signal,
    });
    if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
    }
    return await response.json();
}

function formatRuNumber(value) {
    return new Intl.NumberFormat('ru-RU').format(value ?? 0);
}

function updateNumberOnCard(elementId, value) {
    const element = document.getElementById(elementId);
    if (!element) {
        return;
    }

    element.innerHTML = `
        <span class="dashboard-metric-number text-5xl font-extrabold leading-none text-gray-900 dark:text-white">
            ${formatRuNumber(value)}
        </span>
    `;
}

function updateRankBadge(elementId, rank, totalUsersCount, metricLabel) {
    const badgeElement = document.getElementById(elementId);
    if (!badgeElement) {
        return;
    }

    if (!Number.isFinite(rank) || rank <= 0 || !Number.isFinite(totalUsersCount) || totalUsersCount <= 0) {
        badgeElement.classList.add('hidden');
        badgeElement.innerHTML = '';
        badgeElement.removeAttribute('title');
        return;
    }

    badgeElement.textContent = `${formatRuNumber(rank)} место`;
    badgeElement.title = `Вы занимаете ${formatRuNumber(rank)} место из ${formatRuNumber(totalUsersCount)} пользователей сервиса по количеству ${metricLabel}`;
    badgeElement.classList.remove('hidden');
}

function renderCountriesCoverageCards(countries) {
    const loadingElement = document.getElementById('countries-coverage-cards-loading');
    const cardsContainer = document.getElementById('countries-coverage-cards');
    if (!loadingElement || !cardsContainer) {
        return;
    }

    const items = Array.isArray(countries)
        ? countries.filter((country) => Number(country?.visited_cities || 0) > 0)
        : [];
    const sortedItems = [...items].sort(
        (a, b) => Number(b?.visited_cities || 0) - Number(a?.visited_cities || 0)
    );

    if (sortedItems.length === 0) {
        loadingElement.classList.remove('hidden');
        cardsContainer.classList.add('hidden');
        loadingElement.innerHTML = `
            <div class="col-span-full rounded-xl border border-gray-200 bg-white p-4 text-sm text-gray-600 shadow-sm dark:border-neutral-700 dark:bg-neutral-900 dark:text-neutral-400">
                Пока нет данных по посещённым городам в странах.
            </div>
        `;
        return;
    }

    cardsContainer.innerHTML = sortedItems
        .map((country) => {
            const visitedCities = Number(country?.visited_cities || 0);
            const totalCities = Number(country?.total_cities || 0);
            const rank = Number(country?.rank || 0);
            const totalUsersCount = Number(country?.total_users_count || 0);
            const widthPercent = totalCities > 0 ? Math.round((visitedCities / totalCities) * 100) : 0;
            const countryName = String(country?.name || '—');
            const rankBadgeHtml =
                Number.isFinite(rank) && rank > 0 && Number.isFinite(totalUsersCount) && totalUsersCount > 0
                    ? `<span class="badge badge-soft-outline-secondary badge-pill badge-compact whitespace-nowrap" title="Вы занимаете ${formatRuNumber(rank)} место из ${formatRuNumber(totalUsersCount)} пользователей сервиса по количеству посещённых городов в этой стране">${formatRuNumber(rank)} место</span>`
                    : '';
            return `
                <div class="rounded-xl border border-gray-200 bg-white p-4 shadow-sm dark:border-neutral-700 dark:bg-neutral-900">
                    <div class="mb-3 flex items-start justify-between gap-3">
                        <p class="text-sm font-semibold text-gray-900 dark:text-white">${countryName}</p>
                        ${rankBadgeHtml}
                    </div>
                    <div class="mb-3">
                        <p class="dashboard-metric-number text-2xl font-extrabold leading-none text-gray-900 dark:text-white">
                            ${formatRuNumber(visitedCities)} из ${formatRuNumber(totalCities)}
                        </p>
                    </div>
                    <div class="mt-6 h-1.5 w-full rounded-full bg-gray-200 dark:bg-neutral-700">
                        <div class="h-1.5 rounded-full bg-emerald-500" style="width: ${widthPercent}%"></div>
                    </div>
                </div>
            `;
        })
        .join('');

    loadingElement.classList.add('hidden');
    cardsContainer.classList.remove('hidden');
}

function renderRegionsCoverageCards(countries) {
    const loadingElement = document.getElementById('regions-coverage-cards-loading');
    const cardsContainer = document.getElementById('regions-coverage-cards');
    if (!loadingElement || !cardsContainer) {
        return;
    }

    const items = Array.isArray(countries)
        ? countries.filter((country) => Number(country?.visited_regions || 0) > 0)
        : [];
    const sortedItems = [...items].sort(
        (a, b) => Number(b?.visited_regions || 0) - Number(a?.visited_regions || 0)
    );

    if (sortedItems.length === 0) {
        loadingElement.classList.remove('hidden');
        cardsContainer.classList.add('hidden');
        loadingElement.innerHTML = `
            <div class="col-span-full rounded-xl border border-gray-200 bg-white p-4 text-sm text-gray-600 shadow-sm dark:border-neutral-700 dark:bg-neutral-900 dark:text-neutral-400">
                Пока нет данных по посещённым регионам в странах.
            </div>
        `;
        return;
    }

    cardsContainer.innerHTML = sortedItems
        .map((country) => {
            const visitedRegions = Number(country?.visited_regions || 0);
            const totalRegions = Number(country?.total_regions || 0);
            const widthPercent = totalRegions > 0 ? Math.round((visitedRegions / totalRegions) * 100) : 0;
            const countryName = String(country?.name || '—');
            return `
                <div class="rounded-xl border border-gray-200 bg-white p-4 shadow-sm dark:border-neutral-700 dark:bg-neutral-900">
                    <div class="mb-3 flex items-start justify-between gap-3">
                        <p class="text-sm font-semibold text-gray-900 dark:text-white">${countryName}</p>
                        <p class="whitespace-nowrap text-sm font-semibold text-gray-700 dark:text-neutral-300">
                            ${formatRuNumber(visitedRegions)} из ${formatRuNumber(totalRegions)}
                        </p>
                    </div>
                    <div class="mt-6 h-1.5 w-full rounded-full bg-gray-200 dark:bg-neutral-700">
                        <div class="h-1.5 rounded-full bg-indigo-500" style="width: ${widthPercent}%"></div>
                    </div>
                </div>
            `;
        })
        .join('');

    loadingElement.classList.add('hidden');
    cardsContainer.classList.remove('hidden');
}

function renderCountriesVisitsCards(countries) {
    const loadingElement = document.getElementById('countries-visits-cards-loading');
    const cardsContainer = document.getElementById('countries-visits-cards');
    if (!loadingElement || !cardsContainer) {
        return;
    }

    const items = Array.isArray(countries)
        ? countries.filter((country) => Number(country?.visits || 0) > 0)
        : [];
    const sortedItems = [...items].sort(
        (a, b) => Number(b?.visits || 0) - Number(a?.visits || 0)
    );

    if (sortedItems.length === 0) {
        loadingElement.classList.remove('hidden');
        cardsContainer.classList.add('hidden');
        loadingElement.innerHTML = `
            <div class="col-span-full rounded-xl border border-gray-200 bg-white p-4 text-sm text-gray-600 shadow-sm dark:border-neutral-700 dark:bg-neutral-900 dark:text-neutral-400">
                Пока нет данных по посещениям городов в странах.
            </div>
        `;
        return;
    }

    cardsContainer.innerHTML = sortedItems
        .map((country) => {
            const visits = Number(country?.visits || 0);
            const rank = Number(country?.rank || 0);
            const totalUsersCount = Number(country?.total_users_count || 0);
            const countryName = String(country?.name || '—');
            const rankBadgeHtml =
                Number.isFinite(rank) && rank > 0 && Number.isFinite(totalUsersCount) && totalUsersCount > 0
                    ? `<span class="badge badge-soft-outline-secondary badge-pill badge-compact whitespace-nowrap" title="Вы занимаете ${formatRuNumber(rank)} место из ${formatRuNumber(totalUsersCount)} пользователей сервиса по количеству посещений городов в этой стране">${formatRuNumber(rank)} место</span>`
                    : '';
            return `
                <div class="rounded-xl border border-gray-200 bg-white p-4 shadow-sm dark:border-neutral-700 dark:bg-neutral-900">
                    <div class="mb-3 flex items-start justify-between gap-3">
                        <p class="text-sm font-semibold text-gray-900 dark:text-white">${countryName}</p>
                        ${rankBadgeHtml}
                    </div>
                    <div class="mb-3">
                        <p class="dashboard-metric-number text-5xl font-extrabold leading-none text-gray-900 dark:text-white">
                            ${formatRuNumber(visits)}
                        </p>
                    </div>
                </div>
            `;
        })
        .join('');

    loadingElement.classList.add('hidden');
    cardsContainer.classList.remove('hidden');
}

function renderTrendChart(containerId, chartData, seriesName, color) {
    const chartContainer = document.getElementById(containerId);
    if (!chartContainer) {
        return;
    }

    if (!Array.isArray(chartData) || chartData.length === 0) {
        chartContainer.innerHTML = '<p class="text-gray-600 dark:text-neutral-400">Нет данных</p>';
        return;
    }

    const labels = chartData.map((item) => item.label);
    const values = chartData.map((item) => item.count);
    const chartLabels = labels.length === 1 ? [labels[0], labels[0]] : labels;
    const chartValues = values.length === 1 ? [values[0], values[0]] : values;

    chartContainer.innerHTML = '';

    const chart = new ApexCharts(chartContainer, {
        series: [
            {
                name: seriesName,
                data: chartValues,
            },
        ],
        chart: {
            type: 'area',
            height: '100%',
            toolbar: {
                show: false,
            },
            zoom: {
                enabled: false,
                allowMouseWheelZoom: false,
            },
            selection: {
                enabled: false,
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
                const label = chartLabels[dataPointIndex] || '';
                const value = series[seriesIndex][dataPointIndex];
                return `
                    <div class="px-2 py-1 text-sm text-gray-700 dark:text-neutral-200">
                        ${label}: <span class="font-semibold">${value}</span>
                    </div>
                `;
            },
        },
    });

    chart.render();
}

function renderVisitedCitiesByYearChart(uniqueByYear, totalByYear, newByYear) {
    const loadingElement = document.getElementById('personal-visited-cities-by-year-loading');
    const chartContainer = document.getElementById('personal-visited-cities-by-year-chart');
    if (!loadingElement || !chartContainer) {
        return;
    }

    const uniqueMap = new Map(
        (Array.isArray(uniqueByYear) ? uniqueByYear : []).map((item) => [
            String(item?.label || ''),
            Number(item?.count || 0),
        ])
    );
    const totalMap = new Map(
        (Array.isArray(totalByYear) ? totalByYear : []).map((item) => [
            String(item?.label || ''),
            Number(item?.count || 0),
        ])
    );
    const newMap = new Map(
        (Array.isArray(newByYear) ? newByYear : []).map((item) => [
            String(item?.label || ''),
            Number(item?.count || 0),
        ])
    );
    const labels = [...new Set([...uniqueMap.keys(), ...totalMap.keys(), ...newMap.keys()])]
        .filter((label) => label)
        .sort((a, b) => Number(a) - Number(b));

    if (labels.length === 0) {
        loadingElement.innerHTML =
            '<p class="text-gray-600 dark:text-neutral-400">Нет данных</p>';
        chartContainer.classList.add('hidden');
        return;
    }

    const uniqueValues = labels.map((label) => uniqueMap.get(label) ?? 0);
    const totalValues = labels.map((label) => totalMap.get(label) ?? 0);
    const newValues = labels.map((label) => newMap.get(label) ?? 0);

    loadingElement.classList.add('hidden');
    chartContainer.classList.remove('hidden');
    chartContainer.innerHTML = '';

    const chart = new ApexCharts(chartContainer, {
        series: [
            {
                name: 'Всего посещений',
                data: totalValues,
            },
            {
                name: 'Уникальные города',
                data: uniqueValues,
            },
            {
                name: 'Новые города',
                data: newValues,
            },
        ],
        chart: {
            type: 'area',
            height: 320,
            toolbar: {
                show: false,
            },
            zoom: {
                enabled: false,
                allowMouseWheelZoom: false,
            },
            selection: {
                enabled: false,
            },
        },
        stroke: {
            curve: 'smooth',
            width: 3,
        },
        colors: ['#10b981', '#f59e0b', '#0ea5e9'],
        fill: {
            type: 'gradient',
            gradient: {
                shade: 'dark',
                gradientToColors: ['#10b981', '#f59e0b', '#0ea5e9'],
                shadeIntensity: 1,
                opacityFrom: 0.6,
                opacityTo: 0,
                stops: [0, 100],
            },
        },
        dataLabels: {
            enabled: false,
        },
        markers: {
            size: 0,
            hover: {
                size: 5,
            },
        },
        xaxis: {
            categories: labels,
            labels: {
                style: {
                    colors: '#6b7280',
                },
            },
        },
        yaxis: {
            min: 0,
            labels: {
                formatter(value) {
                    return formatRuNumber(Math.round(value));
                },
            },
        },
        grid: {
            borderColor: '#e5e7eb',
        },
        legend: {
            position: 'top',
            horizontalAlign: 'left',
        },
        tooltip: {
            shared: false,
            intersect: false,
            custom({dataPointIndex, w}) {
                const series = w.config.series || [];
                const label = labels[dataPointIndex] || '';
                const rows = series
                    .map((seriesItem, idx) => {
                        const value = Number(seriesItem?.data?.[dataPointIndex] ?? 0);
                        const color = ['#10b981', '#f59e0b', '#0ea5e9'][idx] || '#6b7280';
                        const name = String(seriesItem?.name || 'Показатель');
                        return `
                            <div class="flex items-center justify-between gap-4 py-1">
                                <div class="flex items-center gap-2">
                                    <span class="inline-block h-2.5 w-2.5 rounded-full" style="background-color: ${color};"></span>
                                    <span>${name}</span>
                                </div>
                                <span class="font-semibold">${formatRuNumber(value)}</span>
                            </div>
                        `;
                    })
                    .join('');

                return `
                    <div class="min-w-[220px] rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-700 shadow-lg dark:border-neutral-700 dark:bg-neutral-900 dark:text-neutral-200">
                        <div class="mb-1 border-b border-gray-200 pb-1.5 font-semibold text-gray-900 dark:border-neutral-700 dark:text-white">
                            ${label}
                        </div>
                        ${rows}
                    </div>
                `;
            },
        },
    });

    chart.render().then(() => {
        const cursorElements = chartContainer.querySelectorAll(
            '.apexcharts-canvas, .apexcharts-svg, .apexcharts-inner, .apexcharts-series path, .apexcharts-area-series, .apexcharts-line-series'
        );
        for (const element of cursorElements) {
            element.style.cursor = 'default';
        }
    });
}

function renderVisitedCitiesByMonthChart(uniqueByMonth, totalByMonth, newByMonth) {
    const loadingElement = document.getElementById('personal-visited-cities-by-month-loading');
    const chartContainer = document.getElementById('personal-visited-cities-by-month-chart');
    if (!loadingElement || !chartContainer) {
        return;
    }

    const uniqueMap = new Map(
        (Array.isArray(uniqueByMonth) ? uniqueByMonth : []).map((item) => [
            String(item?.label || ''),
            Number(item?.count || 0),
        ])
    );
    const totalMap = new Map(
        (Array.isArray(totalByMonth) ? totalByMonth : []).map((item) => [
            String(item?.label || ''),
            Number(item?.count || 0),
        ])
    );
    const newMap = new Map(
        (Array.isArray(newByMonth) ? newByMonth : []).map((item) => [
            String(item?.label || ''),
            Number(item?.count || 0),
        ])
    );

    const labels = [...new Set([...uniqueMap.keys(), ...totalMap.keys(), ...newMap.keys()])]
        .filter((label) => /^\d{2}\.\d{4}$/.test(label))
        .sort((a, b) => {
            const [aMonth, aYear] = a.split('.').map(Number);
            const [bMonth, bYear] = b.split('.').map(Number);
            return aYear * 100 + aMonth - (bYear * 100 + bMonth);
        });
    const monthYearFormatter = new Intl.DateTimeFormat('ru-RU', {
        month: 'long',
        year: 'numeric',
        timeZone: 'UTC',
    });
    const displayLabels = labels.map((label) => {
        const [month, year] = label.split('.').map(Number);
        if (!month || !year) {
            return label;
        }
        return monthYearFormatter.format(new Date(Date.UTC(year, month - 1, 1)));
    });

    if (labels.length === 0) {
        loadingElement.innerHTML =
            '<p class="text-gray-600 dark:text-neutral-400">Нет данных</p>';
        chartContainer.classList.add('hidden');
        return;
    }

    const uniqueValues = labels.map((label) => uniqueMap.get(label) ?? 0);
    const totalValues = labels.map((label) => totalMap.get(label) ?? 0);
    const newValues = labels.map((label) => newMap.get(label) ?? 0);

    loadingElement.classList.add('hidden');
    chartContainer.classList.remove('hidden');
    chartContainer.innerHTML = '';

    const chart = new ApexCharts(chartContainer, {
        series: [
            {
                name: 'Всего посещений',
                data: totalValues,
            },
            {
                name: 'Уникальные города',
                data: uniqueValues,
            },
            {
                name: 'Новые города',
                data: newValues,
            },
        ],
        chart: {
            type: 'area',
            height: 320,
            toolbar: {
                show: false,
            },
            zoom: {
                enabled: false,
                allowMouseWheelZoom: false,
            },
            selection: {
                enabled: false,
            },
        },
        stroke: {
            curve: 'smooth',
            width: 3,
        },
        colors: ['#10b981', '#f59e0b', '#0ea5e9'],
        fill: {
            type: 'gradient',
            gradient: {
                shade: 'dark',
                gradientToColors: ['#10b981', '#f59e0b', '#0ea5e9'],
                shadeIntensity: 1,
                opacityFrom: 0.6,
                opacityTo: 0,
                stops: [0, 100],
            },
        },
        dataLabels: {
            enabled: false,
        },
        markers: {
            size: 0,
            hover: {
                size: 5,
            },
        },
        xaxis: {
            categories: labels,
            labels: {
                style: {
                    colors: '#6b7280',
                },
            },
        },
        yaxis: {
            min: 0,
            labels: {
                formatter(value) {
                    return formatRuNumber(Math.round(value));
                },
            },
        },
        grid: {
            borderColor: '#e5e7eb',
        },
        legend: {
            position: 'top',
            horizontalAlign: 'left',
        },
        tooltip: {
            shared: false,
            intersect: false,
            custom({dataPointIndex, w}) {
                const series = w.config.series || [];
                const label = displayLabels[dataPointIndex] || '';
                const rows = series
                    .map((seriesItem, idx) => {
                        const value = Number(seriesItem?.data?.[dataPointIndex] ?? 0);
                        const color = ['#10b981', '#f59e0b', '#0ea5e9'][idx] || '#6b7280';
                        const name = String(seriesItem?.name || 'Показатель');
                        return `
                            <div class="flex items-center justify-between gap-4 py-1">
                                <div class="flex items-center gap-2">
                                    <span class="inline-block h-2.5 w-2.5 rounded-full" style="background-color: ${color};"></span>
                                    <span>${name}</span>
                                </div>
                                <span class="font-semibold">${formatRuNumber(value)}</span>
                            </div>
                        `;
                    })
                    .join('');

                return `
                    <div class="min-w-[220px] rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-700 shadow-lg dark:border-neutral-700 dark:bg-neutral-900 dark:text-neutral-200">
                        <div class="mb-1 border-b border-gray-200 pb-1.5 font-semibold text-gray-900 dark:border-neutral-700 dark:text-white">
                            ${label}
                        </div>
                        ${rows}
                    </div>
                `;
            },
        },
    });

    chart.render().then(() => {
        const cursorElements = chartContainer.querySelectorAll(
            '.apexcharts-canvas, .apexcharts-svg, .apexcharts-inner, .apexcharts-series path, .apexcharts-area-series, .apexcharts-line-series'
        );
        for (const element of cursorElements) {
            element.style.cursor = 'default';
        }
    });
}

async function fetchVisitedCitiesOverview() {
    return await apiGet(ACCOUNT_STATS_ROUTES.getVisitedCitiesOverview);
}

async function fetchVisitedCitiesCountriesCoverage() {
    return await apiGet(ACCOUNT_STATS_ROUTES.getVisitedCitiesCountriesCoverage);
}

async function fetchVisitedCitiesCountriesVisits() {
    return await apiGet(ACCOUNT_STATS_ROUTES.getVisitedCitiesCountriesVisits);
}

async function fetchVisitedRegionsCountriesCoverage() {
    return await apiGet(ACCOUNT_STATS_ROUTES.getVisitedRegionsCountriesCoverage);
}

async function fetchRegionsVisitedCitiesTreemap(countryCode, signal) {
    const query = new URLSearchParams({country_code: countryCode || 'RU'});
    return await apiGet(
        `${ACCOUNT_STATS_ROUTES.getRegionsVisitedCitiesTreemap}?${query.toString()}`,
        {signal}
    );
}

async function fetchRegionsCountries() {
    const data = await apiGet(ACCOUNT_STATS_ROUTES.getRegionsCountries);
    return Array.isArray(data) ? data : [];
}

function getTreemapFillColor(percent) {
    if (percent >= 100) {
        return TREEMAP_FULL_COVERAGE_COLOR;
    }
    const colorIndex = Math.min(9, Math.floor(percent / 10));
    return TREEMAP_COLOR_BY_TEN_PERCENT[colorIndex];
}

function buildShortLabel(fullname) {
    return fullname.length > TREEMAP_LABEL_MAX
        ? `${fullname.slice(0, TREEMAP_LABEL_MAX).trimEnd()}...`
        : fullname;
}

function normalizeCountryOptions(data) {
    return data
        .map((country) => ({
            code: String(country.code || ''),
            name: String(country.name || country.code || ''),
            numberOfVisitedCities: Number(country.number_of_visited_cities || 0),
        }))
        .filter((country) => country.code && country.numberOfVisitedCities > 0);
}

function renderRegionsTreemap(items, loadingElement, chartContainer) {
    if (treemapState.chartInstance) {
        treemapState.chartInstance.destroy();
        treemapState.chartInstance = null;
    }

    if (items.length === 0) {
        loadingElement.innerHTML =
            '<p class="text-gray-600 dark:text-neutral-400">Нет данных</p>';
        chartContainer.classList.add('hidden');
        return;
    }

    const sortedItems = [...items].sort(
        (a, b) => (b.unique_visited_cities ?? 0) - (a.unique_visited_cities ?? 0)
    );
    const treemapData = sortedItems.map((item) => {
        const totalCities = item.total_cities ?? 0;
        const uniqueVisitedCities = item.unique_visited_cities ?? 0;
        const progress = totalCities > 0 ? uniqueVisitedCities / totalCities : 0;
        const percent = Math.round(progress * 100);
        return {
            x: buildShortLabel(item.fullname),
            fullname: item.fullname,
            y: uniqueVisitedCities,
            valueLabel: `${uniqueVisitedCities} из ${totalCities}`,
            totalCities,
            progress,
            fillColor: getTreemapFillColor(percent),
        };
    });

    loadingElement.classList.add('hidden');
    chartContainer.classList.remove('hidden');
    chartContainer.innerHTML = '';

    const chart = new ApexCharts(chartContainer, {
        series: [
            {
                data: treemapData,
            },
        ],
        legend: {
            show: false,
        },
        chart: {
            type: 'treemap',
            height: 420,
            toolbar: {
                show: false,
            },
            zoom: {
                enabled: false,
                allowMouseWheelZoom: false,
            },
            selection: {
                enabled: false,
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
                    type: 'darken',
                    value: 0.12,
                },
            },
            active: {
                filter: {
                    type: 'darken',
                    value: 0.16,
                },
            },
        },
        dataLabels: {
            enabled: true,
            offsetY: -2,
            formatter(text, opts) {
                const point = treemapData[opts.dataPointIndex];
                if (!point) {
                    return [text, ''];
                }
                return [text, point.valueLabel];
            },
            style: {
                fontSize: '14px',
                fontWeight: 700,
                colors: ['#ffffff'],
            },
            textAnchor: 'middle',
            dropShadow: {
                enabled: true,
                left: 0,
                top: 1,
                blur: 1,
                color: '#0f172a',
                opacity: 0.45,
            },
        },
        tooltip: {
            custom({seriesIndex, dataPointIndex, w}) {
                const point = treemapData[dataPointIndex];
                if (!point) {
                    return '';
                }
                const percent = Math.round((point.progress || 0) * 100);
                return `
                    <div class="min-w-[220px] rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-700 shadow-lg dark:border-neutral-700 dark:bg-neutral-900 dark:text-neutral-200">
                        <div class="mb-1 border-b border-gray-200 pb-1.5 font-semibold text-gray-900 dark:border-neutral-700 dark:text-white">
                            ${point.fullname}
                        </div>
                        <div class="flex items-center justify-between gap-4 py-1">
                            <span>Посещено</span>
                            <span class="font-semibold">${formatRuNumber(point.y)}</span>
                        </div>
                        <div class="flex items-center justify-between gap-4 py-1">
                            <span>Всего городов</span>
                            <span class="font-semibold">${formatRuNumber(point.totalCities)}</span>
                        </div>
                        <div class="flex items-center justify-between gap-4 py-1">
                            <span>Завершено</span>
                            <span class="font-semibold">${percent}%</span>
                        </div>
                    </div>
                `;
            },
        },
    });
    treemapState.chartInstance = chart;
    chart.render();
}

function populateRegionsCountrySelect(items) {
    const countrySelect = document.getElementById('personal-regions-country-select');
    if (!countrySelect) {
        return;
    }

    countrySelect.innerHTML = '';

    for (const item of items) {
        const option = document.createElement('option');
        option.value = item.code;
        option.textContent = item.name;
        if (item.code === treemapState.selectedCountryCode) {
            option.selected = true;
        }
        countrySelect.appendChild(option);
    }

    if (!items.some((item) => item.code === treemapState.selectedCountryCode) && items.length > 0) {
        treemapState.selectedCountryCode = items[0].code;
        countrySelect.value = treemapState.selectedCountryCode;
    }

    countrySelect.disabled = false;
}

function initRegionsVisitedCitiesTreemap() {
    const loadingElement = document.getElementById('personal-regions-treemap-loading');
    const chartContainer = document.getElementById('personal-regions-treemap-chart');
    const countrySelect = document.getElementById('personal-regions-country-select');
    if (!loadingElement || !chartContainer || !countrySelect) {
        return;
    }

    const loadTreemap = (countryCode) => {
        treemapState.selectedCountryCode = countryCode || 'RU';
        const currentRequestId = ++treemapState.requestId;
        if (treemapState.fetchController) {
            treemapState.fetchController.abort();
        }
        if (treemapState.chartInstance) {
            treemapState.chartInstance.destroy();
            treemapState.chartInstance = null;
        }
        treemapState.fetchController = new AbortController();
        loadingElement.classList.remove('hidden');
        chartContainer.classList.add('hidden');
        loadingElement.innerHTML = TREEMAP_LOADING_HTML;

        fetchRegionsVisitedCitiesTreemap(
            treemapState.selectedCountryCode,
            treemapState.fetchController.signal
        )
            .then((data) => {
                if (currentRequestId !== treemapState.requestId) {
                    return;
                }
                const items = Array.isArray(data?.items) ? data.items : [];
                renderRegionsTreemap(items, loadingElement, chartContainer);
            })
            .catch((error) => {
                if (currentRequestId !== treemapState.requestId) {
                    return;
                }
                if (error?.name === 'AbortError') {
                    return;
                }
                console.error('Failed to fetch regions treemap data', error);
                loadingElement.innerHTML =
                    '<p class="text-gray-600 dark:text-neutral-400">Не удалось загрузить данные графика</p>';
            });
    };

    fetchRegionsCountries()
        .then((data) => {
            const items = normalizeCountryOptions(data);
            populateRegionsCountrySelect(items);
            countrySelect.onchange = (event) => {
                const nextCountryCode = event.target.value || 'RU';
                loadTreemap(nextCountryCode);
            };
            loadTreemap(countrySelect.value || treemapState.selectedCountryCode);
        })
        .catch((error) => {
            console.error('Failed to fetch regions countries', error);
            countrySelect.disabled = true;
            loadTreemap(treemapState.selectedCountryCode);
        });
}

function initVisitedCitiesOverview() {
    const requiredElements = [
        document.getElementById('number-personal_unique_visited_cities'),
        document.getElementById('badge-personal_unique_visited_cities_rank'),
        document.getElementById('badge-personal_total_visited_cities_visits_rank'),
        document.getElementById('number-personal_total_visited_cities_visits'),
        document.getElementById('personal-unique-visited-cities-trend-chart'),
        document.getElementById('personal-total-visited-cities-trend-chart'),
        document.getElementById('personal-new-visited-cities-trend-chart'),
        document.getElementById('personal-visited-cities-by-year-loading'),
        document.getElementById('personal-visited-cities-by-year-chart'),
        document.getElementById('personal-visited-cities-by-month-loading'),
        document.getElementById('personal-visited-cities-by-month-chart'),
        document.getElementById('countries-coverage-cards-loading'),
        document.getElementById('countries-coverage-cards'),
        document.getElementById('countries-visits-cards-loading'),
        document.getElementById('countries-visits-cards'),
        document.getElementById('regions-coverage-cards-loading'),
        document.getElementById('regions-coverage-cards'),
    ];

    if (requiredElements.some((element) => !element)) {
        return;
    }

    fetchVisitedCitiesOverview()
        .then((data) => {
            updateNumberOnCard(
                'number-personal_unique_visited_cities',
                data.unique_visited_cities?.count
            );
            updateRankBadge(
                'badge-personal_unique_visited_cities_rank',
                Number(data.unique_visited_cities_rank),
                Number(data.total_users_count),
                'уникальных посещенных городов'
            );
            updateNumberOnCard(
                'number-personal_total_visited_cities_visits',
                data.total_visited_cities_visits?.count
            );
            updateRankBadge(
                'badge-personal_total_visited_cities_visits_rank',
                Number(data.total_visited_cities_visits_rank),
                Number(data.total_users_count),
                'посещений городов'
            );

            renderTrendChart(
                'personal-unique-visited-cities-trend-chart',
                data.unique_visited_cities_by_year,
                'Уникальные города',
                '#f59e0b'
            );
            renderTrendChart(
                'personal-total-visited-cities-trend-chart',
                data.total_visited_cities_visits_by_year,
                'Посещения',
                '#10b981'
            );
            renderTrendChart(
                'personal-new-visited-cities-trend-chart',
                data.new_visited_cities_by_year,
                'Новые города',
                '#0ea5e9'
            );
            renderVisitedCitiesByYearChart(
                data.unique_visited_cities_by_year,
                data.total_visited_cities_visits_by_year,
                data.new_visited_cities_by_year
            );
            renderVisitedCitiesByMonthChart(
                data.unique_visited_cities_by_month,
                data.total_visited_cities_visits_by_month,
                data.new_visited_cities_by_month
            );
        })
        .catch((error) => {
            console.error('Failed to fetch account visited cities overview', error);
            const fallbackElements = [
                'number-personal_unique_visited_cities',
                'number-personal_total_visited_cities_visits',
                'personal-new-visited-cities-trend-chart',
            ];
            for (const elementId of fallbackElements) {
                const element = document.getElementById(elementId);
                if (element) {
                    element.textContent = '—';
                }
            }
            updateRankBadge('badge-personal_unique_visited_cities_rank', Number.NaN, Number.NaN, '');
            updateRankBadge(
                'badge-personal_total_visited_cities_visits_rank',
                Number.NaN,
                Number.NaN,
                ''
            );
            const loadingElement = document.getElementById('personal-visited-cities-by-year-loading');
            if (loadingElement) {
                loadingElement.innerHTML =
                    '<p class="text-gray-600 dark:text-neutral-400">Не удалось загрузить данные графика</p>';
            }
            const monthLoadingElement = document.getElementById('personal-visited-cities-by-month-loading');
            if (monthLoadingElement) {
                monthLoadingElement.innerHTML =
                    '<p class="text-gray-600 dark:text-neutral-400">Не удалось загрузить данные графика</p>';
            }
        });

    fetchVisitedCitiesCountriesCoverage()
        .then((data) => {
            renderCountriesCoverageCards(data.countries_coverage);
        })
        .catch((error) => {
            console.error('Failed to fetch countries coverage data', error);
            renderCountriesCoverageCards([]);
        });

    fetchVisitedRegionsCountriesCoverage()
        .then((data) => {
            renderRegionsCoverageCards(data.countries_coverage);
        })
        .catch((error) => {
            console.error('Failed to fetch regions coverage data', error);
            renderRegionsCoverageCards([]);
        });

    fetchVisitedCitiesCountriesVisits()
        .then((data) => {
            renderCountriesVisitsCards(data.countries_visits);
        })
        .catch((error) => {
            console.error('Failed to fetch countries visits data', error);
            renderCountriesVisitsCards([]);
        });
}

function initAccountStatistics() {
    if (window.__mgAccountStatisticsInitialized) {
        return;
    }
    window.__mgAccountStatisticsInitialized = true;
    initVisitedCitiesOverview();
    initRegionsVisitedCitiesTreemap();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAccountStatistics);
} else {
    initAccountStatistics();
}
