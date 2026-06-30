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
