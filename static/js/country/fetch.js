function getDataFromServer(url) {
    return fetch(url + '?' + new URLSearchParams({'from': 'country map'}))
        .then((response) => {
            if (!response.ok) {
                throw new Error(response.statusText)
            }
            return response.json();
        })
        .then((data) => {
            return data;
        });
}

export function getAllPolygons() {
    const url = `${document.getElementById('url_get_polygons').dataset.url}/country/all`;
    return getDataFromServer(url);
}

export function getAllCountries() {
    const url = document.getElementById('url_get_all_countries').dataset.url;
    return getDataFromServer(url);
}

export function getVisitedCountries() {
    const url = document.getElementById('url_get_visited_countries').dataset.url;
    return getDataFromServer(url);
}

export function getPartsOfTheWorld() {
    const url = document.getElementById('url_get_parts_of_the_world').dataset.url;
    return getDataFromServer(url);
}

export function getLocations() {
    const url = document.getElementById('url_get_locations').dataset.url;
    return getDataFromServer(url);
}