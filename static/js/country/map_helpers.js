const fillColorVisitedCountry = '#32b700';
const fillColorNotVisitedCountry = '#9a9a9a';
const fillOpacity = 0.6;
const strokeColor = '#FFF';
const strokeOpacity = 0.8;
const strokeWidth = 1;


export function addCountryOnMap(polygon, country, map) {
    const myStyle = {
        "fillColor": country.is_visited ? fillColorVisitedCountry : fillColorNotVisitedCountry,
        "fillOpacity": fillOpacity,
        "weight": strokeWidth,
        "color": strokeColor,
        "opacity": strokeOpacity
    };

    const geoJSON = L.geoJSON(polygon, {
        style: myStyle
    }).addTo(map);

    geoJSON.bindTooltip(country.name_ru, {
        direction: 'top',
        sticky: true
    });
    geoJSON.bindPopup(generatePopupContent(country));

    return geoJSON;
}


/**
 * Подготавливает HTML-содержимое для popup-окна с информацией о стран.е
 * @param country {Country} Объект, содержащий в себе всю необходимую информацию о стране.
 * @returns {string}
 */
function generatePopupContent(country) {
    let content = "";

    if (country.fullname_ru) {
        content += `<div><span class="fw-semibold">Полное название:</span> ${country.fullname_ru}</div>`;
    }

    content +=
        `<div><span class="fw-semibold">Часть света:</span> ${country.part_of_the_world}</div>` +
        `<div><span class="fw-semibold">Расположение:</span> ${country.location}</div>`;

    if (isAuthenticated === true) {
        const linkToAdd = `<hr><a href="#" onclick="add_country();">Отметить страну как посещённую</a>`
        const linkToDelete = `<hr><a href="#" onclick="delete_country('${country.iso3166_1_alpha2}')">Удалить страну</a>`
        const link = country.is_visited ? linkToDelete : linkToAdd;

        return `<h4>${country.name_ru}</h4><br>${content + link}`;
    } else {
        return `<h4>${country.name_ru}</h4><br>${content}`;
    }
}