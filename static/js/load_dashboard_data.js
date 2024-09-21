const request_url_ids = [
    ['url_get_total_visited_countries', 'number-total_visited_countries'],
    ['url_get_users_with_visited_countries', 'number-user_with_visited_countries']
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

function updateNumberOnCard(element_id, newNumber) {
    const el = document.getElementById(element_id);
    el.innerHTML = `<h1>${newNumber}</h1>`;
}
