export class City {
    id;
    name;
    region;
    country;
    lat;
    lon;
    first_visit_date;
    last_visit_date;
    number_of_visits;
    visit_years;
}

export const MarkerStyle = {
    OWN: 'own',
    TOGETHER: 'together',
    SUBSCRIPTION: 'subscription',
    NOT_VISITED: 'not_visited'
}