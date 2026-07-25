<!--
---------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
-->

# Timeline Request Timeout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Прерывать загрузку хронологии через 10 секунд, переводить модальное окно в состояние ошибки и разрешать Retry без перезагрузки страницы.

**Architecture:** `loadTimeline` создаёт отдельный `AbortController` и timeout для каждого запроса, передаёт signal в `fetch` и очищает timer в `finally`. Существующий `catch` остаётся единой точкой перехода сетевых ошибок и timeout в состояние `error`.

**Tech Stack:** JavaScript, Fetch API, AbortController, Vitest 2, happy-dom 20, Vite 5.

## Global Constraints

- Таймаут загрузки хронологии равен `10_000` миллисекунд.
- Timeout должен реально отменять сетевой запрос, а не только менять UI-состояние.
- После timeout Retry должен запускать новый независимый запрос.
- Машина состояний, UI-тексты и серверный API не меняются.
- Не создавать коммит без новой прямой команды пользователя.

---

### Task 1: Таймаут запроса хронологии

**Files:**
- Modify: `frontend/js/entries/timeline_modal.test.js:16-18,131-166,245-261`
- Modify: `frontend/js/entries/timeline_modal.js:8,167-186`

**Interfaces:**
- Consumes: глобальные `AbortController`, `fetch`, `setTimeout` и `clearTimeout`.
- Produces: вызов `fetch(url, { signal })`, автоматический переход `loading → error` через 10 секунд и рабочий переход Retry `error → loading → loaded`.

- [ ] **Step 1: Добавить regression-тест зависшего запроса**

В `afterEach` восстанавливать реальные таймеры:

```javascript
afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
});
```

Добавить тест после сценария недублирования запроса:

```javascript
it('прерывает зависший запрос и позволяет повторить загрузку', async () => {
    vi.useFakeTimers();
    const modal = createLazyTimelineModal();
    let firstSignal;
    const fetchMock = vi
        .fn()
        .mockImplementationOnce((_url, options = {}) => {
            firstSignal = options.signal;
            return new Promise((_resolve, reject) => {
                firstSignal?.addEventListener(
                    'abort',
                    () => reject(new DOMException('Aborted', 'AbortError')),
                    { once: true },
                );
            });
        })
        .mockResolvedValueOnce(successfulResponse({ items: [], years: [] }));
    vi.stubGlobal('fetch', fetchMock);
    await loadTimelineModal();

    document.querySelector('[data-timeline-modal-trigger]').click();
    expect(modal.dataset.timelineLoadState).toBe('loading');

    await vi.advanceTimersByTimeAsync(10_000);

    expect(modal.dataset.timelineLoadState).toBe('error');
    expect(firstSignal).toBeInstanceOf(AbortSignal);
    expect(firstSignal.aborted).toBe(true);
    expect(document.querySelector('[data-timeline-error]').hidden).toBe(false);

    vi.useRealTimers();
    document.querySelector('[data-timeline-retry]').click();
    await vi.waitFor(() => expect(modal.dataset.timelineLoadState).toBe('loaded'));
    expect(fetchMock).toHaveBeenCalledTimes(2);
});
```

- [ ] **Step 2: Запустить новый тест и подтвердить ожидаемый RED**

Run from `frontend/`: `npm test -- js/entries/timeline_modal.test.js -t "прерывает зависший запрос"`

Expected: тест падает, потому что первый `fetch` не получает `{ signal }` и состояние остаётся `loading`.

- [ ] **Step 3: Добавить AbortController и гарантированную очистку timeout**

В начало `timeline_modal.js` после лицензии добавить:

```javascript
const TIMELINE_REQUEST_TIMEOUT_MS = 10_000;
```

Изменить сетевую часть `loadTimeline`:

```javascript
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), TIMELINE_REQUEST_TIMEOUT_MS);

modal.dataset.timelineLoadState = 'loading';
showContentState(modal, 'loading');
try {
    const response = await fetch(url, { signal: controller.signal });
    if (!response.ok) throw new Error(`Timeline request failed: ${response.status}`);
    const payload = await response.json();
    validateTimelinePayload(payload);
    renderTimeline(modal, payload);
    modal.dataset.timelineLoadState = 'loaded';
    requestAnimationFrame(() => scrollToFirstVisibleVisitedItem(modal));
} catch {
    modal.dataset.timelineLoadState = 'error';
    showContentState(modal, 'error');
} finally {
    clearTimeout(timeoutId);
}
```

- [ ] **Step 4: Обновить существующее ожидание формы вызова fetch**

В тесте «запрашивает хронологию только при открытии и кэширует успешный ответ» заменить assertion на:

```javascript
expect(fetchMock).toHaveBeenCalledWith('/api/city/timeline?country=RU', {
    signal: expect.any(AbortSignal),
});
```

- [ ] **Step 5: Запустить новый тест и подтвердить GREEN**

Run from `frontend/`: `npm test -- js/entries/timeline_modal.test.js -t "прерывает зависший запрос"`

Expected: `1 passed`.

- [ ] **Step 6: Запустить весь тестовый файл хронологии**

Run from `frontend/`: `npm test -- js/entries/timeline_modal.test.js`

Expected: все тесты проходят без незавершённых timers и unhandled rejection.

- [ ] **Step 7: Проверить production-сборку frontend**

Run from `frontend/`: `npm run build`

Expected: Vite production build завершается с кодом `0`.

- [ ] **Step 8: Запустить точечный pre-commit**

Run: `poetry run pre-commit run --files frontend/js/entries/timeline_modal.js frontend/js/entries/timeline_modal.test.js`

Expected: все применимые hooks завершаются со статусом `Passed`. Если formatter изменит файлы, повторить тестовый файл и pre-commit.

- [ ] **Step 9: Проверить итоговый diff**

Run: `git diff --check && git diff -- frontend/js/entries/timeline_modal.js frontend/js/entries/timeline_modal.test.js`

Expected: whitespace-ошибок нет; diff содержит только timeout, передачу signal, очистку timer и regression-тест.
