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

## Контекст ошибок

- [2026-06-21] Проблема: тесты логирования `services.cache` проверяли `caplog.text`, но логгер настроен с `propagate=False` и сообщения не попадали в `caplog` → Решение: проверять вызовы `services.cache.logger.debug` через мок вместо `caplog`.
- [2026-06-21] Проблема: `services.cache` писал обычные DEBUG-логи через handler с formatter `detail_app`, который требует `IP` и `user`, поэтому на cache miss/set возникал `ValueError: Formatting field not found in record: 'IP'` → Решение: использовать для `services.cache` отдельный handler с formatter без request-полей.
