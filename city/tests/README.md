# Структура тестов City

## 📁 Структура по пирамиде тестирования

```
city/tests/
├── unit/                      # 🟢 Быстрые (2.5s) - без БД, моки
│   ├── models/               # Тесты моделей без БД
│   ├── serializers/          # Тесты сериализаторов
│   ├── dto/                  # Тесты DTO
│   └── forms/                # Тесты форм
│
├── integration/               # 🟡 Средние (32s) - с БД, один компонент
│   ├── api/                  # API endpoints
│   ├── repository/           # Репозитории с БД
│   ├── views/                # Views с БД
│   │   ├── visited_city/    # CRUD операции
│   │   ├── list/            # Список городов
│   │   └── map/             # Карта
│   ├── signals/              # Django signals
│   └── forms/                # Формы с валидацией
│
├── e2e/                       # 🔴 Медленные (10s) - полные сценарии
│   ├── workflows/            # Сценарии использования
│   └── scenarios/            # Комплексные сценарии
│
└── slow/                      # ⏱️  Performance тесты
    └── performance/          # Тесты производительности
```

## 🚀 Запуск тестов

### Разработка (быстрые тесты):

```bash
# Только unit тесты (2.5 секунды)
poetry run pytest city/tests/unit/ -v

# Или через marker
poetry run pytest city/tests -m "unit" -v

# Unit + Integration (без медленных)
poetry run pytest city/tests -m "unit or (integration and not slow)" -v
```

### Перед коммитом (полная проверка):

```bash
# Все тесты city
poetry run pytest city/tests/ -v

# Или только не-slow
poetry run pytest city/tests -m "not slow" -v
```

### CI/CD (полное покрытие):

```bash
# Все тесты включая медленные
poetry run pytest city/tests/ -v
```

## 📊 Статистика

| Категория   | Кол-во   | Время    | Marker                     | Описание             |
| ----------- | -------- | -------- | -------------------------- | -------------------- |
| Unit        | 70       | ~2.5s    | `@pytest.mark.unit`        | Без БД, с моками     |
| Integration | 295      | ~32s     | `@pytest.mark.integration` | С БД, один компонент |
| E2E         | 56       | ~10s     | `@pytest.mark.e2e`         | Полные сценарии      |
| Slow        | 3        | ~0.8s    | `@pytest.mark.slow`        | Performance тесты    |
| **ИТОГО**   | **424+** | **~50s** | -                          | Полное покрытие      |

## 🎯 Примеры использования

### По типу тестов:

```bash
# Запустить только unit тесты
poetry run pytest -m unit

# Только integration
poetry run pytest -m integration

# Только e2e
poetry run pytest -m e2e

# Только slow
poetry run pytest -m slow
```

### По директориям:

```bash
# Только unit тесты
poetry run pytest city/tests/unit/

# Только integration API
poetry run pytest city/tests/integration/api/

# Только visited_city integration
poetry run pytest city/tests/integration/views/visited_city/

# Только e2e workflows
poetry run pytest city/tests/e2e/workflows/
```

### Комбинации:

```bash
# Быстрые тесты (unit + integration без slow)
poetry run pytest city/tests -m "not slow"

# Unit и e2e (без integration)
poetry run pytest city/tests -m "unit or e2e"

# Только visited_city все типы
poetry run pytest city/tests -k "visited_city"
```

## 🔍 Полезные опции

```bash
# Только первая ошибка
poetry run pytest -m unit --maxfail=1

# С покрытием кода
poetry run pytest -m integration --cov=city --cov-report=html

# Параллельный запуск (требует pytest-xdist)
poetry run pytest -m unit -n auto

# Показать самые медленные тесты
poetry run pytest -m integration --durations=10
```

## 📝 Конвенции

### Именование файлов:

-   `test_<component>.py` - основной тест компонента
-   `test_<feature>_<detail>.py` - детальные тесты фичи

### Классы тестов:

-   `TestComponentUnit` - unit тесты
-   `TestComponentIntegration` - integration тесты
-   `TestComponentE2E` - e2e сценарии

### Markers:

Всегда добавляйте соответствующий marker к классу или методу:

```python
@pytest.mark.unit
class TestSomethingUnit:
    def test_something(self):
        ...
```

## 🛠️ Поддержка

При добавлении новых тестов:

1. Определите тип теста (unit/integration/e2e)
2. Поместите в соответствующую папку
3. Добавьте правильный marker
4. Убедитесь что тесты проходят: `pytest path/to/test.py -v`
