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
