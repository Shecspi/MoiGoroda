<!--
---------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
-->

# DMR City Search With ISO Codes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Keep one `/api/city/search` endpoint, migrate it to DMR, and replace numeric country and region filters with stable ISO codes.

**Architecture:** DMR parses and validates a typed msgspec query model, then delegates ORM filtering to `CitySearchService`. The add-city modal uses a code-mode variant of the shared cascade selector, while the city-creation form keeps its existing numeric FK mode.

**Tech Stack:** Django 5.2, django-modern-rest 0.3 with msgspec, Django ORM, Vitest 2.1, vanilla JavaScript.

## Global Constraints

- Preserve `/api/city/search` and its successful item fields: `id`, `title`, `region`, `country`.
- Accept only `query`, optional `country`, optional `region`, and optional `limit`; reject removed `country_id` and `region_id` parameters.
- `country` is a two-character `Country.code`; `region` is a 1–10 character globally unique `Region.iso3166`.
- When a region is selected, the modal sends only `region`.
- Keep numeric-ID mode unchanged for the city-creation form.
- Add or preserve the project license comment in every modified or created source file.
- Do not add appearance-only UI tests.
- Run Django tests sequentially through `poetry run pytest`.
- Do not create a git commit unless the user gives a separate explicit command.

---

## File Map

- `city/services/search.py`: owns title matching, priority ordering, ISO-code filters, and result limiting.
- `city/api/lookups.py`: owns typed DMR query/response models and the city-search controller.
- `city/api/__init__.py`: re-exports `.lookups` so the URL module can resolve `api.CitySearchController`; its unrelated `.visited` export remains unchanged.
- `city/api/common.py`: loses the legacy DRF `city_search` function and its now-unused imports.
- `city/urls/api.py`: maps the unchanged search URL to the DMR controller.
- `city/serializers.py`: loses the obsolete DRF query serializer; `CitySerializer` remains for unrelated endpoints.
- `city/tests/unit/services/test_search_service.py`: verifies ORM filtering by country and region codes.
- `city/tests/integration/api/test_city_search.py`: verifies the public DMR contract and response compatibility.
- `city/tests/unit/serializers/test_city_search_params_serializer.py`: removed because DMR msgspec query validation replaces that unit.
- `frontend/js/components/city_cascade_selector.js`: adds opt-in code mode while retaining default ID mode.
- `frontend/js/components/city_cascade_selector.test.js`: verifies both modes and the region-by-country-code request.
- `frontend/js/components/city_autocomplete.js`: sends the most specific selected ISO filter.
- `frontend/js/components/city_autocomplete.test.js`: verifies country-only and region-only search URLs.
- `frontend/components/add-city-modal/add-city-modal.js`: wires code-mode cascade values into autocomplete.
- `frontend/components/add-city-modal/add-city-modal.test.js`: verifies the complete modal country → region → city flow.

---

### Task 1: Replace Numeric Search Filters With ISO Codes In The Service

**Files:**
- Modify: `city/tests/unit/services/test_search_service.py`
- Modify: `city/services/search.py`

**Interfaces:**
- Consumes: `City`, `Country.code`, and `Region.iso3166`.
- Produces: `CitySearchService.search_cities(query: str, country: str | None = None, region: str | None = None, limit: int = 50) -> QuerySet[City]`.

- [ ] **Step 1: Replace the numeric-filter unit test with code-filter tests**

```python
@patch('city.services.search.City.objects')
def test_search_cities_filters_by_country_code(mock_city_objects: MagicMock) -> None:
    queryset = MagicMock()
    mock_city_objects.select_related.return_value = queryset
    queryset.filter.return_value = queryset
    queryset.annotate.return_value = queryset
    queryset.order_by.return_value = queryset
    queryset.__getitem__.return_value = queryset

    CitySearchService.search_cities(query='Моск', country='RU')

    queryset.filter.assert_has_calls([
        call(title__icontains='Моск'),
        call(country__code='RU'),
    ])


@patch('city.services.search.City.objects')
def test_search_cities_filters_by_region_iso3166(mock_city_objects: MagicMock) -> None:
    queryset = MagicMock()
    mock_city_objects.select_related.return_value = queryset
    queryset.filter.return_value = queryset
    queryset.annotate.return_value = queryset
    queryset.order_by.return_value = queryset
    queryset.__getitem__.return_value = queryset

    CitySearchService.search_cities(query='Моск', region='RU-MOW')

    queryset.filter.assert_has_calls([
        call(title__icontains='Моск'),
        call(region__iso3166='RU-MOW'),
    ])
```

- [ ] **Step 2: Run the focused service tests and confirm the region test fails**

Run:

```bash
poetry run pytest city/tests/unit/services/test_search_service.py -q
```

Expected: the new region test fails because `search_cities` does not yet accept `region`, and the removed numeric behavior is no longer the expected interface.

- [ ] **Step 3: Narrow the service signature and ORM filters**

```python
@staticmethod
def search_cities(
    query: str,
    country: str | None = None,
    region: str | None = None,
    limit: int = 50,
) -> QuerySet[City]:
    cities_queryset = (
        City.objects.select_related('country', 'region')
        .filter(title__icontains=query)
        .annotate(
            search_priority=Case(
                When(title__istartswith=query, then=1),
                default=2,
                output_field=IntegerField(),
            )
        )
        .order_by('search_priority', 'title')
    )
    if country:
        cities_queryset = cities_queryset.filter(country__code=country)
    if region:
        cities_queryset = cities_queryset.filter(region__iso3166=region)
    return cities_queryset[:limit]
```

Remove `country_id` and `region_id` from the method, docstring, and implementation. Keep title filtering, `select_related`, priority annotation, ordering, and slicing unchanged.

- [ ] **Step 4: Run the service tests again**

Run:

```bash
poetry run pytest city/tests/unit/services/test_search_service.py -q
```

Expected: all tests in the file pass.

- [ ] **Step 5: Review the task diff without committing**

Run:

```bash
git diff -- city/services/search.py city/tests/unit/services/test_search_service.py
```

Expected: only the service contract and its code-filter tests changed.

---

### Task 2: Migrate `/api/city/search` To A Typed DMR Controller

**Files:**
- Modify: `city/tests/integration/api/test_city_search.py`
- Modify: `city/api/lookups.py`
- Modify: `city/api/__init__.py`
- Modify: `city/api/common.py`
- Modify: `city/urls/api.py`
- Modify: `city/serializers.py`
- Delete: `city/tests/unit/serializers/test_city_search_params_serializer.py`

**Interfaces:**
- Consumes: `CitySearchService.search_cities(query, country, region, limit)` from Task 1.
- Produces: `CitySearchQuery`, `CitySearchItem`, and `CitySearchController` in `city.api.lookups`, re-exported by `city.api.__init__`; route name remains `city_search`.

- [ ] **Step 1: Rewrite contract tests around DMR and ISO filters**

Add the controller assertion and replace the numeric-ID test with region-code and removed-parameter tests:

```python
from dmr import Controller

from city.api.lookups import CitySearchController


def test_uses_django_modern_rest_controller(self) -> None:
    assert issubclass(CitySearchController, Controller)


@patch('city.services.search.CitySearchService.search_cities')
def test_search_cities_with_region_code(
    self,
    mock_search: MagicMock,
    api_client: APIClient,
    mock_city: MagicMock,
) -> None:
    mock_city.id = 1
    mock_city.title = 'Москва'
    mock_city.region.full_name = 'Москва'
    mock_city.country.name = 'Россия'
    mock_search.return_value = [mock_city]

    response = api_client.get(self.url, {'query': 'Моск', 'region': 'RU-MOW'})

    assert response.status_code == status.HTTP_200_OK
    mock_search.assert_called_once_with(
        query='Моск', country=None, region='RU-MOW', limit=50,
    )
    assert response.json()[0]['country'] == 'Россия'


@pytest.mark.parametrize('removed_param', ['country_id', 'region_id'])
def test_rejects_removed_numeric_filters(
    self,
    api_client: APIClient,
    removed_param: str,
) -> None:
    response = api_client.get(self.url, {'query': 'Моск', removed_param: '1'})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize(
    ('params', 'invalid_field'),
    [
        ({'query': 'Моск', 'country': 'R'}, 'country'),
        ({'query': 'Моск', 'region': 'R' * 11}, 'region'),
        ({'query': 'Моск', 'limit': '201'}, 'limit'),
    ],
)
def test_rejects_invalid_query_values(
    self,
    api_client: APIClient,
    params: dict[str, str],
    invalid_field: str,
) -> None:
    response = api_client.get(self.url, params)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert invalid_field in str(response.json())


@pytest.mark.parametrize(
    'location_filter',
    [{'country': 'ZZ'}, {'region': 'ZZ-UNKNOWN'}],
)
def test_unknown_valid_location_code_returns_empty_list(
    self,
    api_client: APIClient,
    location_filter: dict[str, str],
) -> None:
    response = api_client.get(self.url, {'query': 'Несуществующий', **location_filter})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []
```

Update existing mock assertions so every service call includes `region=None`. Keep tests for query validation, country filtering, default/custom limit, empty results, and prohibited methods; adjust validation assertions to DMR's `detail` response instead of DRF field dictionaries.

- [ ] **Step 2: Run the endpoint tests and confirm they fail against the DRF view**

Run:

```bash
poetry run pytest city/tests/integration/api/test_city_search.py -q
```

Expected: DMR controller, region filtering, and numeric-parameter rejection tests fail.

- [ ] **Step 3: Define constrained msgspec query and response types**

In `city/api/lookups.py`, add:

```python
from typing import Annotated, Any

import msgspec
from dmr import Controller, Query, ResponseSpec, modify

from city.services.search import CitySearchService


SearchText = Annotated[str, msgspec.Meta(min_length=1, max_length=100)]
CountryCode = Annotated[str, msgspec.Meta(min_length=2, max_length=2)]
RegionCode = Annotated[str, msgspec.Meta(min_length=1, max_length=10)]
SearchLimit = Annotated[int, msgspec.Meta(ge=1, le=200)]


class CitySearchQuery(msgspec.Struct, kw_only=True, forbid_unknown_fields=True):
    query: SearchText
    country: CountryCode | None = None
    region: RegionCode | None = None
    limit: SearchLimit = 50


class CitySearchItem(msgspec.Struct):
    id: int
    title: str
    region: str | None
    country: str | None
```

`forbid_unknown_fields=True` is required so removed numeric parameters produce HTTP 400 instead of silently becoming an unfiltered query.

- [ ] **Step 4: Implement the DMR query controller**

```python
class CitySearchController(
    Query[CitySearchQuery],
    Controller[MsgspecSerializer],
):
    @modify(
        status_code=HTTPStatus.OK,
        extra_responses=[
            ResponseSpec(dict[str, list[dict[str, str]]], status_code=HTTPStatus.BAD_REQUEST),
        ],
        tags=['Города'],
    )
    def get(self) -> Any:
        params = self.parsed_query
        query = params.query.strip()
        if not query:
            return self.to_response(
                raw_data={'detail': [{'msg': 'Параметр query не должен быть пустым'}]},
                status_code=HTTPStatus.BAD_REQUEST,
            )

        cities = CitySearchService.search_cities(
            query=query,
            country=params.country,
            region=params.region,
            limit=params.limit,
        )
        return self.to_response(
            raw_data=[
                CitySearchItem(
                    id=city.id,
                    title=city.title,
                    region=city.region.full_name if city.region is not None else None,
                    country=(
                        None
                        if params.country is not None
                        else city.country.name if city.country is not None else None
                    ),
                )
                for city in cities
            ],
            status_code=HTTPStatus.OK,
        )
```

This preserves query trimming and the existing country-label omission for country-filtered searches. Region-filtered results retain their country label.

- [ ] **Step 5: Replace the route and remove the legacy DRF endpoint**

In `city/api/__init__.py`, preserve the unrelated `.visited` export and expose the controller through:

```python
from .lookups import *
```

In `city/urls/api.py`:

```python
dmr_path('search', api.CitySearchController.as_view(), name='city_search'),
```

Delete `city_search` from `city/api/common.py`, remove its now-unused `CitySearchParamsSerializer` and `CitySearchService` imports, delete `CitySearchParamsSerializer` from `city/serializers.py`, and delete its dedicated unit-test file. Do not remove `CitySerializer`, because other city endpoints still use it.

- [ ] **Step 6: Run backend search tests sequentially**

Run:

```bash
poetry run pytest city/tests/unit/services/test_search_service.py city/tests/integration/api/test_city_search.py -q
```

Expected: both files pass. If PostgreSQL test database creation fails with the known collation-version error, report it as an infrastructure blocker and still run the unit-only file separately.

- [ ] **Step 7: Run static backend checks for changed Python files**

Run:

```bash
poetry run ruff check city/api/lookups.py city/api/common.py city/urls/api.py city/serializers.py city/services/search.py city/tests/integration/api/test_city_search.py city/tests/unit/services/test_search_service.py
poetry run mypy city/api/lookups.py city/services/search.py
```

Expected: both commands exit successfully.

---

### Task 3: Add Opt-In ISO-Code Mode To The Cascade Selector

**Files:**
- Modify: `frontend/js/components/city_cascade_selector.test.js`
- Modify: `frontend/js/components/city_cascade_selector.js`

**Interfaces:**
- Consumes: country items with `id`, `code`, `name`; region items with `id`, `iso3166`, `title`.
- Produces: constructor option `locationValueMode: 'id' | 'code'`; code-mode `value` is `{countryCode, regionCode, cityId}` and default mode remains `{countryId, regionId, cityId}`.

- [ ] **Step 1: Add a failing code-mode test without changing existing ID-mode tests**

```javascript
it('uses ISO codes for a modal without a city select', async () => {
    document.querySelector('[data-city]').remove();
    fetch
        .mockResolvedValueOnce({
            ok: true,
            json: vi.fn().mockResolvedValue([{id: 1, code: 'RU', name: 'Россия'}]),
        })
        .mockResolvedValueOnce({
            ok: true,
            json: vi.fn().mockResolvedValue([
                {id: 10, iso3166: 'RU-MOW', title: 'Москва'},
            ]),
        });
    const onChange = vi.fn();
    const selector = new CityCascadeSelector(document.body, {
        locationValueMode: 'code',
        onChange,
    });

    await selector.init();
    const country = document.querySelector('[data-city-country]');
    country.value = 'RU';
    country.dispatchEvent(new Event('change'));
    await vi.waitFor(() => {
        expect(document.querySelector('[data-city-region] option[value="RU-MOW"]')).not.toBeNull();
    });
    const region = document.querySelector('[data-city-region]');
    region.value = 'RU-MOW';
    region.dispatchEvent(new Event('change'));

    expect(fetch.mock.calls[1][0]).toBe('/api/region/list/RU/');
    expect(onChange).toHaveBeenLastCalledWith({
        countryCode: 'RU',
        regionCode: 'RU-MOW',
        cityId: '',
    });
});
```

- [ ] **Step 2: Run the selector test and confirm code mode is missing**

Run from `frontend/`:

```bash
npm run test -- js/components/city_cascade_selector.test.js
```

Expected: the new test fails because options still use IDs and the request still uses `country_id`.

- [ ] **Step 3: Implement code-mode value selection and region URL generation**

Add `locationValueMode = 'id'` to the constructor options and store it. Add focused helpers:

```javascript
getOptionValue(select, item) {
    if (this.locationValueMode === 'code' && select === this.countrySelect) {
        return String(item.code);
    }
    if (this.locationValueMode === 'code' && select === this.regionSelect) {
        return String(item.iso3166);
    }
    return String(item.id);
}

getRegionsUrl(countryValue) {
    if (this.locationValueMode === 'code') {
        return `/api/region/list/${encodeURIComponent(countryValue)}/`;
    }
    return `/api/region/list?country_id=${encodeURIComponent(countryValue)}`;
}
```

Use `getOptionValue(select, item)` inside `setOptions` so only country and region values switch to codes; city options always keep numeric IDs. Implement the `value` getter explicitly:

```javascript
get value() {
    const cityId = this.citySelect?.value || '';
    if (this.locationValueMode === 'code') {
        return {
            countryCode: this.countrySelect?.value || '',
            regionCode: this.regionSelect?.value || '',
            cityId,
        };
    }
    return {
        countryId: this.countrySelect?.value || '',
        regionId: this.regionSelect?.value || '',
        cityId,
    };
}
```

- [ ] **Step 4: Run the complete selector test file**

Run from `frontend/`:

```bash
npm run test -- js/components/city_cascade_selector.test.js
```

Expected: the new code-mode test and all existing ID-mode tests pass.

- [ ] **Step 5: Review the selector diff without committing**

Run:

```bash
git diff -- frontend/js/components/city_cascade_selector.js frontend/js/components/city_cascade_selector.test.js
```

Expected: default ID URLs and returned field names remain covered and unchanged.

---

### Task 4: Send ISO Filters From Autocomplete And The Modal

**Files:**
- Modify: `frontend/js/components/city_autocomplete.test.js`
- Modify: `frontend/js/components/city_autocomplete.js`
- Modify: `frontend/components/add-city-modal/add-city-modal.test.js`
- Modify: `frontend/components/add-city-modal/add-city-modal.js`

**Interfaces:**
- Consumes: code-mode selector payload `{countryCode, regionCode, cityId}` from Task 3.
- Produces: `CityAutocomplete.setFilters({country?: string, region?: string})`; requests include `region` when present, otherwise `country`, and never numeric geographic filters.

- [ ] **Step 1: Replace the autocomplete numeric-filter test with country and region tests**

```javascript
it('filters by country code when no region is selected', async () => {
    fetch.mockResolvedValue({
        ok: true,
        json: vi.fn().mockResolvedValue([
            {id: 42, title: 'Москва', region: 'Москва', country: 'Россия'},
        ]),
    });
    const root = document.querySelector('[data-city-autocomplete]');
    const autocomplete = new CityAutocomplete(root);
    autocomplete.init();
    const input = root.querySelector('[data-city-autocomplete-input]');
    autocomplete.setFilters({country: 'RU'});
    input.value = 'Моск';
    input.dispatchEvent(new Event('input'));
    await vi.waitFor(() => expect(fetch).toHaveBeenCalledOnce());

    expect(fetch.mock.calls[0][0]).toBe(
        '/api/city/search?query=%D0%9C%D0%BE%D1%81%D0%BA&country=RU',
    );
});

it('sends only the region code when a region is selected', async () => {
    fetch.mockResolvedValue({
        ok: true,
        json: vi.fn().mockResolvedValue([
            {id: 42, title: 'Москва', region: 'Москва', country: 'Россия'},
        ]),
    });
    const root = document.querySelector('[data-city-autocomplete]');
    const autocomplete = new CityAutocomplete(root);
    autocomplete.init();
    const input = root.querySelector('[data-city-autocomplete-input]');
    autocomplete.setFilters({country: 'RU', region: 'RU-MOW'});
    input.value = 'Моск';
    input.dispatchEvent(new Event('input'));
    await vi.waitFor(() => expect(fetch).toHaveBeenCalledOnce());

    expect(fetch.mock.calls[0][0]).toBe(
        '/api/city/search?query=%D0%9C%D0%BE%D1%81%D0%BA&region=RU-MOW',
    );
});
```

Update the abort-on-filter-change test to call `setFilters({country: 'RU', region: 'RU-MOW'})`.

- [ ] **Step 2: Update the modal integration-style unit test for code values**

Use country and region payloads that contain codes:

```javascript
json: vi.fn().mockResolvedValue([{id: 7, code: 'RU', name: 'Россия'}])
json: vi.fn().mockResolvedValue([
    {id: 11, iso3166: 'RU-MOW', title: 'Москва', country_code: 'RU'},
])
```

Select `RU` and `RU-MOW`, then assert that the third fetch URL is:

```javascript
'/api/city/search?query=%D0%9C%D0%BE%D1%81%D0%BA&region=RU-MOW'
```

- [ ] **Step 3: Run the focused frontend tests and confirm they fail**

Run from `frontend/`:

```bash
npm run test -- js/components/city_autocomplete.test.js components/add-city-modal/add-city-modal.test.js
```

Expected: tests fail because autocomplete and modal still exchange numeric IDs.

- [ ] **Step 4: Change `CityAutocomplete` to code filters with most-specific precedence**

```javascript
setFilters({country = '', region = ''}) {
    this.country = country;
    this.region = region;
    this.controller?.abort();
    this.controller = null;
    this.requestVersion += 1;
    this.input.value = '';
    this.clearResults();
    this.onSelect(null);
}

const params = new URLSearchParams({query});
if (this.region) {
    params.set('region', this.region);
} else if (this.country) {
    params.set('country', this.country);
}
```

Rename `countryId`/`regionId` instance fields to `country`/`region`. Do not change rendering, keyboard navigation, selection, loading, or stale-request handling.

- [ ] **Step 5: Configure the modal for code mode**

```javascript
this.cityCascadeSelector = new CityCascadeSelector(this, {
    locationValueMode: 'code',
    onChange: ({countryCode, regionCode}) => {
        this.cityAutocomplete.setFilters({
            country: countryCode,
            region: regionCode,
        });
    },
    onError: () => {
        showDangerToast('Ошибка', 'Не удалось загрузить список городов. Попробуйте ещё раз.');
    },
});
```

- [ ] **Step 6: Run all focused frontend tests**

Run from `frontend/`:

```bash
npm run test -- js/components/city_cascade_selector.test.js js/components/city_autocomplete.test.js components/add-city-modal/add-city-modal.test.js
```

Expected: all focused tests pass.

- [ ] **Step 7: Search for stale numeric city-search consumers**

Run from the repository root:

```bash
rg -n "city/search.*(country_id|region_id)|setFilters\(\{countryId|regionId" frontend city
```

Expected: no runtime code or tests pass `country_id`/`region_id` to `/api/city/search`; matches belonging to other ID-based lookup endpoints are out of scope and remain unchanged.

---

### Task 5: Final Verification

**Files:**
- Verify only; modify source files only if a verification failure identifies a regression in this feature.

**Interfaces:**
- Consumes: completed backend and frontend tasks.
- Produces: evidence that the DMR contract, both selector modes, and production assets are valid.

- [ ] **Step 1: Run the focused backend suite sequentially**

```bash
poetry run pytest city/tests/unit/services/test_search_service.py city/tests/integration/api/test_city_search.py -q
```

Expected: all selected tests pass, subject only to the documented PostgreSQL collation infrastructure blocker.

- [ ] **Step 2: Run the focused frontend suite**

From `frontend/`:

```bash
npm run test -- js/components/city_cascade_selector.test.js js/components/city_autocomplete.test.js components/add-city-modal/add-city-modal.test.js
```

Expected: all selected Vitest tests pass.

- [ ] **Step 3: Run Python static checks**

```bash
poetry run ruff check city/api/lookups.py city/api/common.py city/urls/api.py city/serializers.py city/services/search.py city/tests/integration/api/test_city_search.py city/tests/unit/services/test_search_service.py
poetry run mypy city/api/lookups.py city/services/search.py
```

Expected: both commands exit successfully.

- [ ] **Step 4: Build production frontend assets**

From `frontend/`:

```bash
npm run build
```

Expected: Vite exits successfully and writes the configured production manifest without warnings introduced by these changes.

- [ ] **Step 5: Review final scope and status without staging or committing**

```bash
git status --short
git diff --check
git diff --stat
```

Expected: no whitespace errors; the new design and plan documents plus the intended backend/frontend files are present, while unrelated pre-existing changes remain untouched.
