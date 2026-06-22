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
