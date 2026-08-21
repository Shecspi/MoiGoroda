# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

# Правила проекта

## Лицензия в файлах

- Во все создаваемые и редактируемые файлы нужно добавлять информацию о лицензии:

```text
# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------
```

- Лицензионный блок должен быть обычным комментарием файла, а не docstring/module docstring.
- В Python-файлах размещайте лицензионный блок перед module docstring и импортами.

## Принятые продуктовые допущения

- [2026-06-21] Статистика `visited-cities/countries-coverage`: `rank` и `total_users_count` могут быть устаревшими до `CACHE_TTL_SECONDS` (сейчас 1 час). Это допустимо продуктово: данные используются как приблизительная статистика, а не как финансовый/соревновательный источник истины. Не считать это production blocker при ревью, если TTL остаётся разумным и поведение явно задокументировано в коде.

## Правила Git

- Никогда не делать коммиты без прямого указания пользователя.
- Коммиты разрешены только по явной команде "сделай коммит" или аналогичной.
- Просьба добавить файлы в индекс, подготовить изменения, проверить статус или завершить задачу не является разрешением на коммит.

## Документация `docs/superpowers/`

- `docs/superpowers/plans/` — implementation plans, `docs/superpowers/specs/` — design specs. Создаются skills (writing-plans, brainstorming).
- Коммитить plans/specs только для крупных фич (3+ задач, затрагивающие несколько модулей). Для тривиальных задач документы не создавать и не коммитить.
- После завершения фичи документ остаётся в репозитории как история архитектурных решений.

## Тестирование интерфейса

- Не создавать тесты, которые проверяют только внешний вид, тексты, CSS-классы или структуру HTML интерфейса, без отдельной прямой просьбы. Для UI-задач проверять шаблон статически, сборкой frontend-ассетов и существующими функциональными тестами.

## OpenSpec: TDD и review

- При выполнении OpenSpec change через `/opsx-apply` считать его artifacts источником требований: перед кодом назвать критерии успеха и проверки, которые подтвердят результат.
- При сообщении о баге сначала применять skill `diagnosing-bugs`, чтобы воспроизвести проблему и подтвердить её причину; затем планировать и исправлять её через OpenSpec.
- Для изменения наблюдаемого поведения, исправления регрессии, API, прав доступа, доменного инварианта, persistence или integration contract применять skill `tdd`: до первого теста согласовать публичный seam, затем работать вертикальными циклами `red -> green`.
- Если публичный seam или границы модуля для TDD неясны, до первого теста применять skill `codebase-design` и согласовывать интерфейс.
- Для механических изменений, текстов и визуальных стилей TDD не обязателен; следовать правилам тестирования интерфейса выше и выполнять релевантные проверки.
- До начала реализации зафиксировать текущий `HEAD` как baseline для review. После явного commit от пользователя, но до объявления change готовым или предложения архивировать его, применять skill `code-review` к diff от baseline и OpenSpec artifacts. Нерешённые findings исправлять, повторно проверять и review повторять от того же baseline.
- Если пользователь не просил commit, сообщать, что commit-based review pending; не создавать commit самостоятельно.

## Agent skills

### Issue tracker

Задачи и спецификации ведутся в GitHub Issues репозитория. См. `docs/agents/issue-tracker.md`.

### Triage labels

Используется стандартный словарь из пяти triage labels. См. `docs/agents/triage-labels.md`.

### Domain docs

Репозиторий использует single-context layout. См. `docs/agents/domain.md`.

## Контекст ошибок

- [2026-06-21] Проблема: тесты логирования `services.cache` проверяли `caplog.text`, но логгер настроен с `propagate=False` и сообщения не попадали в `caplog` → Решение: проверять вызовы `services.cache.logger.debug` через мок вместо `caplog`.
- [2026-06-21] Проблема: `services.cache` писал обычные DEBUG-логи через handler с formatter `detail_app`, который требует `IP` и `user`, поэтому на cache miss/set возникал `ValueError: Formatting field not found in record: 'IP'` → Решение: использовать для `services.cache` отдельный handler с formatter без request-полей.
- [2026-06-21] Проблема: после выделения `stats` cache alias тесты статистики продолжали проверять `django.core.cache.cache` (`default`) и не видели сохранённое значение → Решение: в тестах cache-aside статистики очищать и проверять `caches['stats']`.
- [2026-06-22] Проблема: dashboard overview endpoints брали `now_date` через `datetime.now(timezone.utc).date()`, а при `USE_TZ=False` Django создавал новые записи по локальной дате; после локальной полуночи и до UTC-полуночи свежие записи выпадали из графиков и тест `test_users_overview_last_6m_weekly_chart_has_non_zero_data` падал → Решение: использовать `django.utils.timezone.now().date()` в dashboard API, чтобы период строился в той же временной модели, что и поля моделей.
- [2026-06-22] Проблема: после удаления `account.views.access.logger_email` e2e-тесты продолжали патчить этот атрибут и падали с `AttributeError` до выполнения сценария → Решение: убрать patch-и удалённого логгера из e2e-тестов регистрации и связанных пользовательских сценариев.
- [2026-06-22] Проблема: параллельный запуск нескольких `pytest` процессов с Django DB в одном workspace может одновременно создавать одну test DB и падать с `ProgrammingError: relation ... already exists` → Решение: запускать Django DB тесты последовательно либо использовать корректную изоляцию/разные test DB для параллельных процессов.
- [2026-06-29] Проблема: после миграции на Tailwind 4 Preline variant `hs-overlay-backdrop-open:*` генерировался так, что классы на элементе `.hs-overlay-backdrop` срабатывали сразу, и backdrop фильтров на `/city/all/list` и `/region/*/list` отображался поверх страницы → Решение: для вручную управляемого offcanvas backdrop убрать `hs-overlay-backdrop-open:*` классы из шаблонов и оставлять только базовые `opacity-0 pointer-events-none`; открытие/закрытие уже делает `filter_city.js`/`filter_region.js` через `opacity-100 pointer-events-auto`.
- [2026-06-29] Проблема: в Django templates с наследованием `{% comment %}`-блок лицензии перед `{% extends %}` вызывает `TemplateSyntaxError: {% extends ... %} must be the first tag` → Решение: в наследуемых шаблонах оставлять `{% extends %}` первым tag, а лицензионный `{% comment %}` размещать сразу после него.
- [2026-06-29] Проблема: Vite 4 CSS minifier выдавал production build warning `A nested style rule cannot start with "button"` на nested CSS `button&` из Swiper 12 pagination CSS → Решение: обновить Vite до 5.4.x, использовать ESM-конфиг `vite.config.mjs` и явно задать `build.manifest: 'manifest.json'`, потому что в Vite 5 `manifest: true` по умолчанию пишет файл в `.vite/manifest.json`, а Django templatetag loader ожидает `static/js/manifest.json`.
- [2026-06-29] Проблема: после обновления Vite до 5 dev server стал обслуживать проект под configured base `/static/js/`, а Django `vite_asset`/`vite_css` в DEBUG продолжали генерировать URL без base (`http://localhost:5173/css/tailwind.css`, `http://localhost:5173/js/entries/...`) и браузер получал 404 → Решение: в dev-mode генерировать asset URL с префиксом `http://localhost:5173/static/js/` и покрыть это unit-тестами templatetag.
- [2026-06-30] Проблема: запуск `pytest` напрямую использовал системный Python 3.14 без зависимостей проекта и падал на импорте `django` → Решение: запускать backend tests через `poetry run pytest`, чтобы использовать Poetry-окружение проекта на Python 3.12 с установленными test dependencies.
- [2026-06-30] Проблема: после сужения `name-tests-test.exclude` до `create_db.py` pre-commit hook падал на существующих Django-style файлах `test_*.py`, если у hook не задан `args: [--django]` → Решение: держать `args: [--django]` у `name-tests-test` и не исключать `test_*.py` из проверки.
- [2026-07-02] Проблема: регрессионный тест Django-шаблона ожидал `&amp;` в Tailwind arbitrary variant class (`[&:not(.hidden)]:inline-flex`), но `response.content.decode()` сохраняет литеральный `&` в статическом class-атрибуте → Решение: в assertions по HTML-контенту сравнивать фактическую строку класса с литеральным `&`, если шаблон содержит его статически.
- [2026-07-02] Проблема: frontend-регрессионный тест для Tailwind display-конфликта искал любой `hidden ... inline-flex` в исходнике и ложно срабатывал на подстроку `hidden` внутри классов вроде `focus:outline-hidden` → Решение: проверять конкретные старые паттерны классов (`hidden py-2 px-4 inline-flex`, `hidden shrink-0 inline-flex`) или парсить class-атрибуты по токенам.
- [2026-06-24] Проблема: тесты `region-all-list` закрепляли наличие `visit_years` в контексте list-страницы, хотя поле используется только `region-all-map`; это заставляло сохранять дорогой `ARRAY_AGG` в SQL списка регионов → Решение: проверять `visit_years` только в тестах карты, а для списка добавить регрессионный тест на отсутствие `ARRAY_AGG`.
- [2026-06-24] Проблема: `region-all-list` для авторизованных пользователей считал `num_total`/`num_visited` через общий `LEFT JOIN Region -> City -> VisitedCity` с `GROUP BY`; PostgreSQL сортировал десятки тысяч строк до пагинации, и `EXPLAIN ANALYZE` на 300 регионах/30k городах показывал ~480 ms на основной queryset → Решение: для list-пути, где не нужны `ratio_visited` и `visit_years`, считать `num_total`/`num_visited` через indexed `Subquery`, оставив aggregate-путь для карты.
- [2026-06-26] Проблема: новый Django-шаблон с `{% extends %}` падал с `TemplateSyntaxError`, потому что лицензионный `{% comment %}` был размещён перед `{% extends %}` → Решение: в шаблонах с наследованием оставлять `{% extends %}` первым template tag, а лицензионный комментарий размещать сразу после него.
- [2026-06-27] Проблема: запуск системного `pytest` вне Poetry-окружения падал с `ModuleNotFoundError: No module named 'django'` → Решение: запускать Django-тесты через `poetry run pytest ...`.
- [2026-07-05] Проблема: CSS-only tooltip'ы DaisyUI (`dui-tooltip dui-tooltip-top`) центрируются над элементом через `inset-inline: 50%` + `translateX(-50%)`, из-за чего tooltip выходит за viewport, если элемент расположен у края экрана → Решение: для крайних элементов тулбара использовать `dui-tooltip-start` (левый край) и `dui-tooltip-end` (правый край) вместо центрирования; добавить CSS-правило `.dui-tooltip[data-tip]:before { max-width: min(20rem, calc(100vw - 2rem)); }` для ограничения ширины tooltip'а по viewport.
- [2026-07-09] Проблема: после перевода тулбара персональной коллекции на daisyUI обработчик копирования ссылки в `personal_collection_status.js` продолжал вызывать legacy `showSuccessToast`/`showDangerToast`, поэтому показывался старый toast → Решение: для действий копирования ссылки использовать `showDaisyToast` и покрывать это frontend unit-тестом.
- [2026-07-09] Проблема: `aria-current="true"` для read-only daisyUI рейтинга персональной коллекции вычислялся в Django-шаблоне через `floatformat`/`add`, но локализация превращала `5.0` в `5,0`, а `add:0.5` не давал надёжный float-порог → Решение: вычислять стабильное `current_rating_value` в Python-сервисе и сравнивать в шаблоне с нелокализованными значениями половинок.
- [2026-07-24] Проблема: lifecycle-тест `NotVisitedCityLayer.clear()` зависал, потому что после исправления полной очистки продолжал ожидать новый mounted batch у уже снятого с карты кластерного слоя → Решение: после `clear()` считать оба представления размонтированными; последующие `add()` до `show()` проверять как unmounted (`needsClustering`), а `chunkProgress` вызывать только после подтверждённого монтирования кластера.
- [2026-07-24] Проблема: при дополнении существующего implementation plan новые Tasks 5–7 пересеклись с номерами уже завершённых задач в SDD progress ledger → Решение: перед добавлением этапов сверять `.superpowers/sdd/progress.md` и продолжать нумерацию свободными номерами, чтобы не перезаписывать task briefs и не повторять завершённую работу.
- [2026-07-24] Проблема: первая команда проверки Vite manifest завершилась ошибкой из-за неверного quoting динамического jq-выражения → Решение: для известных ключей manifest использовать одинарно заключённый jq-фильтр с явными строковыми литералами и отдельно фиксировать успешную команду и её raw output в verification report.
- [2026-07-24] Проблема: `poetry install` в новом worktree падал с `SecretServiceNotAvailableException`, когда Poetry пытался обратиться к недоступному системному keyring → Решение: запускать установку с `PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring`.
- [2026-07-24] Проблема: в изолированном worktree отсутствует игнорируемый `MoiGoroda/.env`, а подмена PostgreSQL на SQLite ломает миграции с `AddIndexConcurrently`; загрузка `.env` через `source` также ненадёжна из-за shell-метасимволов в значениях → Решение: загружать исходный `.env` через Python API `dotenv.load_dotenv`, задавать уникальный `DATABASE_NAME` для изоляции test DB и запускать `pytest` через `os.execv`.
- [2026-07-25] Проблема: integration-тест настоящего Leaflet.markercluster падал с `Map has no maxZoom specified`, а отрицательный `chunkInterval` создавал бесконечную очередь пустых chunk и таймаут → Решение: для карты без tile layer явно задавать `maxZoom`, а для принудительного chunked batch использовать минимальный неотрицательный `chunkInterval: 0`.
- [2026-07-25] Проблема: попытка передать текстовый вывод `git log --oneline` в `git log --stdin` привела к интерпретации строки коммита как revision и ошибке `bad revision` → Решение: при просмотре истории выбранных путей передавать пути напрямую в одной команде `git log --oneline -- <paths>`.
