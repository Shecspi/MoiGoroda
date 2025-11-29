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

function loadVisitedCountriesChart() {
    const canvas = document.getElementById('visitedCountriesChart');
    const loadingElement = document.getElementById('visitedCountriesChartLoading');
    
    if (!canvas || !loadingElement) {
        return;
    }

    fetchChartData(DASHBOARD_ROUTES.getAddedVisitedCountriesChart)
        .then((data) => {
            const visitedCountriesData = {};
            data.forEach((item) => {
                visitedCountriesData[item.date] = item.count;
            });

            // Скрываем спиннер и показываем canvas
            loadingElement.classList.add('hidden');
            canvas.classList.remove('hidden');

            const ctx = canvas.getContext('2d');

            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: Object.keys(visitedCountriesData),
                    datasets: [
                        {
                            label: 'Количество добавленных посещённых стран за 1 день',
                            data: Object.values(visitedCountriesData),
                            borderColor: 'rgba(7,54,0,0.2)',
                            backgroundColor: 'rgba(58,255,51,0.2)',
                            borderWidth: 2,
                            borderRadius: 5,
                            borderSkipped: false,
                        },
                    ],
                },
            });
        })
        .catch((error) => {
            console.error('Failed to fetch chart data', error);
            // Скрываем спиннер и показываем сообщение об ошибке
            loadingElement.innerHTML = '<p class="text-gray-600 dark:text-neutral-400">Не удалось загрузить данные графика</p>';
        });
}

function loadRegistrationsChart() {
    const canvas = document.getElementById('myChart');
    const loadingElement = document.getElementById('myChartLoading');
    
    if (!canvas || !loadingElement) {
        return;
    }

    fetchChartData(DASHBOARD_ROUTES.getRegistrationsChart)
        .then((data) => {
            const registrationsData = {};
            data.forEach((item) => {
                registrationsData[item.date] = item.count;
            });

            // Скрываем спиннер и показываем canvas
            loadingElement.classList.add('hidden');
            canvas.classList.remove('hidden');

            const ctx = canvas.getContext('2d');

            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: Object.keys(registrationsData),
                    datasets: [
                        {
                            label: 'Количество регистраций',
                            data: Object.values(registrationsData),
                            borderColor: 'rgba(51,171,255,0.5)',
                            backgroundColor: 'rgba(51,171,255,0.2)',
                            borderWidth: 2,
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

function loadRegistrationsByMonthChart() {
    const canvas = document.getElementById('myChartMonth');
    const loadingElement = document.getElementById('myChartMonthLoading');
    
    if (!canvas || !loadingElement) {
        return;
    }

    fetchChartData(DASHBOARD_ROUTES.getRegistrationsByMonthChart)
        .then((data) => {
            const registrationsData = {};
            data.forEach((item) => {
                registrationsData[item.date] = item.count;
            });

            // Скрываем спиннер и показываем canvas
            loadingElement.classList.add('hidden');
            canvas.classList.remove('hidden');

            const ctx = canvas.getContext('2d');

            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: Object.keys(registrationsData),
                    datasets: [
                        {
                            label: 'Количество регистраций',
                            data: Object.values(registrationsData),
                            borderColor: 'rgba(139,92,246,0.5)',
                            backgroundColor: 'rgba(139,92,246,0.2)',
                            borderWidth: 2.5,
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

function loadVisitedCitiesByUserChart() {
    const canvas = document.getElementById('chart_qty_visited_cities');
    const loadingElement = document.getElementById('chart_qty_visited_citiesLoading');
    
    if (!canvas || !loadingElement) {
        return;
    }

    fetchChartData(DASHBOARD_ROUTES.getVisitedCitiesByUserChart)
        .then((data) => {
            const visitedCitiesData = {};
            data.forEach((item) => {
                visitedCitiesData[item.username] = item.count;
            });

            // Скрываем спиннер и показываем canvas
            loadingElement.classList.add('hidden');
            canvas.classList.remove('hidden');

            const ctx = canvas.getContext('2d');

            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: Object.keys(visitedCitiesData),
                    datasets: [
                        {
                            label: 'Количество посещённых городов',
                            data: Object.values(visitedCitiesData),
                            borderColor: 'rgba(52,0,0,0.2)',
                            backgroundColor: 'rgba(255,115,115,0.2)',
                            borderWidth: 2,
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

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        loadVisitedCountriesChart();
        loadRegistrationsChart();
        loadRegistrationsByMonthChart();
        loadVisitedCitiesByUserChart();
    });
} else {
    loadVisitedCountriesChart();
    loadRegistrationsChart();
    loadRegistrationsByMonthChart();
    loadVisitedCitiesByUserChart();
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