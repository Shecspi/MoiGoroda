<!--
---------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
-->

# DMR City Search With ISO Codes

## Goal

Keep one city-search endpoint while removing the mixed numeric and textual geographic identifiers from its public contract. Migrate the endpoint from DRF function-based view code to DMR without changing its URL or successful response shape.

## API Contract

`GET /api/city/search` accepts:

- `query`: required city-title substring, 1–100 characters;
- `country`: optional two-character `Country.code`, such as `RU`;
- `region`: optional 1–10 character `Region.iso3166`, such as `RU-MOW`;
- `limit`: optional result limit from 1 to 200, defaulting to 50.

The endpoint no longer accepts `country_id` or `region_id`. When a region is selected, the modal sends only `region`, because the globally unique region code already identifies its country. The successful response remains a JSON array whose items contain `id`, `title`, `region`, and `country`.

## Backend Design

- Replace the `city_search` DRF function in `city/api/common.py` with a DMR `CitySearchController` in `city/api/lookups.py`.
- Re-export the controller from `city/api/__init__.py` through `.lookups`, because `city/urls/api.py` resolves `api.CitySearchController`; preserve the unrelated `.visited` export.
- Register the existing `/api/city/search` URL through `dmr.routing.path`.
- Change `CitySearchService.search_cities` to filter by `country__code` and `region__iso3166`; remove its numeric geographic filters.
- Preserve the existing title matching, result priority, ordering, limit, anonymous access, and consumer-visible response format.
- Keep the existing behavior that omits the country label when a country filter is present. A region-filtered result may include the country label.

## File Map

- `city/api/lookups.py`: owns the typed DMR city-search controller.
- `city/api/__init__.py`: re-exports `.lookups` for URL resolution and keeps the unrelated `.visited` export unchanged.
- `city/urls/api.py`: maps the unchanged search URL to `api.CitySearchController`.
- `city/tests/integration/api/test_city_search.py`: verifies validation, ISO filtering, and response compatibility.
- `frontend/js/components/city_cascade_selector.js`: owns code-mode cascade values and request lifecycle.
- `frontend/components/add-city-modal/add-city-modal.js`: connects cascade filter changes to city selection.

## Frontend Design

- Add a configurable code mode to `CityCascadeSelector`; its default ID mode remains unchanged for the city-creation form, whose fields submit numeric foreign keys.
- In code mode, country options use `Country.code`, region options use `Region.iso3166`, and regions are loaded through the existing `/api/region/list/<country_code>/` endpoint.
- Configure the add-city modal to use code mode.
- Change `CityAutocomplete` to send `country` while only a country is selected and `region` after a region is selected. It never sends numeric geographic identifiers.
- Leave the city-list toolbar and personal-collection search consumers on `/api/city/search`; their existing unfiltered or country-code requests remain compatible.

## Error Handling

- Missing, empty, too long, or otherwise invalid `query` values return HTTP 400.
- A country value whose length is not two characters, a blank or overlong region value, and a limit outside 1–200 return HTTP 400 rather than being silently ignored.
- A syntactically valid unknown country or region code returns an empty list.
- Unsupported HTTP methods return HTTP 405.

## Verification

- Contract tests cover DMR routing, successful unfiltered search, country-code filtering, region-code filtering, validation errors, response compatibility, and prohibited methods.
- Service unit tests cover the two code-based ORM filters and removal of numeric-filter behavior.
- Frontend unit tests cover code-mode cascade requests and values, modal filter propagation, and the absence of `country_id`/`region_id` in autocomplete requests.
- Run the focused backend tests sequentially through Poetry, focused Vitest tests, frontend linting for changed files if available, and the frontend production build.
