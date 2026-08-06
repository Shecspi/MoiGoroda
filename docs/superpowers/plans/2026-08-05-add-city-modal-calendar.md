<!--
---------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
-->

# Add-City Modal Calendar Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the add-city modal's manual date input and custom calendar with a readonly Vanilla Calendar Pro popup opened from the input and styled by daisyUI.

**Architecture:** `AddCityModal` will own one input-mode `Calendar` instance attached directly to its readonly date input. Its `onChangeToInput` callback will synchronize an ISO date to the readonly display input. The existing quick-date buttons will use one shared method that updates both input and calendar selection; the legacy picker stays untouched for the city creation page.

**Tech Stack:** Django templates, Vanilla JavaScript web component, Vanilla Calendar Pro, daisyUI 5, Vitest, pytest, Vite.

## Global Constraints

- Add `vanilla-calendar-pro` as a frontend dependency.
- Scope the replacement to the add-city modal; do not alter `frontend/js/components/visit_date_picker.js` or city creation page behavior.
- Configure a Russian, single-date calendar with daisyUI `vc` styling, `inputMode: true`, and `positionToInput: 'auto'`.
- Date input is readonly; displayed value is `DD.MM.YYYY`; submitted form value is ISO `YYYY-MM-DD`.
- Keep `Сегодня` and `Вчера` and synchronize them with the calendar selection.
- Do not commit without a direct user command.

---

### Task 11: Add Vanilla Calendar Pro dependency

**Files:**
- Modify: `frontend/package.json`
- Modify: `frontend/package-lock.json`

**Interfaces:**
- Produces: `Calendar` and stylesheet import from `vanilla-calendar-pro` for `frontend/components/add-city-modal/add-city-modal.js`.

- [ ] **Step 1: Add the package**

Run from `frontend/`:

```bash
npm install vanilla-calendar-pro
```

- [ ] **Step 2: Verify the dependency is locked**

Run:

```bash
npm ls vanilla-calendar-pro
```

Expected: one installed `vanilla-calendar-pro` version and exit code 0.

### Task 12: Replace the modal date picker UI and integration

**Files:**
- Modify: `templates/components/add-city-modal.html:35-51`
- Modify: `frontend/components/add-city-modal/add-city-modal.js:14-102,164-171,178-193`
- Test: `city/tests/unit/test_add_city_modal_template.py`
- Test: `frontend/components/add-city-modal/add-city-modal.test.js`

**Interfaces:**
- Consumes: `Calendar` from `vanilla-calendar-pro`; `isoFromParts` and `isoToRuDisplay` from `frontend/js/components/visit_date_picker.js`.
- Produces: `AddCityModal#setVisitDate(iso)` and `AddCityModal#clearVisitDate()` that keep the readonly input and `Calendar.selectedDates` synchronized.

- [ ] **Step 1: Write the failing Django-template test**

Add an assertion that the date input is readonly and a calendar mount exists:

```python
date_input = soup.find('input', {'id': 'date-of-visit'})
calendar = soup.find('div', {'id': 'add-city-visit-calendar'})

assert date_input is not None
assert date_input.has_attr('readonly')
assert calendar is not None
assert 'vc' in calendar.get('class', [])
```

- [ ] **Step 2: Run the Django test to verify it fails**

Run:

```bash
poetry run pytest city/tests/unit/test_add_city_modal_template.py -q
```

Expected: FAIL because the current text input is editable and no calendar mount exists.

- [ ] **Step 3: Write the failing frontend integration test**

Create `frontend/components/add-city-modal/add-city-modal.test.js`. Mock `Calendar`, mount the HTML template fixture and assert that selecting a date and invoking `setVisitDate('2026-08-05')` produce `05.08.2026` in `#date-of-visit` and `['2026-08-05']` in the calendar options/state.

```js
expect(dateInput.readOnly).toBe(true);
expect(calendarOptions.selectionDatesMode).toBe('single');
expect(calendarOptions.locale).toBe('ru-RU');
expect(dateInput.value).toBe('05.08.2026');
expect(calendar.selectedDates).toEqual(['2026-08-05']);
```

- [ ] **Step 4: Run the frontend test to verify it fails**

Run from `frontend/`:

```bash
npm test -- components/add-city-modal/add-city-modal.test.js
```

Expected: FAIL because `AddCityModal` currently instantiates the legacy picker and has no calendar instance or synchronization method.

- [ ] **Step 5: Change the template to make the input readonly and add calendar mount**

Replace the editable input attributes with a readonly display input and add the mounting element below the quick-date row:

```html
<input type="text"
       id="date-of-visit"
       name="date_of_visit"
       class="dui-input dui-input-bordered dui-input-primary flex-1"
       placeholder="Выберите дату"
       autocomplete="off"
       readonly>
<div id="add-city-visit-calendar" class="vc mt-3"></div>
```

- [ ] **Step 6: Replace legacy modal picker initialization with Vanilla Calendar Pro**

Import the library and stylesheet:

```js
import { Calendar } from 'vanilla-calendar-pro';
import 'vanilla-calendar-pro/styles/index.css';
```

Remove `clearVisitDateInput`, `initVisitDatePickers`, `setVisitDateInputValue`, and `valueFromInputToIso` imports. Store `this.visitCalendar`, initialize it using `{ locale: 'ru-RU', selectionDatesMode: 'single', enableDateToggle: false, onClickDate: (self) => this.setVisitDate(self.selectedDates[0] || '') }`, and call `init()`.

Define synchronization methods:

```js
setVisitDate(iso) {
    const value = iso || '';
    this.querySelector('#date-of-visit').value = value ? isoToRuDisplay(value) : '';
    this.visitCalendar.selectedDates = value ? [value] : [];
    this.visitCalendar.update({ dates: true, month: false, year: false });
}

clearVisitDate() {
    this.setVisitDate('');
}
```

Make quick-date handlers call `this.setVisitDate(isoFromParts(...))`, reset call `this.clearVisitDate()`, and submit read `this.visitCalendar.selectedDates[0] || ''` directly into `formData`.

- [ ] **Step 7: Run focused tests to verify they pass**

Run:

```bash
poetry run pytest city/tests/unit/test_add_city_modal_template.py -q
```

Expected: PASS.

Run from `frontend/`:

```bash
npm test -- components/add-city-modal/add-city-modal.test.js
```

Expected: PASS.

### Task 13: Verify production integration

**Files:**
- Modify only files from Tasks 11-12 if verification finds an integration defect.

**Interfaces:**
- Consumes: the readonly modal input, `AddCityModal` calendar synchronization and Vite bundle.
- Produces: a buildable modal calendar implementation with no legacy picker initialization.

- [ ] **Step 1: Run lint checks**

Run:

```bash
poetry run ruff check city/tests/unit/test_add_city_modal_template.py
```

Expected: `All checks passed!`

- [ ] **Step 2: Run the frontend test suite**

Run from `frontend/`:

```bash
npm test
```

Expected: all Vitest tests pass.

- [ ] **Step 3: Build frontend assets**

Run from `frontend/`:

```bash
npm run build
```

Expected: Vite build succeeds and emits an add-city-modal bundle that includes the calendar dependency.

- [ ] **Step 4: Manual browser verification**

Open the add-city modal and verify these scenarios:

```text
1. The date field cannot accept keyboard typing.
2. Selecting a calendar day renders DD.MM.YYYY in the field.
3. Today and Yesterday update the displayed date and selected calendar day.
4. Closing and reopening the modal clears both input and calendar selection.
5. Submitting sends YYYY-MM-DD as date_of_visit.
```

### Task 14: Restore Map Event Regression Test

**Files:**
- Modify: `frontend/js/entries/map_city.test.js:10-56,124-131`

**Interfaces:**
- Consumes: `map_city.js` document-level `city-added` listener and an event detail with `city.id`.
- Produces: a regression test that verifies map marker removal through the current event-based integration.

- [ ] **Step 1: Confirm the existing failure**

Run from `frontend/`:

```bash
npx vitest run js/entries/map_city.test.js
```

Expected: FAIL because the test reads a nonexistent `initAddCityForm` mock call.

- [ ] **Step 2: Replace stale callback expectation with the real event contract**

Remove the `initAddCityForm` mock and dispatch the event registered by `map_city.js`:

```js
document.dispatchEvent(new CustomEvent('city-added', {
    detail: {city: {id: 123, name: 'Город'}},
}));

expect(mocks.actions.removeNotVisitedMarker).toHaveBeenCalledWith(123);
```

- [ ] **Step 3: Run the focused test**

Run from `frontend/`:

```bash
npx vitest run js/entries/map_city.test.js
```

Expected: 2 tests pass.

- [ ] **Step 4: Run the full frontend suite**

Run from `frontend/`:

```bash
npm test
```

Expected: all Vitest tests pass.

## Self-Review

- Spec coverage: Task 11 installs the required library; Task 12 implements readonly single-date Russian calendar, ISO/display conversion, quick button synchronization, and reset; Task 13 verifies all requested behavior; Task 14 restores a stale test that blocks frontend verification.
- Placeholder scan: no TODO or unspecified implementation steps remain.
- Type consistency: `setVisitDate(iso)` and `clearVisitDate()` are the only new controller interfaces and are used consistently in initialization, quick buttons, reset, and submission.
