<!--
# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------
-->

# City Timeline Lazy Loading Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Загружать общую и региональную хронологию городов через два API только после первого открытия модального окна.

**Architecture:** ORM-логика обеих хронологий переносится в `city.services.timeline`, а два тонких DMR-контроллера разрешают область выборки и сериализуют единый контракт. Страницы рендерят только каркас модального окна с API URL; общий JavaScript запрашивает, безопасно отображает и кэширует успешный ответ в DOM.

**Tech Stack:** Python 3.12, Django 5.2, Django REST Framework, PostgreSQL ORM, Django templates, JavaScript, Vitest 2.1, happy-dom, Vite 5.4, Tailwind CSS 4, daisyUI 5.

## Global Constraints

- Реализовать ровно два GET-эндпоинта: `/api/city/timeline` и `/api/region/<region_id>/city_timeline`.
- Реализовать оба endpoint только через django-modern-rest `Controller`, DMR Router/path и типизированные msgspec-схемы.
- Оба API используют только `request.user`; идентификатор пользователя не принимается от клиента.
- Без `country` общая хронология полная, с `country` ограничена указанной страной.
- Региональная хронология включает непосещённые города, общая — только посещения.
- Порядок, повторные посещения, фильтрация по годам и прокрутка сохраняют текущее поведение.
- Успешный ответ, включая пустой, запрашивается один раз за жизнь страницы; после ошибки разрешён новый запрос.
- Значения из API вставляются только через DOM API и `textContent`.
- Модальная хронология коллекции остаётся совместима с общим `timeline_modal.js` и не выполняет fetch без `data-timeline-url`.
- Во все создаваемые и редактируемые файлы добавить лицензионный блок проекта; в Python он располагается до module docstring и импортов.
- Backend-тесты запускать последовательно через `poetry run pytest`, не создавая параллельные процессы с общей test DB.
- Коммиты не создавать без отдельной прямой команды пользователя.

---

### Task 1: Timeline Query Service

**Files:**
- Create: `city/services/timeline.py`
- Create: `city/tests/integration/services/test_timeline.py`

**Interfaces:**
- Consumes: `City`, `VisitedCity`, валидные `user_id`, `country_id` и `region_id`.
- Produces: `build_city_timeline(*, user_id: int, country_id: int | None = None) -> TimelineResult`.
- Produces: `build_region_city_timeline(*, user_id: int, region_id: int) -> TimelineResult`.
- Produces: `TimelineItem` с обязательными `city_title`, `date_label`, `status`, `year`, `is_first_visited` и `TimelineResult` с `items`, `years`.

- [ ] **Step 1: Написать падающие интеграционные тесты сервиса**

Создать реальные страны, регион, города, двух пользователей и посещения с датами `2024-05-02`, `2024-01-01`, `2023-06-03` и `None`. Проверки должны явно фиксировать:

```python
result = build_city_timeline(user_id=user.id)

assert [item['city_title'] for item in result['items']] == [
    'Повторный город',
    'Повторный город',
    'Старый город',
    'Город без даты',
]
assert [item['year'] for item in result['items']] == [2024, 2024, 2023, None]
assert [item['is_first_visited'] for item in result['items']] == [True, False, False, False]
assert result['years'] == [2024, 2023]
```

Добавить отдельную проверку страны и пользователя:

```python
result = build_city_timeline(user_id=user.id, country_id=russia.id)

assert {item['city_title'] for item in result['items']} == {
    'Повторный город',
    'Старый город',
    'Город без даты',
}
assert 'Иностранный город' not in {item['city_title'] for item in result['items']}
assert 'Город другого пользователя' not in {item['city_title'] for item in result['items']}
```

Для региона проверить три группы и первый посещённый элемент:

```python
result = build_region_city_timeline(user_id=user.id, region_id=region.id)

assert [(item['city_title'], item['status']) for item in result['items']] == [
    ('Непосещённый город', 'unvisited'),
    ('Повторный город', 'visited'),
    ('Повторный город', 'visited'),
    ('Старый город', 'visited'),
    ('Город без даты', 'visited'),
]
assert [item['is_first_visited'] for item in result['items']] == [False, True, False, False, False]
assert result['years'] == [2024, 2023]
```

- [ ] **Step 2: Запустить тесты и подтвердить ожидаемое падение**

Run:

```bash
poetry run pytest city/tests/integration/services/test_timeline.py -q
```

Expected: FAIL на импорте отсутствующего `city.services.timeline`.

- [ ] **Step 3: Реализовать минимальный типизированный сервис**

Создать типы и функции с такой формой:

```python
class TimelineItem(TypedDict):
    city_title: str
    date_label: str
    status: Literal['visited', 'unvisited']
    year: int | None
    is_first_visited: bool


class TimelineResult(TypedDict):
    items: list[TimelineItem]
    years: list[int]


def build_city_timeline(*, user_id: int, country_id: int | None = None) -> TimelineResult:
    dated_visits = VisitedCity.objects.filter(
        user_id=user_id,
        date_of_visit__isnull=False,
    )
    undated_visits = VisitedCity.objects.filter(
        user_id=user_id,
        date_of_visit__isnull=True,
    )
    if country_id is not None:
        dated_visits = dated_visits.filter(city__country_id=country_id)
        undated_visits = undated_visits.filter(city__country_id=country_id)
    return _build_result(
        unvisited_titles=(),
        dated_visits=dated_visits.select_related('city').order_by(
            '-date_of_visit', 'city__title', 'id'
        ),
        undated_visits=undated_visits.select_related('city').order_by('city__title', 'id'),
    )
```

`build_region_city_timeline` получает непосещённые города через `Exists(VisitedCity.objects.filter(city_id=OuterRef('pk'), user_id=user_id))`, затем передаёт три упорядоченных набора в `_build_result`. `_build_result` создаёт обязательные поля каждого элемента, помечает только первый `visited`, а годы собирает в `set[int]` и сортирует по убыванию.

- [ ] **Step 4: Запустить тесты сервиса до зелёного результата**

Run:

```bash
poetry run pytest city/tests/integration/services/test_timeline.py -q
```

Expected: PASS без warnings и ошибок логирования.

---

### Task 2: City Timeline API

**Files:**
- Create: `city/api/timeline.py`
- Modify: `city/api/__init__.py`
- Modify: `city/urls/api.py`
- Create: `city/tests/integration/api/test_city_timeline.py`

**Interfaces:**
- Consumes: `build_city_timeline`, `Country.code`, `request.user.pk`, необязательный query-параметр `country`.
- Produces: named route `api__get_city_timeline` по адресу `/api/city/timeline`.
- Produces: `200 {"items": [...], "years": [...]}`, `401` для гостя, `404` для неизвестной страны, `405` для методов кроме GET.

- [ ] **Step 1: Написать падающие API-тесты**

Создать `TestCityTimelineAPI` с `APIClient` и `reverse('api__get_city_timeline')`. Зафиксировать минимум следующие утверждения:

```python
def test_guest_returns_401(api_client: APIClient) -> None:
    response = api_client.get(reverse('api__get_city_timeline'))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize('method', ['post', 'put', 'patch', 'delete'])
def test_rejects_non_get_methods(
    api_client: APIClient,
    authenticated_user: User,
    method: str,
) -> None:
    response = getattr(api_client, method)(reverse('api__get_city_timeline'))
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
```

Добавить реальные данные и проверить полный ответ, `?country=RU`, `?country=ZZ`, пустые массивы и отсутствие посещений второго пользователя. Для фильтра обязательно проверить, что URL передаёт код, а сервис получает ID найденной страны.

- [ ] **Step 2: Запустить API-тесты и подтвердить ожидаемое падение**

Run:

```bash
poetry run pytest city/tests/integration/api/test_city_timeline.py -q
```

Expected: FAIL из-за отсутствующего route `api__get_city_timeline`.

- [ ] **Step 3: Добавить маршрут и обработчик**

В `city/urls/api.py` добавить:

```python
dmr_path(
    'timeline',
    api.GetCityTimelineController.as_view(),
    name='api__get_city_timeline',
),
```

В `city/api/__init__.py` реэкспортировать `timeline`. Обработчик должен иметь следующую последовательность:

```python
class GetCityTimelineController(Controller[MsgspecSerializer]):
    @modify(
        status_code=HTTPStatus.OK,
        extra_responses=[
            ResponseSpec(TimelineErrorResponse, status_code=HTTPStatus.UNAUTHORIZED),
            ResponseSpec(TimelineErrorResponse, status_code=HTTPStatus.NOT_FOUND),
            ResponseSpec(TimelineErrorResponse, status_code=HTTPStatus.METHOD_NOT_ALLOWED),
        ],
    )
    def get(self) -> TimelineResponse:
        user = self.request.user
        if not user.is_authenticated or user.pk is None:
            raise APIError(
                TimelineErrorResponse(detail='Пользователь должен быть авторизован'),
                status_code=HTTPStatus.UNAUTHORIZED,
            )
        country_code = self.request.GET.get('country')
        country_id: int | None = None
        if country_code is not None:
            country = Country.objects.filter(code=country_code).only('id').first()
            if country is None:
                raise APIError(
                    TimelineErrorResponse(
                        detail=f'Страна с кодом {country_code} не найдена'
                    ),
                    status_code=HTTPStatus.NOT_FOUND,
                )
            country_id = country.id
        result = build_city_timeline(
            user_id=user.pk,
            country_id=country_id,
        )
        return msgspec.convert(result, type=TimelineResponse, strict=True)

    def handle_method_not_allowed(self, method: str) -> HttpResponse:
        return self.to_response(
            raw_data=TimelineErrorResponse(detail=f'Метод "{method}" не разрешен.'),
            status_code=HTTPStatus.METHOD_NOT_ALLOWED,
            headers={'Allow': 'GET'},
        )
```

- [ ] **Step 4: Запустить API и сервисные тесты**

Run:

```bash
poetry run pytest city/tests/integration/api/test_city_timeline.py city/tests/integration/services/test_timeline.py -q
```

Expected: PASS.

---

### Task 3: Region Timeline API

**Files:**
- Modify: `region/api.py`
- Modify: `region/urls/api.py`
- Create: `region/tests/integration/test_city_timeline_api.py`

**Interfaces:**
- Consumes: `build_region_city_timeline`, `Region.pk`, `request.user.pk`.
- Produces: named route `api__get_region_city_timeline` по адресу `/api/region/<region_id>/city_timeline`.
- Produces: тот же JSON-контракт, `401` для гостя, `404` для неизвестного региона и `405` для методов кроме GET.

- [ ] **Step 1: Написать падающие тесты регионального API**

Использовать `APIClient.force_login`, фикстуры региона и реальные города. Зафиксировать доступ и область:

```python
url = reverse('api__get_region_city_timeline', kwargs={'region_id': test_region.pk})
response = api_client.get(url)
assert response.status_code == status.HTTP_401_UNAUTHORIZED
```

После аутентификации проверить порядок `unvisited`, dated, undated; повторные посещения; уникальные годы; город, посещённый только другим пользователем, как `unvisited`; пустой регион; неизвестный ID; методы POST/PUT/PATCH/DELETE.

- [ ] **Step 2: Запустить тесты и подтвердить ожидаемое падение**

Run:

```bash
poetry run pytest region/tests/integration/test_city_timeline_api.py -q
```

Expected: FAIL из-за отсутствующего route `api__get_region_city_timeline`.

- [ ] **Step 3: Добавить маршрут и обработчик**

В `region/urls/api.py` добавить:

```python
dmr_path(
    '<int:region_id>/city_timeline',
    GetRegionCityTimelineController.as_view(),
    name='api__get_region_city_timeline',
),
```

В `region/api.py` реализовать:

```python
class GetRegionCityTimelineController(Controller[MsgspecSerializer]):
    @modify(
        status_code=HTTPStatus.OK,
        extra_responses=[
            ResponseSpec(TimelineErrorResponse, status_code=HTTPStatus.UNAUTHORIZED),
            ResponseSpec(TimelineErrorResponse, status_code=HTTPStatus.NOT_FOUND),
            ResponseSpec(TimelineErrorResponse, status_code=HTTPStatus.METHOD_NOT_ALLOWED),
        ],
    )
    def get(self) -> TimelineResponse:
        user = self.request.user
        if not user.is_authenticated or user.pk is None:
            raise APIError(
                TimelineErrorResponse(detail='Пользователь должен быть авторизован'),
                status_code=HTTPStatus.UNAUTHORIZED,
            )
        region_id = int(self.kwargs['region_id'])
        if not Region.objects.filter(pk=region_id).exists():
            raise APIError(
                TimelineErrorResponse(detail=f'Регион с ID {region_id} не найден'),
                status_code=HTTPStatus.NOT_FOUND,
            )
        result = build_region_city_timeline(user_id=user.pk, region_id=region_id)
        return msgspec.convert(result, type=TimelineResponse, strict=True)

    def handle_method_not_allowed(self, method: str) -> HttpResponse:
        return self.to_response(
            raw_data=TimelineErrorResponse(detail=f'Метод "{method}" не разрешен.'),
            status_code=HTTPStatus.METHOD_NOT_ALLOWED,
            headers={'Allow': 'GET'},
        )
```

- [ ] **Step 4: Запустить тесты обоих API и сервиса**

Run:

```bash
poetry run pytest city/tests/integration/services/test_timeline.py city/tests/integration/api/test_city_timeline.py region/tests/integration/test_city_timeline_api.py -q
```

Expected: PASS.

---

### Task 4: Remove Timeline Work From Initial Page Rendering

**Files:**
- Modify: `city/views.py:559-613`
- Modify: `region/views.py:409-484`
- Modify: `templates/city/list/toolbar.html:76-165`
- Modify: `templates/region/selected/list/toolbar.html:57-144`
- Modify: `city/tests/integration/views/list/test_content.py:130-219`
- Modify: `region/tests/integration/test_views.py:383-473`

**Interfaces:**
- Consumes: routes `api__get_city_timeline`, `api__get_region_city_timeline`, existing `country_code`, `region_id`.
- Produces: `dialog[data-timeline-url]` с постоянными loading/error/retry/empty/items/year-filter hooks.
- Produces: page-view context без timeline item/year collections и без timeline ORM-запросов.

- [ ] **Step 1: Заменить старые view-тесты падающими проверками нового контракта**

Для city-view проверить:

```python
response = client.get(reverse('city-all-list'))
assert 'city_timeline_items' not in response.context
assert 'city_timeline_years' not in response.context
content = response.content.decode()
assert f'data-timeline-url="{reverse("api__get_city_timeline")}"' in content
assert 'data-timeline-loading' in content
assert 'data-timeline-error' in content
assert 'data-timeline-retry' in content
assert 'data-timeline-empty' in content
assert 'data-timeline-items' in content
assert 'data-timeline-item' not in content
```

Отдельный запрос `reverse('city-all-list') + '?country=RU'` должен содержать `data-timeline-url="/api/city/timeline?country=RU"`. Для региональной страницы проверить отсутствие `region_timeline_items`/`region_timeline_years` и URL с текущим `region_id`.

- [ ] **Step 2: Запустить view-тесты и подтвердить падение на старом серверном рендеринге**

Run:

```bash
poetry run pytest city/tests/integration/views/list/test_content.py region/tests/integration/test_views.py -q
```

Expected: FAIL, потому что timeline context и предварительно отрисованные элементы ещё присутствуют.

- [ ] **Step 3: Удалить вычисление хронологии из page-view**

Удалить из `VisitedCity_List.get_context_data()` блок `city_timeline_items`/`city_timeline_years` и метод `get_city_timeline_items`. Удалить из регионального `get_context_data()` list-only timeline block и метод `get_region_timeline_items`. После удаления очистить только ставшие неиспользуемыми импорты `Exists`/`OuterRef`; не затрагивать импорты, используемые остальной логикой файлов.

- [ ] **Step 4: Заменить серверные элементы каркасом модального окна**

На city dialog установить:

```django
data-timeline-url="{% url 'api__get_city_timeline' %}{% if country_code %}?country={{ country_code }}{% endif %}"
data-timeline-load-state="idle"
```

На region dialog установить:

```django
data-timeline-url="{% url 'api__get_region_city_timeline' region_id=region_id %}"
data-timeline-load-state="idle"
```

В обоих окнах оставить постоянный `[data-timeline-year-filter-form]`, скрытый `[data-timeline-year-filter-container]`, `[data-timeline-year-controls]`, reset input, `[data-timeline-scroll-container]`, `[data-timeline-loading]`, скрытые `[data-timeline-error]` с кнопкой `[data-timeline-retry]`, `[data-timeline-empty]` и `<ul data-timeline-items hidden>`. Тексты empty сохраняются разными для общей и региональной хронологии.

- [ ] **Step 5: Запустить view-тесты после каждого изменения Python и шаблонов**

Run:

```bash
poetry run pytest city/tests/integration/views/list/test_content.py region/tests/integration/test_views.py -q
```

Expected: PASS.

---

### Task 5: Lazy Fetch, Safe Rendering, Cache and Retry

**Files:**
- Modify: `frontend/js/entries/timeline_modal.test.js`
- Modify: `frontend/js/entries/timeline_modal.js`

**Interfaces:**
- Consumes: `dialog.dataset.timelineUrl`, JSON `{items, years}`, постоянные data hooks из Task 4.
- Produces: состояния `idle`, `loading`, `loaded`, `error` в `data-timeline-load-state`.
- Preserves: модальные окна без `data-timeline-url`, существующие year-filter/reset/scroll hooks.

- [ ] **Step 1: Добавить падающие тесты запуска запроса**

Добавить `afterEach(() => vi.unstubAllGlobals())`, создать lazy-modal fixture и mock:

```javascript
const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    json: vi.fn().mockResolvedValue({ items: [], years: [] }),
});
vi.stubGlobal('fetch', fetchMock);

await loadTimelineModal();
expect(fetchMock).not.toHaveBeenCalled();

document.querySelector('[data-timeline-modal-trigger]').click();
expect(modal.showModal).toHaveBeenCalledOnce();
expect(fetchMock).toHaveBeenCalledOnce();
expect(fetchMock).toHaveBeenCalledWith('/api/city/timeline?country=RU');
```

Добавить deferred response и проверить, что два клика в `loading` не создают второй запрос, а повторное открытие после `loaded` также оставляет один вызов.

- [ ] **Step 2: Запустить frontend-тест и подтвердить падение из-за отсутствия fetch**

Run from `frontend/`:

```bash
npm test -- js/entries/timeline_modal.test.js
```

Expected: FAIL на `fetchMock` call count.

- [ ] **Step 3: Реализовать состояния и загрузку минимально до зелёного запуска**

Добавить `loadTimeline(modal)`:

```javascript
async function loadTimeline(modal) {
    const url = modal.dataset.timelineUrl;
    const state = modal.dataset.timelineLoadState;
    if (!url || state === 'loading' || state === 'loaded') return;

    modal.dataset.timelineLoadState = 'loading';
    showState(modal, 'loading');
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`Timeline request failed: ${response.status}`);
        const payload = await response.json();
        validateTimelinePayload(payload);
        renderTimeline(modal, payload);
        modal.dataset.timelineLoadState = 'loaded';
    } catch {
        modal.dataset.timelineLoadState = 'error';
        showState(modal, 'error');
    }
}
```

Trigger сначала вызывает `showModal()`, затем `loadTimeline(modal)`. Для dialog без URL остаётся только прежняя прокрутка.

- [ ] **Step 4: Добавить падающие тесты рендеринга и безопасности**

Успешный payload должен создать years/items/marker и сохранить текст:

```javascript
expect(document.querySelector('[data-timeline-year-filter="2024"]')).not.toBeNull();
expect(document.querySelectorAll('[data-timeline-item]')).toHaveLength(2);
expect(document.querySelector('[data-timeline-first-visited]').textContent).toContain('Казань');
```

Для `city_title: '<img src=x onerror=alert(1)>'` проверить:

```javascript
expect(document.querySelector('[data-timeline-items] img')).toBeNull();
expect(document.querySelector('[data-timeline-item]').textContent).toContain(
    '<img src=x onerror=alert(1)>'
);
```

Также добавить empty success, non-OK, rejected fetch, malformed payload, retry после ошибки и отсутствие fetch у server-rendered collection modal.

- [ ] **Step 5: Запустить тесты и подтвердить падение на отсутствующем renderer/retry**

Run from `frontend/`:

```bash
npm test -- js/entries/timeline_modal.test.js
```

Expected: FAIL на отсутствии сгенерированных элементов или повторного запроса.

- [ ] **Step 6: Реализовать безопасный renderer, empty/error и retry**

`validateTimelinePayload` принимает только объект с массивами `items` и `years`. `renderTimeline` очищает controls/items через `replaceChildren`, создаёт элементы `document.createElement`, задаёт API-значения через `textContent`, `value`, `dataset` и `toggleAttribute`, затем показывает empty либо list и year container.

Status classes выбираются только по `item.status === 'visited'`; произвольные строки из API не становятся class names. Постоянная retry-кнопка вызывает `loadTimeline(modal)`, когда state равен `error`. Успешный пустой ответ выставляет `loaded` и не запрашивается повторно.

- [ ] **Step 7: Адаптировать прежние тесты фильтрации к асинхронно созданным элементам**

После открытия ждать через `await vi.waitFor(...)`, затем сохранить проверки одного/нескольких годов, reset и прокрутки. Добавить отдельный тест server-rendered modal без URL, подтверждающий прежнюю фильтрацию и нулевое число fetch-вызовов.

- [ ] **Step 8: Запустить frontend-тест после каждого изменения JavaScript**

Run from `frontend/`:

```bash
npm test -- js/entries/timeline_modal.test.js
```

Expected: PASS без unhandled promise rejections.

---

### Task 6: Full Verification

**Files:**
- Verify all files changed in Tasks 1-5.
- Modify only files implicated by a failing verification; add a regression test before each behavioral correction.

**Interfaces:**
- Consumes: completed service, APIs, templates and JavaScript.
- Produces: passing backend/frontend suites, clean build and clean static checks.

- [ ] **Step 1: Запустить все затронутые backend-тесты одним процессом**

```bash
poetry run pytest city/tests/integration/services/test_timeline.py city/tests/integration/api/test_city_timeline.py region/tests/integration/test_city_timeline_api.py city/tests/integration/views/list/test_content.py region/tests/integration/test_views.py -q
```

Expected: PASS.

- [ ] **Step 2: Запустить регрессию приложений city и region**

```bash
poetry run pytest city/tests region/tests -q
```

Expected: PASS.

- [ ] **Step 3: Запустить полный frontend test suite**

Run from `frontend/`:

```bash
npm test
```

Expected: PASS.

- [ ] **Step 4: Собрать frontend assets**

Run from `frontend/`:

```bash
npm run build
```

Expected: exit code 0 без build errors.

- [ ] **Step 5: Запустить Python static checks изменённых модулей**

```bash
poetry run ruff check city/services/timeline.py city/api/timeline.py city/api/__init__.py city/urls/api.py city/views.py region/api.py region/urls/api.py region/views.py city/tests/integration/services/test_timeline.py city/tests/integration/api/test_city_timeline.py region/tests/integration/test_city_timeline_api.py city/tests/integration/views/list/test_content.py region/tests/integration/test_views.py
poetry run mypy city/services/timeline.py city/api/timeline.py region/api.py
```

Expected: обе команды завершаются без ошибок.

- [ ] **Step 6: Запустить pre-commit для всех изменённых файлов**

```bash
poetry run pre-commit run --files city/services/timeline.py city/api/timeline.py city/api/__init__.py city/urls/api.py city/views.py region/api.py region/urls/api.py region/views.py templates/city/list/toolbar.html templates/region/selected/list/toolbar.html frontend/js/entries/timeline_modal.js frontend/js/entries/timeline_modal.test.js city/tests/integration/services/test_timeline.py city/tests/integration/api/test_city_timeline.py region/tests/integration/test_city_timeline_api.py city/tests/integration/views/list/test_content.py region/tests/integration/test_views.py docs/superpowers/specs/2026-07-14-city-timeline-lazy-loading-design.md docs/superpowers/plans/2026-07-14-city-timeline-lazy-loading.md
```

Expected: все hooks Passed. Если formatter изменил файлы, повторить соответствующие тесты и эту команду.

- [ ] **Step 7: Проверить итоговый diff и отсутствие случайных изменений**

```bash
git status --short
```

Expected: только файлы задачи, нет whitespace errors, коммит не создан.
