<!--
---------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
-->

# Country-Filtered City Timeline Labels Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Сделать надписи хронологии списка городов однозначными при фильтрации по стране, не меняя поведение API.

**Architecture:** Django-шаблон использует уже доступные `country_code`, `country_name` и фильтр `prepositional`, чтобы условно выводить три странозависимые надписи. Integration-тест страницы фиксирует тексты как с фильтром `country=RU`, так и без него.

**Tech Stack:** Django templates, pytest, pytest-django, Tailwind CSS 4, Vite 5.

## Global Constraints

- При выбранной стране использовать её название во всех трёх связанных надписях.
- Без фильтра страны сохранить текущие надписи без изменений.
- Не менять заголовок модального окна, API-контракт или фильтрацию данных.
- Не создавать коммит без прямой команды пользователя.

---

### Task 1: Контекстные надписи хронологии

**Files:**
- Modify: `city/tests/integration/views/list/test_content.py:134-176`
- Modify: `templates/city/list/toolbar.html:76-79,109-147`

**Interfaces:**
- Consumes: шаблонные переменные `country_code: str | None`, `country_name: str` и фильтр `prepositional` из `region.templatetags.morphology`.
- Produces: странозависимые HTML-тексты без изменения URL или структуры ответа API.

- [ ] **Step 1: Добавить падающие assertions для обеих веток шаблона**

В `test_initial_page_context_has_no_timeline_data` после получения `content` добавить проверки текущих общих текстов:

```python
assert 'title="Показать хронологию посещения городов"' in content
assert '>Все сохранённые посещения</p>' in content
assert '>У Вас пока нет посещённых городов в хронологии.</span>' in content
```

В `test_timeline_url_includes_selected_country` сохранить декодированный ответ в `content` и добавить проверки согласованных текстов:

```python
content = response.content.decode()
assert 'data-timeline-url="/api/city/timeline?country=RU"' in content
assert 'title="Показать хронологию посещений в России"' in content
assert '>Все сохранённые посещения в России</p>' in content
assert '>В России пока нет посещённых городов в хронологии.</span>' in content
```

- [ ] **Step 2: Запустить тест и подтвердить ожидаемое падение странозависимой ветки**

Run: `poetry run pytest city/tests/integration/views/list/test_content.py::TestCityTimeline -q`

Expected: `test_timeline_url_includes_selected_country` падает на первой новой странозависимой надписи; тест без страны проходит.

- [ ] **Step 3: Условно вывести три надписи в шаблоне**

В кнопке хронологии заменить `title` на:

```django
title="{% if country_code %}Показать хронологию посещений в {{ country_name|prepositional }}{% else %}Показать хронологию посещения городов{% endif %}"
```

Под заголовком модального окна заменить подпись на:

```django
<p class="mt-1 text-sm text-base-content/60">{% if country_code %}Все сохранённые посещения в {{ country_name|prepositional }}{% else %}Все сохранённые посещения{% endif %}</p>
```

В пустом состоянии заменить текст на:

```django
<span>{% if country_code %}В {{ country_name|prepositional }} пока нет посещённых городов в хронологии.{% else %}У Вас пока нет посещённых городов в хронологии.{% endif %}</span>
```

- [ ] **Step 4: Запустить точечный тест и подтвердить исправление**

Run: `poetry run pytest city/tests/integration/views/list/test_content.py::TestCityTimeline -q`

Expected: `2 passed`.

- [ ] **Step 5: Запустить все integration-тесты list-view**

Run: `poetry run pytest city/tests/integration/views/list -q`

Expected: все тесты проходят.

- [ ] **Step 6: Проверить production-сборку frontend**

Run from `frontend/`: `npm run build`

Expected: Vite production build завершается с кодом `0` без ошибок.

- [ ] **Step 7: Запустить все project hooks**

Run: `poetry run pre-commit run --all-files`

Expected: все hooks завершаются со статусом `Passed`; если formatter изменит файл, повторить точечные тесты и весь pre-commit до зелёного результата.

- [ ] **Step 8: Проверить итоговый diff**

Run: `git diff --check && git diff -- templates/city/list/toolbar.html city/tests/integration/views/list/test_content.py docs/superpowers/specs/2026-07-15-country-filtered-city-timeline-labels-design.md docs/superpowers/plans/2026-07-15-country-filtered-city-timeline-labels.md`

Expected: `git diff --check` не выводит ошибок; diff содержит только согласованные надписи, тесты и документацию без изменений API.
