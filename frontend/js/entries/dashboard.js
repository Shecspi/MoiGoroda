import {getCookie} from '../components/get_cookie.js';

const DASHBOARD_ROUTES = Object.freeze({
    // Пользователи
    getNumberOfUsers: '/api/dashboard/users/',
    getRegistrationsYesterday: '/api/dashboard/users/registrations/yesterday/',
    getRegistrationsWeek: '/api/dashboard/users/registrations/week/',
    getRegistrationsMonth: '/api/dashboard/users/registrations/month/',
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
    getRegistrationsChart: '/api/dashboard/users/registrations/chart/',
    getRegistrationsByMonthChart: '/api/dashboard/users/registrations/chart/month/',
    getVisitedCitiesByUserChart: '/api/dashboard/visited_cities/by_user/chart/',
    getUniqueVisitedCitiesByUserChart: '/api/dashboard/visited_cities/unique_by_user/chart/',
});

// Пользователи
loadQuantityCard('number-total_users', DASHBOARD_ROUTES.getNumberOfUsers);
loadQuantityCard('number-registrations_yesterday', DASHBOARD_ROUTES.getRegistrationsYesterday);
loadQuantityCard('number-registrations_week', DASHBOARD_ROUTES.getRegistrationsWeek);
loadQuantityCard('number-registrations_month', DASHBOARD_ROUTES.getRegistrationsMonth);
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
    loadChart(
        'myChart',
        'myChartLoading',
        DASHBOARD_ROUTES.getRegistrationsChart,
        'Количество регистраций',
        'rgba(51,171,255,0.5)',
        'rgba(51,171,255,0.2)',
        2
    );
}

function loadRegistrationsByMonthChart() {
    loadChart(
        'myChartMonth',
        'myChartMonthLoading',
        DASHBOARD_ROUTES.getRegistrationsByMonthChart,
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

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        loadVisitedCountriesChart();
        loadRegistrationsChart();
        loadRegistrationsByMonthChart();
        loadVisitedCitiesByUserChart();
        loadUniqueVisitedCitiesByUserChart();
    });
} else {
    loadVisitedCountriesChart();
    loadRegistrationsChart();
    loadRegistrationsByMonthChart();
    loadVisitedCitiesByUserChart();
    loadUniqueVisitedCitiesByUserChart();
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