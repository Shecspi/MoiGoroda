import ApexCharts from "apexcharts";
import { getCookie } from "../components/get_cookie.js";

const ACCOUNT_STATS_ROUTES = Object.freeze({
    getVisitedCitiesOverview: "/api/account/stats/visited-cities/overview/",
    getVisitedCitiesCountriesCoverage:
        "/api/account/stats/visited-cities/countries-coverage/",
    getVisitedCitiesCountriesVisits:
        "/api/account/stats/visited-cities/countries-visits/",
    getVisitedRegionsCountriesCoverage:
        "/api/account/stats/regions/countries-coverage/",
    getRegionsVisitedCitiesTreemap:
        "/api/account/stats/regions/visited-cities-treemap/",
    getRegionsVisitedCitiesCountries:
        "/api/account/stats/regions/visited-cities-countries/",
    getVisitedCountriesOverview:
        "/api/account/stats/visited-countries/overview/",
});

function getStatisticsRequestContext() {
    const root = document.getElementById("account-statistics-root");
    const sharedUserIdRaw = root?.dataset?.statisticsUserId || "";
    const isSharedMode = root?.dataset?.statisticsSharedMode === "1";
    const sharedUserId = Number(sharedUserIdRaw);
    const hasSharedUserId = Number.isInteger(sharedUserId) && sharedUserId > 0;
    return {
        isSharedMode,
        sharedUserId: hasSharedUserId ? sharedUserId : null,
    };
}

function buildStatsUrl(baseUrl, requestContext) {
    if (!requestContext?.isSharedMode || !requestContext?.sharedUserId) {
        return baseUrl;
    }
    const separator = baseUrl.includes("?") ? "&" : "?";
    return `${baseUrl}${separator}shared_user_id=${requestContext.sharedUserId}`;
}

/** Overview: общий URL + фильтр страны для блока «регионы по годам» (как в treemap). */
function buildVisitedCitiesOverviewUrl(requestContext, regionsCountryCode) {
    let url = buildStatsUrl(
        ACCOUNT_STATS_ROUTES.getVisitedCitiesOverview,
        requestContext,
    );
    const code = regionsCountryCode != null ? String(regionsCountryCode).trim() : "";
    if (code !== "") {
        const sep = url.includes("?") ? "&" : "?";
        url = `${url}${sep}regions_country_code=${encodeURIComponent(code)}`;
    }
    return url;
}

const treemapState = {
    selectedCountryCode: "RU",
    requestId: 0,
    fetchController: null,
    chartInstance: null,
};
const TREEMAP_LABEL_MAX = 28;
const TREEMAP_COLOR_BY_TEN_PERCENT = [
    "#b91c1c", // 0-9%
    "#dc2626", // 10-19%
    "#ea580c", // 20-29%
    "#f59e0b", // 30-39%
    "#eab308", // 40-49%
    "#84cc16", // 50-59%
    "#22c55e", // 60-69%
    "#14b8a6", // 70-79%
    "#06b6d4", // 80-89%
    "#3b82f6", // 90-99%
];
const TREEMAP_FULL_COVERAGE_COLOR = "#8b5cf6"; // 100%
const TREEMAP_LOADING_HTML = `
    <div class="animate-spin inline-block h-7 w-7 rounded-full border-[3px] border-current border-t-transparent text-blue-600 dark:text-blue-400" role="status" aria-label="loading">
        <span class="sr-only">Загрузка...</span>
    </div>
`;

async function apiGet(url, { signal } = {}) {
    const response = await fetch(url, {
        method: "GET",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            Accept: "application/json",
        },
        credentials: "same-origin",
        signal,
    });
    if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
    }
    return await response.json();
}

function formatRuNumber(value) {
    return new Intl.NumberFormat("ru-RU").format(value ?? 0);
}

function escapeHtml(value) {
    return String(value ?? "").replace(
        /[&<>"']/g,
        (char) =>
            ({
                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "'": "&#39;",
            })[char],
    );
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

function updateRankBadge(
    elementId,
    rank,
    totalUsersCount,
    metricLabel,
    metricValue,
    isSharedMode = false,
) {
    const badgeElement = document.getElementById(elementId);
    if (!badgeElement) {
        return;
    }

    if (
        !Number.isFinite(rank) ||
        rank <= 0 ||
        !Number.isFinite(totalUsersCount) ||
        totalUsersCount <= 0 ||
        !Number.isFinite(metricValue) ||
        metricValue <= 0
    ) {
        badgeElement.classList.add("hidden");
        badgeElement.innerHTML = "";
        badgeElement.removeAttribute("title");
        return;
    }

    badgeElement.textContent = `${formatRuNumber(rank)} место`;
    badgeElement.title = isSharedMode
        ? `Пользователь занимает ${formatRuNumber(rank)} место из ${formatRuNumber(totalUsersCount)} пользователей сервиса по количеству ${metricLabel}`
        : `Вы занимаете ${formatRuNumber(rank)} место из ${formatRuNumber(totalUsersCount)} пользователей сервиса по количеству ${metricLabel}`;
    badgeElement.classList.remove("hidden");
}

function countForCalendarYearFromSeries(series, year) {
    if (!Array.isArray(series)) {
        return 0;
    }
    const label = String(year);
    const row = series.find(
        (item) => item != null && String(item.label) === label,
    );
    return Number(row?.count ?? 0);
}

/** Для sparkline по годам: все календарные годы от минимального в данных до текущего включительно, пропуски — 0. */
function normalizeYearlySeriesThroughCurrentYear(chartData) {
    const currentYear = new Date().getFullYear();
    const map = new Map();
    if (Array.isArray(chartData)) {
        for (const item of chartData) {
            if (item == null) {
                continue;
            }
            const y = parseInt(String(item.label), 10);
            if (Number.isFinite(y)) {
                map.set(y, Number(item.count ?? 0));
            }
        }
    }
    if (map.size === 0) {
        return [
            { label: String(currentYear - 1), count: 0 },
            { label: String(currentYear), count: 0 },
        ];
    }
    const years = [...map.keys()];
    const minYear = Math.min(...years);
    const endYear = Math.max(currentYear, ...years);
    const result = [];
    for (let y = minYear; y <= endYear; y += 1) {
        result.push({
            label: String(y),
            count: map.has(y) ? map.get(y) : 0,
        });
    }
    return result;
}

function renderRegionTrendChart(containerId, chartData, seriesName, color) {
    renderTrendChart(
        containerId,
        normalizeYearlySeriesThroughCurrentYear(chartData),
        seriesName,
        color,
    );
}

/** Как на дашборде: процент изменения к прошлому периоду, округление до сотых. */
function buildCalendarYearComparison(currentCount, previousCount) {
    const current = Number(currentCount) || 0;
    const previous = Number(previousCount) || 0;
    const delta = current - previous;
    const deltaPercent =
        previous === 0
            ? 0
            : Math.round((delta / previous) * 10000) / 100;
    return {
        current_count: current,
        previous_count: previous,
        delta,
        delta_percent: deltaPercent,
    };
}

function updatePersonalYearPreviousRow(elementId, value) {
    const element = document.getElementById(elementId);
    if (!element) {
        return;
    }
    element.innerHTML = `<span class="dashboard-metric-number text-base font-semibold text-gray-900 dark:text-white">${formatRuNumber(value)}</span>`;
}

function updatePersonalYearCurrentRow(elementId, comparison) {
    const element = document.getElementById(elementId);
    if (!element || !comparison) {
        return;
    }
    const deltaNumber = Number(comparison.delta);
    const deltaClass =
        deltaNumber >= 0
            ? "text-emerald-600 dark:text-emerald-400"
            : "text-red-600 dark:text-red-400";
    const trendIcon =
        deltaNumber >= 0
            ? `
            <svg class="h-4 w-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M7 17L17 7M17 7H9M17 7v8"/>
            </svg>
        `
            : `
            <svg class="h-4 w-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M7 7l10 10M17 17H9M17 17V9"/>
            </svg>
        `;
    const absPercent = Math.abs(Number(comparison.delta_percent));
    element.innerHTML = `
        <span class="dashboard-metric-number inline-flex flex-wrap items-center justify-end gap-x-2 gap-y-1 text-base font-semibold text-gray-900 dark:text-white">
            <span>${formatRuNumber(comparison.current_count)}</span>
            <span class="inline-flex items-center gap-1 ${deltaClass}">
                ${trendIcon}
                <span>${absPercent}%</span>
            </span>
        </span>
    `;
}

/** Годовые значения из тех же серий, что и мини-графики карточек (`*_by_year`). */
function applyPersonalYearRowsFromSeries(idPrefix, byYearSeries) {
    const year = new Date().getFullYear();
    const current = countForCalendarYearFromSeries(byYearSeries, year);
    const previous = countForCalendarYearFromSeries(byYearSeries, year - 1);
    const comparison = buildCalendarYearComparison(current, previous);
    updatePersonalYearCurrentRow(`${idPrefix}-current`, comparison);
    updatePersonalYearPreviousRow(`${idPrefix}-previous`, previous);
}

function renderUnifiedCountryCards(
    citiesCoverage,
    regionsCoverage,
    visits,
    isSharedMode = false,
) {
    const loadingElement = document.getElementById(
        "unified-country-cards-loading",
    );
    const cardsContainer = document.getElementById("unified-country-cards");

    if (!loadingElement || !cardsContainer) return;

    const countryMap = new Map();

    const safeCitiesCoverage = Array.isArray(citiesCoverage)
        ? citiesCoverage
        : [];
    const safeRegionsCoverage = Array.isArray(regionsCoverage)
        ? regionsCoverage
        : [];
    const safeVisits = Array.isArray(visits) ? visits : [];

    for (const c of safeCitiesCoverage) {
        if (!countryMap.has(c.name)) countryMap.set(c.name, { name: c.name });
        const obj = countryMap.get(c.name);
        obj.visitedCities = Number(c.visited_cities || 0);
        obj.totalCities = Number(c.total_cities || 0);
        obj.citiesRank = Number(c.rank || 0);
        obj.citiesTotalUsers = Number(c.total_users_count || 0);
    }

    for (const c of safeRegionsCoverage) {
        if (!countryMap.has(c.name)) countryMap.set(c.name, { name: c.name });
        const obj = countryMap.get(c.name);
        obj.visitedRegions = Number(c.visited_regions || 0);
        obj.totalRegions = Number(c.total_regions || 0);
        obj.finishedRegions = Number(c.finished_regions || 0);
    }

    for (const c of safeVisits) {
        if (!countryMap.has(c.name)) countryMap.set(c.name, { name: c.name });
        const obj = countryMap.get(c.name);
        obj.visits = Number(c.visits || 0);
        obj.visitsRank = Number(c.rank || 0);
        obj.visitsTotalUsers = Number(c.total_users_count || 0);
    }

    const items = Array.from(countryMap.values()).filter(
        (c) => c.visitedCities > 0 || c.visitedRegions > 0 || c.visits > 0,
    );

    items.sort((a, b) => {
        const vA = a.visitedCities || 0;
        const vB = b.visitedCities || 0;
        if (vB !== vA) return vB - vA;
        return a.name.localeCompare(b.name);
    });

    if (items.length === 0) {
        loadingElement.classList.remove("hidden");
        cardsContainer.classList.add("hidden");
        loadingElement.innerHTML = `
            <div class="col-span-full rounded-xl border border-gray-200 bg-white p-4 text-sm text-gray-600 shadow-sm dark:border-neutral-700 dark:bg-neutral-900 dark:text-neutral-400">
                Пока нет данных по посещённым странам
            </div>
        `;
        return;
    }

    cardsContainer.innerHTML = items
        .map((c) => {
            const countryName = c.name || "—";
            const safeCountryName = escapeHtml(countryName);
            const visitedCities = c.visitedCities || 0;
            const totalCities = c.totalCities || 0;
            const citiesWidth =
                totalCities > 0
                    ? Math.round((visitedCities / totalCities) * 100)
                    : 0;
            const citiesRank = c.citiesRank || 0;
            const citiesUsers = c.citiesTotalUsers || 0;

            const citiesRankHtml =
                citiesRank > 0 && citiesUsers > 0
                    ? `<span class="badge badge-soft-outline-secondary badge-pill badge-compact whitespace-nowrap ml-2" title="${isSharedMode ? "Пользователь занимает" : "Вы занимаете"} ${formatRuNumber(citiesRank)} место из ${formatRuNumber(citiesUsers)} пользователей сервиса по количеству посещённых городов в этой стране">${formatRuNumber(citiesRank)} место</span>`
                    : "";

            const visitedRegions = c.visitedRegions || 0;
            const totalRegions = c.totalRegions || 0;
            const regionsWidth =
                totalRegions > 0
                    ? Math.round((visitedRegions / totalRegions) * 100)
                    : 0;
            const finishedRegions = c.finishedRegions || 0;

            const totalVisits = c.visits || 0;
            const visitsRank = c.visitsRank || 0;
            const visitsUsers = c.visitsTotalUsers || 0;

            const visitsRankHtml =
                visitsRank > 0 && visitsUsers > 0
                    ? `<span class="badge badge-soft-outline-secondary badge-pill badge-compact whitespace-nowrap ml-2" title="${isSharedMode ? "Пользователь занимает" : "Вы занимаете"} ${formatRuNumber(visitsRank)} место из ${formatRuNumber(visitsUsers)} пользователей сервиса по общему количеству посещений городов в этой стране">${formatRuNumber(visitsRank)} место</span>`
                    : "";

            const hasCities = visitedCities > 0 || totalCities > 0;
            const hasRegions = visitedRegions > 0 || totalRegions > 0;

            return `
            <div class="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-neutral-700 dark:bg-neutral-900 flex flex-col gap-4">
                <div class="flex items-center justify-between">
                    <h3 class="text-lg font-bold text-gray-900 dark:text-white">${safeCountryName}</h3>
                </div>

                ${
                    hasCities || hasRegions
                        ? `
                <div class="flex flex-wrap justify-center gap-4">
                    ${
                        hasCities
                            ? `
                    <div class="flex flex-1 flex-col items-center min-w-[160px]">
                        <div class="mb-2 text-center text-sm font-medium text-gray-700 dark:text-neutral-300">
                            Города
                        </div>
                        <div class="progress-gauge progress-gauge-lg progress-gauge-rotate-135 progress-gauge-primary" role="progressbar" aria-valuenow="${citiesWidth}" aria-valuemin="0" aria-valuemax="100">
                            <svg viewBox="0 0 36 36" xmlns="http://www.w3.org/2000/svg">
                                <circle cx="18" cy="18" r="16" fill="none" class="progress-gauge-bg" stroke-width="1" stroke-dasharray="75 100" stroke-linecap="round"></circle>
                                <circle cx="18" cy="18" r="16" fill="none" class="progress-gauge-bar" stroke-width="2" stroke-dasharray="${citiesWidth * 0.75} 100" stroke-linecap="round"></circle>
                            </svg>
                            <div class="progress-gauge-text">
                                <span class="progress-gauge-value">${formatRuNumber(visitedCities)}</span>
                                <span class="progress-gauge-label text-xs">из ${formatRuNumber(totalCities)}</span>
                            </div>
                        </div>
                        ${
                            citiesRankHtml
                                ? `<div class="mt-2 text-center">${citiesRankHtml}</div>`
                                : ""
                        }
                    </div>
                    `
                            : ""
                    }
                    ${
                        hasRegions
                            ? `
                    <div class="flex flex-1 flex-col items-center min-w-[160px]">
                        <div class="mb-2 text-center text-sm font-medium text-gray-700 dark:text-neutral-300">
                            Регионы
                        </div>
                        <div class="progress-gauge progress-gauge-lg progress-gauge-rotate-135 progress-gauge-purple" role="progressbar" aria-valuenow="${regionsWidth}" aria-valuemin="0" aria-valuemax="100">
                            <svg viewBox="0 0 36 36" xmlns="http://www.w3.org/2000/svg">
                                <circle cx="18" cy="18" r="16" fill="none" class="progress-gauge-bg" stroke-width="1" stroke-dasharray="75 100" stroke-linecap="round"></circle>
                                <circle cx="18" cy="18" r="16" fill="none" class="progress-gauge-bar" stroke-width="2" stroke-dasharray="${regionsWidth * 0.75} 100" stroke-linecap="round"></circle>
                            </svg>
                            <div class="progress-gauge-text">
                                <span class="progress-gauge-value">${formatRuNumber(visitedRegions)}</span>
                                <span class="progress-gauge-label text-xs">из ${formatRuNumber(totalRegions)}</span>
                            </div>
                        </div>
                    </div>
                    `
                            : ""
                    }
                </div>
                `
                        : ""
                }

                ${
                    finishedRegions > 0
                        ? `
                <div class="flex items-center justify-between text-sm">
                    <span class="font-medium text-gray-700 dark:text-neutral-300">Закрытые регионы</span>
                    <span class="badge badge-soft-outline-success badge-pill whitespace-nowrap">${formatRuNumber(finishedRegions)} из ${formatRuNumber(totalRegions)}</span>
                </div>
                `
                        : ""
                }

                ${
                    totalVisits > 0
                        ? `
                <div class="flex items-center justify-between text-sm border-t border-gray-100 dark:border-neutral-800 pt-3 mt-1">
                    <span class="font-medium text-gray-700 dark:text-neutral-300">Всего визитов ${visitsRankHtml}</span>
                    <span class="badge badge-soft-outline-info badge-pill whitespace-nowrap">${formatRuNumber(totalVisits)}</span>
                </div>
                `
                        : ""
                }
            </div>
        `;
        })
        .join("");

    loadingElement.classList.add("hidden");
    cardsContainer.classList.remove("hidden");
}

function renderTrendChart(containerId, chartData, seriesName, color) {
    const chartContainer = document.getElementById(containerId);
    if (!chartContainer) {
        return;
    }

    if (!Array.isArray(chartData) || chartData.length === 0) {
        chartContainer.innerHTML =
            '<p class="text-gray-600 dark:text-neutral-400">Нет данных</p>';
        return;
    }

    const labels = chartData.map((item) => item.label);
    const values = chartData.map((item) => item.count);
    const chartLabels = labels.length === 1 ? [labels[0], labels[0]] : labels;
    const chartValues = values.length === 1 ? [values[0], values[0]] : values;

    chartContainer.innerHTML = "";

    const chart = new ApexCharts(chartContainer, {
        series: [
            {
                name: seriesName,
                data: chartValues,
            },
        ],
        chart: {
            type: "area",
            height: "100%",
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
            curve: "straight",
            width: 2,
            colors: [color],
        },
        colors: [color],
        fill: {
            type: "gradient",
            gradient: {
                shade: "dark",
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
                    type: "none",
                },
            },
            hover: {
                filter: {
                    type: "none",
                },
            },
            active: {
                filter: {
                    type: "none",
                },
            },
        },
        xaxis: {
            categories: chartLabels,
        },
        tooltip: {
            custom({ series, seriesIndex, dataPointIndex }) {
                const label = chartLabels[dataPointIndex] || "";
                const value = series[seriesIndex][dataPointIndex];
                return `
                    <div class="px-2 py-1 text-sm text-gray-700 dark:text-neutral-200">
                        ${escapeHtml(label)}: <span class="font-semibold">${formatRuNumber(value)}</span>
                    </div>
                `;
            },
        },
    });

    chart.render();
}

function renderVisitedCitiesByYearChart(uniqueByYear, totalByYear, newByYear) {
    const loadingElement = document.getElementById(
        "personal-visited-cities-by-year-loading",
    );
    const chartContainer = document.getElementById(
        "personal-visited-cities-by-year-chart",
    );
    if (!loadingElement || !chartContainer) {
        return;
    }

    const uniqueMap = new Map(
        (Array.isArray(uniqueByYear) ? uniqueByYear : []).map((item) => [
            String(item?.label || ""),
            Number(item?.count || 0),
        ]),
    );
    const totalMap = new Map(
        (Array.isArray(totalByYear) ? totalByYear : []).map((item) => [
            String(item?.label || ""),
            Number(item?.count || 0),
        ]),
    );
    const newMap = new Map(
        (Array.isArray(newByYear) ? newByYear : []).map((item) => [
            String(item?.label || ""),
            Number(item?.count || 0),
        ]),
    );
    const labels = [
        ...new Set([...uniqueMap.keys(), ...totalMap.keys(), ...newMap.keys()]),
    ]
        .filter((label) => label)
        .sort((a, b) => Number(a) - Number(b));

    if (labels.length === 0) {
        loadingElement.innerHTML =
            '<p class="text-gray-600 dark:text-neutral-400">Нет данных</p>';
        chartContainer.classList.add("hidden");
        return;
    }

    const uniqueValues = labels.map((label) => uniqueMap.get(label) ?? 0);
    const totalValues = labels.map((label) => totalMap.get(label) ?? 0);
    const newValues = labels.map((label) => newMap.get(label) ?? 0);

    loadingElement.classList.add("hidden");
    chartContainer.classList.remove("hidden");
    chartContainer.innerHTML = "";

    const chart = new ApexCharts(chartContainer, {
        series: [
            {
                name: "Всего посещений",
                data: totalValues,
            },
            {
                name: "Уникальные города",
                data: uniqueValues,
            },
            {
                name: "Новые города",
                data: newValues,
            },
        ],
        chart: {
            type: "area",
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
            curve: "smooth",
            width: 3,
        },
        colors: ["#10b981", "#f59e0b", "#0ea5e9"],
        fill: {
            type: "gradient",
            gradient: {
                shade: "dark",
                gradientToColors: ["#10b981", "#f59e0b", "#0ea5e9"],
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
                    colors: "#6b7280",
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
            borderColor: "#e5e7eb",
        },
        legend: {
            position: "top",
            horizontalAlign: "left",
        },
        tooltip: {
            shared: false,
            intersect: false,
            custom({ dataPointIndex, w }) {
                const series = w.config.series || [];
                const label = labels[dataPointIndex] || "";
                const rows = series
                    .map((seriesItem, idx) => {
                        const value = Number(
                            seriesItem?.data?.[dataPointIndex] ?? 0,
                        );
                        const color =
                            ["#10b981", "#f59e0b", "#0ea5e9"][idx] || "#6b7280";
                        const name = String(seriesItem?.name || "Показатель");
                        const safeName = escapeHtml(name);
                        return `
                            <div class="flex items-center justify-between gap-4 py-1">
                                <div class="flex items-center gap-2">
                                    <span class="inline-block h-2.5 w-2.5 rounded-full" style="background-color: ${color};"></span>
                                    <span>${safeName}</span>
                                </div>
                                <span class="font-semibold">${formatRuNumber(value)}</span>
                            </div>
                        `;
                    })
                    .join("");

                return `
                    <div class="min-w-[220px] rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-700 shadow-lg dark:border-neutral-700 dark:bg-neutral-900 dark:text-neutral-200">
                        <div class="mb-1 border-b border-gray-200 pb-1.5 font-semibold text-gray-900 dark:border-neutral-700 dark:text-white">
                            ${escapeHtml(label)}
                        </div>
                        ${rows}
                    </div>
                `;
            },
        },
    });

    chart.render().then(() => {
        const cursorElements = chartContainer.querySelectorAll(
            ".apexcharts-canvas, .apexcharts-svg, .apexcharts-inner, .apexcharts-series path, .apexcharts-area-series, .apexcharts-line-series",
        );
        for (const element of cursorElements) {
            element.style.cursor = "default";
        }
    });
}

function renderVisitedCitiesByMonthChart(
    uniqueByMonth,
    totalByMonth,
    newByMonth,
) {
    const loadingElement = document.getElementById(
        "personal-visited-cities-by-month-loading",
    );
    const chartContainer = document.getElementById(
        "personal-visited-cities-by-month-chart",
    );
    if (!loadingElement || !chartContainer) {
        return;
    }

    const uniqueMap = new Map(
        (Array.isArray(uniqueByMonth) ? uniqueByMonth : []).map((item) => [
            String(item?.label || ""),
            Number(item?.count || 0),
        ]),
    );
    const totalMap = new Map(
        (Array.isArray(totalByMonth) ? totalByMonth : []).map((item) => [
            String(item?.label || ""),
            Number(item?.count || 0),
        ]),
    );
    const newMap = new Map(
        (Array.isArray(newByMonth) ? newByMonth : []).map((item) => [
            String(item?.label || ""),
            Number(item?.count || 0),
        ]),
    );

    const labels = [
        ...new Set([...uniqueMap.keys(), ...totalMap.keys(), ...newMap.keys()]),
    ]
        .filter((label) => /^\d{2}\.\d{4}$/.test(label))
        .sort((a, b) => {
            const [aMonth, aYear] = a.split(".").map(Number);
            const [bMonth, bYear] = b.split(".").map(Number);
            return aYear * 100 + aMonth - (bYear * 100 + bMonth);
        });
    const monthYearFormatter = new Intl.DateTimeFormat("ru-RU", {
        month: "long",
        year: "numeric",
        timeZone: "UTC",
    });
    const displayLabels = labels.map((label) => {
        const [month, year] = label.split(".").map(Number);
        if (!month || !year) {
            return label;
        }
        return monthYearFormatter.format(
            new Date(Date.UTC(year, month - 1, 1)),
        );
    });

    if (labels.length === 0) {
        loadingElement.innerHTML =
            '<p class="text-gray-600 dark:text-neutral-400">Нет данных</p>';
        chartContainer.classList.add("hidden");
        return;
    }

    const uniqueValues = labels.map((label) => uniqueMap.get(label) ?? 0);
    const totalValues = labels.map((label) => totalMap.get(label) ?? 0);
    const newValues = labels.map((label) => newMap.get(label) ?? 0);

    loadingElement.classList.add("hidden");
    chartContainer.classList.remove("hidden");
    chartContainer.innerHTML = "";

    const chart = new ApexCharts(chartContainer, {
        series: [
            {
                name: "Всего посещений",
                data: totalValues,
            },
            {
                name: "Уникальные города",
                data: uniqueValues,
            },
            {
                name: "Новые города",
                data: newValues,
            },
        ],
        chart: {
            type: "area",
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
            curve: "smooth",
            width: 3,
        },
        colors: ["#10b981", "#f59e0b", "#0ea5e9"],
        fill: {
            type: "gradient",
            gradient: {
                shade: "dark",
                gradientToColors: ["#10b981", "#f59e0b", "#0ea5e9"],
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
                    colors: "#6b7280",
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
            borderColor: "#e5e7eb",
        },
        legend: {
            position: "top",
            horizontalAlign: "left",
        },
        tooltip: {
            shared: false,
            intersect: false,
            custom({ dataPointIndex, w }) {
                const series = w.config.series || [];
                const label = displayLabels[dataPointIndex] || "";
                const rows = series
                    .map((seriesItem, idx) => {
                        const value = Number(
                            seriesItem?.data?.[dataPointIndex] ?? 0,
                        );
                        const color =
                            ["#10b981", "#f59e0b", "#0ea5e9"][idx] || "#6b7280";
                        const name = String(seriesItem?.name || "Показатель");
                        const safeName = escapeHtml(name);
                        return `
                            <div class="flex items-center justify-between gap-4 py-1">
                                <div class="flex items-center gap-2">
                                    <span class="inline-block h-2.5 w-2.5 rounded-full" style="background-color: ${color};"></span>
                                    <span>${safeName}</span>
                                </div>
                                <span class="font-semibold">${formatRuNumber(value)}</span>
                            </div>
                        `;
                    })
                    .join("");

                return `
                    <div class="min-w-[220px] rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-700 shadow-lg dark:border-neutral-700 dark:bg-neutral-900 dark:text-neutral-200">
                        <div class="mb-1 border-b border-gray-200 pb-1.5 font-semibold text-gray-900 dark:border-neutral-700 dark:text-white">
                            ${escapeHtml(label)}
                        </div>
                        ${rows}
                    </div>
                `;
            },
        },
    });

    chart.render().then(() => {
        const cursorElements = chartContainer.querySelectorAll(
            ".apexcharts-canvas, .apexcharts-svg, .apexcharts-inner, .apexcharts-series path, .apexcharts-area-series, .apexcharts-line-series",
        );
        for (const element of cursorElements) {
            element.style.cursor = "default";
        }
    });
}

async function fetchVisitedCitiesOverview(requestContext, regionsCountryCode) {
    const url =
        regionsCountryCode !== undefined && regionsCountryCode !== null
            ? buildVisitedCitiesOverviewUrl(requestContext, regionsCountryCode)
            : buildStatsUrl(
                  ACCOUNT_STATS_ROUTES.getVisitedCitiesOverview,
                  requestContext,
              );
    return await apiGet(url);
}

function applyVisitedRegionsOverviewData(data) {
    if (!data) {
        return;
    }
    updateNumberOnCard(
        "number-personal_regions_total_visits",
        data.total_region_visits?.count,
    );
    updateNumberOnCard(
        "number-personal_regions_unique",
        data.unique_visited_regions?.count,
    );
    updateNumberOnCard(
        "number-personal_regions_new",
        data.new_visited_regions?.count,
    );
    applyPersonalYearRowsFromSeries(
        "personal-regions-total-ytd",
        data.total_region_visits_by_year,
    );
    applyPersonalYearRowsFromSeries(
        "personal-regions-unique-ytd",
        data.unique_visited_regions_by_year,
    );
    applyPersonalYearRowsFromSeries(
        "personal-regions-new-ytd",
        data.new_visited_regions_by_year,
    );
    renderRegionTrendChart(
        "personal-regions-total-trend-chart",
        data.total_region_visits_by_year,
        "Посещения",
        "#7c3aed",
    );
    renderRegionTrendChart(
        "personal-regions-unique-trend-chart",
        data.unique_visited_regions_by_year,
        "Регионы",
        "#10b981",
    );
    renderRegionTrendChart(
        "personal-regions-new-trend-chart",
        data.new_visited_regions_by_year,
        "Новые регионы",
        "#0ea5e9",
    );
}

async function refreshVisitedRegionsYearRows(requestContext, countryCode) {
    const code =
        countryCode != null && String(countryCode).trim() !== ""
            ? String(countryCode).trim()
            : treemapState.selectedCountryCode;
    const url = buildVisitedCitiesOverviewUrl(requestContext, code);
    const data = await apiGet(url);
    applyVisitedRegionsOverviewData(data);
}

function renderVisitedCountriesOverviewCards(data, isSharedMode = false) {
    const loadingElement = document.getElementById(
        "visited-countries-overview-loading",
    );
    const totalContainer = document.getElementById(
        "visited-countries-total-card",
    );
    const byPartContainer = document.getElementById(
        "visited-countries-by-part-cards",
    );
    if (!loadingElement || !totalContainer || !byPartContainer) {
        return;
    }

    const visited = Number(data?.visited ?? 0);
    const total = Number(data?.total ?? 0);
    const byLocation = Array.isArray(data?.by_location) ? data.by_location : [];

    if (visited === 0) {
        loadingElement.classList.remove("hidden");
        totalContainer.classList.add("hidden");
        byPartContainer.classList.add("hidden");
        loadingElement.innerHTML = `
            <div class="col-span-full rounded-xl border border-gray-200 bg-white p-4 text-sm text-gray-600 shadow-sm dark:border-neutral-700 dark:bg-neutral-900 dark:text-neutral-400">
                Пока нет данных по посещённым странам
            </div>
        `;
        return;
    }

    const totalWidthPercent =
        total > 0 ? Math.round((visited / total) * 100) : 0;

    // Первая строка — общая карточка
    totalContainer.innerHTML = `
        <div class="rounded-xl border border-gray-200 bg-white p-4 shadow-sm dark:border-neutral-700 dark:bg-neutral-900">
            <div class="mb-3">
                <p class="text-sm font-semibold text-gray-900 dark:text-white">Всего стран</p>
            </div>
            <div class="mb-3">
                <p class="dashboard-metric-number text-2xl font-extrabold leading-none text-gray-900 dark:text-white">
                    ${formatRuNumber(visited)} из ${formatRuNumber(total)}
                </p>
            </div>
            <div class="mt-6 h-1.5 w-full rounded-full bg-gray-200 dark:bg-neutral-700">
                <div class="h-1.5 rounded-full bg-teal-500" style="width: ${totalWidthPercent}%"></div>
            </div>
        </div>
    `;

    // Вторая строка — карточки по частям света
    byPartContainer.innerHTML = byLocation
        .map((item) => {
            const locVisited = Number(item?.visited ?? 0);
            const locTotal = Number(item?.total ?? 0);
            const locWidthPercent =
                locTotal > 0 ? Math.round((locVisited / locTotal) * 100) : 0;
            const locationName = String(item?.location_name || "—");
            const safeLocationName = escapeHtml(locationName);
            return `
                <div class="rounded-xl border border-gray-200 bg-white p-4 shadow-sm dark:border-neutral-700 dark:bg-neutral-900">
                    <div class="mb-3">
                        <p class="text-sm font-semibold text-gray-900 dark:text-white">${safeLocationName}</p>
                    </div>
                    <div class="mb-3">
                        <p class="dashboard-metric-number text-2xl font-extrabold leading-none text-gray-900 dark:text-white">
                            ${formatRuNumber(locVisited)} из ${formatRuNumber(locTotal)}
                        </p>
                    </div>
                    <div class="mt-6 h-1.5 w-full rounded-full bg-gray-200 dark:bg-neutral-700">
                        <div class="h-1.5 rounded-full bg-teal-500" style="width: ${locWidthPercent}%"></div>
                    </div>
                </div>
            `;
        })
        .join("");

    loadingElement.classList.add("hidden");
    totalContainer.classList.remove("hidden");
    byPartContainer.classList.remove("hidden");
}

async function fetchVisitedCountriesOverview(requestContext) {
    return await apiGet(
        buildStatsUrl(
            ACCOUNT_STATS_ROUTES.getVisitedCountriesOverview,
            requestContext,
        ),
    );
}

async function fetchVisitedCitiesCountriesCoverage(requestContext) {
    return await apiGet(
        buildStatsUrl(
            ACCOUNT_STATS_ROUTES.getVisitedCitiesCountriesCoverage,
            requestContext,
        ),
    );
}

async function fetchVisitedCitiesCountriesVisits(requestContext) {
    return await apiGet(
        buildStatsUrl(
            ACCOUNT_STATS_ROUTES.getVisitedCitiesCountriesVisits,
            requestContext,
        ),
    );
}

async function fetchVisitedRegionsCountriesCoverage(requestContext) {
    return await apiGet(
        buildStatsUrl(
            ACCOUNT_STATS_ROUTES.getVisitedRegionsCountriesCoverage,
            requestContext,
        ),
    );
}

async function fetchRegionsVisitedCitiesTreemap(
    countryCode,
    signal,
    requestContext,
) {
    const query = new URLSearchParams({ country_code: countryCode || "RU" });
    return await apiGet(
        buildStatsUrl(
            `${ACCOUNT_STATS_ROUTES.getRegionsVisitedCitiesTreemap}?${query.toString()}`,
            requestContext,
        ),
        { signal },
    );
}

async function fetchRegionsCountries(requestContext) {
    const data = await apiGet(
        buildStatsUrl(
            ACCOUNT_STATS_ROUTES.getRegionsVisitedCitiesCountries,
            requestContext,
        ),
    );
    return Array.isArray(data?.countries) ? data.countries : [];
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
            code: String(country.code || ""),
            name: String(country.name || country.code || ""),
            numberOfVisitedCities: Number(
                country.number_of_visited_cities || 0,
            ),
        }))
        .filter((country) => country.code && country.numberOfVisitedCities > 0);
}

function renderRegionsTreemap(items, loadingElement, chartContainer) {
    if (treemapState.chartInstance) {
        treemapState.chartInstance.destroy();
        treemapState.chartInstance = null;
    }

    const visitedItems = items.filter(
        (item) => Number(item?.unique_visited_cities ?? 0) > 0,
    );

    if (visitedItems.length === 0) {
        loadingElement.innerHTML =
            '<p class="text-gray-600 dark:text-neutral-400">Нет данных</p>';
        chartContainer.classList.add("hidden");
        return;
    }

    const sortedItems = [...visitedItems].sort(
        (a, b) =>
            (b.unique_visited_cities ?? 0) - (a.unique_visited_cities ?? 0),
    );
    const treemapData = sortedItems.map((item) => {
        const totalCities = item.total_cities ?? 0;
        const uniqueVisitedCities = item.unique_visited_cities ?? 0;
        const fullname = String(item.fullname || "—");
        const progress =
            totalCities > 0 ? uniqueVisitedCities / totalCities : 0;
        const percent = Math.round(progress * 100);
        return {
            x: buildShortLabel(fullname),
            fullname,
            y: uniqueVisitedCities,
            valueLabel: `${uniqueVisitedCities} из ${totalCities}`,
            totalCities,
            progress,
            fillColor: getTreemapFillColor(percent),
        };
    });

    loadingElement.classList.add("hidden");
    chartContainer.classList.remove("hidden");
    chartContainer.innerHTML = "";

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
            type: "treemap",
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
                    type: "none",
                },
            },
            hover: {
                filter: {
                    type: "darken",
                    value: 0.12,
                },
            },
            active: {
                filter: {
                    type: "darken",
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
                    return [text, ""];
                }
                return [text, point.valueLabel];
            },
            style: {
                fontSize: "14px",
                fontWeight: 700,
                colors: ["#ffffff"],
            },
            textAnchor: "middle",
            dropShadow: {
                enabled: true,
                left: 0,
                top: 1,
                blur: 1,
                color: "#0f172a",
                opacity: 0.45,
            },
        },
        tooltip: {
            custom({ seriesIndex, dataPointIndex, w }) {
                const point = treemapData[dataPointIndex];
                if (!point) {
                    return "";
                }
                const percent = Math.round((point.progress || 0) * 100);
                return `
                    <div class="min-w-[220px] rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-700 shadow-lg dark:border-neutral-700 dark:bg-neutral-900 dark:text-neutral-200">
                        <div class="mb-1 border-b border-gray-200 pb-1.5 font-semibold text-gray-900 dark:border-neutral-700 dark:text-white">
                            ${escapeHtml(point.fullname)}
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
    const countrySelect = document.getElementById(
        "personal-regions-country-select",
    );
    if (!countrySelect) {
        return;
    }

    countrySelect.innerHTML = "";

    for (const item of items) {
        const option = document.createElement("option");
        option.value = item.code;
        option.textContent = item.name;
        if (item.code === treemapState.selectedCountryCode) {
            option.selected = true;
        }
        countrySelect.appendChild(option);
    }

    if (
        !items.some((item) => item.code === treemapState.selectedCountryCode) &&
        items.length > 0
    ) {
        treemapState.selectedCountryCode = items[0].code;
        countrySelect.value = treemapState.selectedCountryCode;
    }

    countrySelect.disabled = false;
}

function initRegionsVisitedCitiesTreemap(requestContext) {
    const loadingElement = document.getElementById(
        "personal-regions-treemap-loading",
    );
    const chartContainer = document.getElementById(
        "personal-regions-treemap-chart",
    );
    const countrySelect = document.getElementById(
        "personal-regions-country-select",
    );
    if (!loadingElement || !chartContainer || !countrySelect) {
        return;
    }

    const loadTreemap = (countryCode) => {
        treemapState.selectedCountryCode = countryCode || "RU";
        const currentRequestId = ++treemapState.requestId;
        if (treemapState.fetchController) {
            treemapState.fetchController.abort();
        }
        if (treemapState.chartInstance) {
            treemapState.chartInstance.destroy();
            treemapState.chartInstance = null;
        }
        treemapState.fetchController = new AbortController();
        loadingElement.classList.remove("hidden");
        chartContainer.classList.add("hidden");
        loadingElement.innerHTML = TREEMAP_LOADING_HTML;

        fetchRegionsVisitedCitiesTreemap(
            treemapState.selectedCountryCode,
            treemapState.fetchController.signal,
            requestContext,
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
                if (error?.name === "AbortError") {
                    return;
                }
                console.error("Failed to fetch regions treemap data", error);
                loadingElement.innerHTML =
                    '<p class="text-gray-600 dark:text-neutral-400">Не удалось загрузить данные графика</p>';
            });
    };

    fetchRegionsCountries(requestContext)
        .then((data) => {
            const items = normalizeCountryOptions(data);
            populateRegionsCountrySelect(items);
            const selectedCode =
                countrySelect.value || treemapState.selectedCountryCode;
            countrySelect.onchange = (event) => {
                const nextCountryCode = event.target.value || "RU";
                loadTreemap(nextCountryCode);
                void refreshVisitedRegionsYearRows(
                    requestContext,
                    nextCountryCode,
                ).catch((err) => {
                    console.error(
                        "Failed to refresh visited regions year stats",
                        err,
                    );
                });
            };
            loadTreemap(selectedCode);
            void refreshVisitedRegionsYearRows(requestContext, selectedCode).catch(
                (err) => {
                    console.error(
                        "Failed to refresh visited regions year stats",
                        err,
                    );
                },
            );
        })
        .catch((error) => {
            console.error("Failed to fetch regions countries", error);
            countrySelect.disabled = true;
            loadTreemap(treemapState.selectedCountryCode);
            void refreshVisitedRegionsYearRows(
                requestContext,
                treemapState.selectedCountryCode,
            ).catch((err) => {
                console.error(
                    "Failed to refresh visited regions year stats",
                    err,
                );
            });
        });
}

function initVisitedCitiesOverview(requestContext) {
    const requiredElements = [
        document.getElementById("number-personal_unique_visited_cities"),
        document.getElementById("badge-personal_unique_visited_cities_rank"),
        document.getElementById(
            "badge-personal_total_visited_cities_visits_rank",
        ),
        document.getElementById("number-personal_total_visited_cities_visits"),
        document.getElementById("number-personal_new_visited_cities"),
        document.getElementById("personal-unique-ytd-previous"),
        document.getElementById("personal-unique-ytd-current"),
        document.getElementById("personal-visits-ytd-previous"),
        document.getElementById("personal-visits-ytd-current"),
        document.getElementById("personal-new-ytd-previous"),
        document.getElementById("personal-new-ytd-current"),
        document.getElementById("number-personal_regions_total_visits"),
        document.getElementById("number-personal_regions_unique"),
        document.getElementById("number-personal_regions_new"),
        document.getElementById("personal-regions-total-ytd-previous"),
        document.getElementById("personal-regions-total-ytd-current"),
        document.getElementById("personal-regions-unique-ytd-previous"),
        document.getElementById("personal-regions-unique-ytd-current"),
        document.getElementById("personal-regions-new-ytd-previous"),
        document.getElementById("personal-regions-new-ytd-current"),
        document.getElementById("personal-regions-total-trend-chart"),
        document.getElementById("personal-regions-unique-trend-chart"),
        document.getElementById("personal-regions-new-trend-chart"),
        document.getElementById("personal-unique-visited-cities-trend-chart"),
        document.getElementById("personal-total-visited-cities-trend-chart"),
        document.getElementById("personal-new-visited-cities-trend-chart"),
        document.getElementById("personal-visited-cities-by-year-loading"),
        document.getElementById("personal-visited-cities-by-year-chart"),
        document.getElementById("personal-visited-cities-by-month-loading"),
        document.getElementById("personal-visited-cities-by-month-chart"),
        document.getElementById("unified-country-cards-loading"),
        document.getElementById("unified-country-cards"),
        document.getElementById("visited-countries-overview-loading"),
        document.getElementById("visited-countries-total-card"),
        document.getElementById("visited-countries-by-part-cards"),
    ];

    if (requiredElements.some((element) => !element)) {
        return;
    }

    fetchVisitedCitiesOverview(requestContext, treemapState.selectedCountryCode)
        .then((data) => {
            updateNumberOnCard(
                "number-personal_unique_visited_cities",
                data.unique_visited_cities?.count,
            );
            updateRankBadge(
                "badge-personal_unique_visited_cities_rank",
                Number(data.unique_visited_cities_rank),
                Number(data.total_users_count),
                "уникальных посещенных городов",
                Number(data.unique_visited_cities?.count),
                requestContext?.isSharedMode,
            );
            updateNumberOnCard(
                "number-personal_total_visited_cities_visits",
                data.total_visited_cities_visits?.count,
            );
            updateRankBadge(
                "badge-personal_total_visited_cities_visits_rank",
                Number(data.total_visited_cities_visits_rank),
                Number(data.total_users_count),
                "посещений городов",
                Number(data.total_visited_cities_visits?.count),
                requestContext?.isSharedMode,
            );
            updateNumberOnCard(
                "number-personal_new_visited_cities",
                data.new_visited_cities?.count,
            );
            applyPersonalYearRowsFromSeries(
                "personal-unique-ytd",
                data.unique_visited_cities_by_year,
            );
            applyPersonalYearRowsFromSeries(
                "personal-visits-ytd",
                data.total_visited_cities_visits_by_year,
            );
            applyPersonalYearRowsFromSeries(
                "personal-new-ytd",
                data.new_visited_cities_by_year,
            );

            renderTrendChart(
                "personal-unique-visited-cities-trend-chart",
                data.unique_visited_cities_by_year,
                "Уникальные города",
                "#f59e0b",
            );
            renderTrendChart(
                "personal-total-visited-cities-trend-chart",
                data.total_visited_cities_visits_by_year,
                "Посещения",
                "#10b981",
            );
            renderTrendChart(
                "personal-new-visited-cities-trend-chart",
                data.new_visited_cities_by_year,
                "Новые города",
                "#0ea5e9",
            );
            renderVisitedCitiesByYearChart(
                data.unique_visited_cities_by_year,
                data.total_visited_cities_visits_by_year,
                data.new_visited_cities_by_year,
            );
            renderVisitedCitiesByMonthChart(
                data.unique_visited_cities_by_month,
                data.total_visited_cities_visits_by_month,
                data.new_visited_cities_by_month,
            );
            applyVisitedRegionsOverviewData(data);
        })
        .catch((error) => {
            console.error(
                "Failed to fetch account visited cities overview",
                error,
            );
            const fallbackElements = [
                "number-personal_unique_visited_cities",
                "number-personal_total_visited_cities_visits",
                "number-personal_new_visited_cities",
                "personal-unique-ytd-previous",
                "personal-unique-ytd-current",
                "personal-visits-ytd-previous",
                "personal-visits-ytd-current",
                "personal-new-ytd-previous",
                "personal-new-ytd-current",
                "number-personal_regions_total_visits",
                "number-personal_regions_unique",
                "number-personal_regions_new",
                "personal-regions-total-ytd-previous",
                "personal-regions-total-ytd-current",
                "personal-regions-unique-ytd-previous",
                "personal-regions-unique-ytd-current",
                "personal-regions-new-ytd-previous",
                "personal-regions-new-ytd-current",
                "personal-regions-total-trend-chart",
                "personal-regions-unique-trend-chart",
                "personal-regions-new-trend-chart",
                "personal-new-visited-cities-trend-chart",
            ];
            for (const elementId of fallbackElements) {
                const element = document.getElementById(elementId);
                if (element) {
                    element.textContent = "—";
                }
            }
            updateRankBadge(
                "badge-personal_unique_visited_cities_rank",
                Number.NaN,
                Number.NaN,
                "",
                Number.NaN,
            );
            updateRankBadge(
                "badge-personal_total_visited_cities_visits_rank",
                Number.NaN,
                Number.NaN,
                "",
                Number.NaN,
            );
            const loadingElement = document.getElementById(
                "personal-visited-cities-by-year-loading",
            );
            if (loadingElement) {
                loadingElement.innerHTML =
                    '<p class="text-gray-600 dark:text-neutral-400">Не удалось загрузить данные графика</p>';
            }
            const monthLoadingElement = document.getElementById(
                "personal-visited-cities-by-month-loading",
            );
            if (monthLoadingElement) {
                monthLoadingElement.innerHTML =
                    '<p class="text-gray-600 dark:text-neutral-400">Не удалось загрузить данные графика</p>';
            }
        });

    Promise.all([
        fetchVisitedCitiesCountriesCoverage(requestContext),
        fetchVisitedRegionsCountriesCoverage(requestContext),
        fetchVisitedCitiesCountriesVisits(requestContext),
    ])
        .then(([citiesCoverage, regionsCoverage, visits]) => {
            renderUnifiedCountryCards(
                citiesCoverage.countries_coverage,
                regionsCoverage.countries_coverage,
                visits.countries_visits,
                requestContext?.isSharedMode,
            );
        })
        .catch((error) => {
            console.error("Failed to fetch unified country data", error);
            renderUnifiedCountryCards([], [], [], requestContext?.isSharedMode);
        });

    fetchVisitedCountriesOverview(requestContext)
        .then((data) => {
            renderVisitedCountriesOverviewCards(
                data,
                requestContext?.isSharedMode,
            );
        })
        .catch((error) => {
            console.error("Failed to fetch visited countries overview", error);
            renderVisitedCountriesOverviewCards(
                {},
                requestContext?.isSharedMode,
            );
        });
}

function initAccountStatistics() {
    if (window.__mgAccountStatisticsInitialized) {
        return;
    }
    window.__mgAccountStatisticsInitialized = true;
    const requestContext = getStatisticsRequestContext();
    initVisitedCitiesOverview(requestContext);
    initRegionsVisitedCitiesTreemap(requestContext);
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initAccountStatistics);
} else {
    initAccountStatistics();
}
