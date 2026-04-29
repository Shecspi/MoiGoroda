import ApexCharts from 'apexcharts';
import {getCookie} from '../components/get_cookie.js';

const ACCOUNT_STATS_ROUTES = Object.freeze({
    getVisitedCitiesOverview: '/api/account/stats/visited_cities/overview/',
    getRegionsVisitedCitiesTreemap: '/api/account/stats/regions/visited_cities_treemap/',
});

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

async function fetchVisitedCitiesOverview() {
    const response = await fetch(ACCOUNT_STATS_ROUTES.getVisitedCitiesOverview, {
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

    return await response.json();
}

async function fetchRegionsVisitedCitiesTreemap() {
    const response = await fetch(ACCOUNT_STATS_ROUTES.getRegionsVisitedCitiesTreemap, {
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

    return await response.json();
}

function initRegionsVisitedCitiesTreemap() {
    const loadingElement = document.getElementById('personal-regions-treemap-loading');
    const chartContainer = document.getElementById('personal-regions-treemap-chart');
    if (!loadingElement || !chartContainer) {
        return;
    }

    fetchRegionsVisitedCitiesTreemap()
        .then((data) => {
            const items = Array.isArray(data?.items) ? data.items : [];
            if (items.length === 0) {
                loadingElement.innerHTML =
                    '<p class="text-gray-600 dark:text-neutral-400">Нет данных</p>';
                return;
            }

            const sortedItems = [...items].sort(
                (a, b) => (b.unique_visited_cities ?? 0) - (a.unique_visited_cities ?? 0)
            );
            const paletteByTenPercent = [
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
            const fullCoverageColor = '#8b5cf6'; // 100%
            const treemapData = sortedItems.map((item) => {
                const totalCities = item.total_cities ?? 0;
                const uniqueVisitedCities = item.unique_visited_cities ?? 0;
                const progress = totalCities > 0 ? uniqueVisitedCities / totalCities : 0;
                const percent = Math.round(progress * 100);
                const colorIndex = Math.min(9, Math.floor(percent / 10));
                let fillColor = fullCoverageColor;
                if (percent < 100) {
                    fillColor = paletteByTenPercent[colorIndex];
                }
                const shortLabel =
                    item.fullname.length > 28
                        ? `${item.fullname.slice(0, 28).trimEnd()}...`
                        : item.fullname;
                return {
                    x: shortLabel,
                    fullname: item.fullname,
                    y: uniqueVisitedCities,
                    valueLabel: `${uniqueVisitedCities} из ${totalCities}`,
                    totalCities,
                    progress,
                    fillColor,
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
                        const point = opts.w.config.series[0].data[opts.dataPointIndex];
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
                        const point = w.config.series[seriesIndex].data[dataPointIndex];
                        const percent = Math.round((point.progress || 0) * 100);
                        return `
                            <div class="px-2 py-1 text-sm text-gray-700 dark:text-neutral-200">
                                <div class="font-semibold">${point.fullname}</div>
                                <div>Посещено: <span class="font-semibold">${point.y}</span></div>
                                <div>Всего городов: <span class="font-semibold">${point.totalCities}</span></div>
                                <div>Покрытие: <span class="font-semibold">${percent}%</span></div>
                            </div>
                        `;
                    },
                },
            });
            chart.render();
        })
        .catch((error) => {
            console.error('Failed to fetch regions treemap data', error);
            loadingElement.innerHTML =
                '<p class="text-gray-600 dark:text-neutral-400">Не удалось загрузить данные графика</p>';
        });
}

function initVisitedCitiesOverview() {
    const requiredElements = [
        document.getElementById('number-personal_unique_visited_cities'),
        document.getElementById('number-personal_total_visited_cities_visits'),
        document.getElementById('personal-unique-visited-cities-trend-chart'),
        document.getElementById('personal-total-visited-cities-trend-chart'),
        document.getElementById('personal-new-visited-cities-trend-chart'),
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
            updateNumberOnCard(
                'number-personal_total_visited_cities_visits',
                data.total_visited_cities_visits?.count
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
        });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        initVisitedCitiesOverview();
        initRegionsVisitedCitiesTreemap();
    });
} else {
    initVisitedCitiesOverview();
    initRegionsVisitedCitiesTreemap();
}
