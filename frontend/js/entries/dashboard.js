import {getCookie} from '../components/get_cookie.js';

const request_url_ids = [
    ['url_get_total_visited_countries', 'number-total_visited_countries'],
    ['url_get_users_with_visited_countries', 'number-user_with_visited_countries'],
    ['url_get_average_qty_visited_countries', 'number-average_qty_visited_countries'],
    ['url_get_max_qty_visited_countries', 'number-max_qty_visited_countries'],
    ['url_get_qty_of_added_visited_countries_yesterday', 'number-qty_of_added_visited_countries_yesterday'],
    ['url_get_qty_of_added_visited_countries_week', 'number-qty_of_added_visited_countries_week'],
    ['url_get_qty_of_added_visited_countries_month', 'number-qty_of_added_visited_countries_month'],
    ['url_get_qty_of_added_visited_countries_year', 'number-qty_of_added_visited_countries_year'],
]

for (const item of request_url_ids) {
    const url = document.getElementById(item[0]).dataset.url;

    fetch(url, {
        method: 'GET', headers: {
            'X-CSRFToken': getCookie("csrftoken")
        }
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error(response.statusText)
            }
            return response.json()
        })
        .then((data) => {
            updateNumberOnCard(item[1], data.qty);
        })
}

fetch(document.getElementById('url_get_added_visited_countries_by_day').dataset.url, {
    method: 'GET', headers: {
        'X-CSRFToken': getCookie("csrftoken")
    }
}).then((response) => {
    if (!response.ok) {
        throw new Error(response.statusText)
    }
    return response.json()
}).then((data) => {
    let visitedCountriesData = {}
    data.forEach((item) => {
        visitedCountriesData[item.date] = item.qty;
    });

    const ctx = document.getElementById('visitedCountriesChart').getContext('2d');

    const myChart = new Chart(ctx, {
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
});

function updateNumberOnCard(element_id, newNumber) {
    const el = document.getElementById(element_id);
    el.innerHTML = `<span class="text-2xl font-bold text-gray-900 dark:text-white">${newNumber}</span>`;
}