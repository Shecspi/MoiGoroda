<!--
---------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
-->

## Context

The preselected-city flow currently transfers focus to the visit-date input as part of modal setup. The input focus opens the calendar through the existing focus handler, which is unnecessary before the user chooses a date. See `proposal.md` for motivation and the delta spec for the required visible behavior.

## Goals / Non-Goals

**Goals:**

- Direct native modal focus to the dialog when opening with a preselected city.
- Keep automatic focus on the city field for the city-selection flow.
- Retain manual date-input and shortcut interactions.

**Non-Goals:**

- Redesigning the date picker or replacing its calendar library.
- Changing visit submission, edit mode, or date validation.

## Decisions

### Direct native focus by modal flow

The modal controller will mark the native dialog as the autofocus target before opening it when a city is already selected. This prevents the browser from selecting the first form control while keeping focus within the modal. It will retain its existing city-input focus when no city is selected. The calendar continues to open only through the existing user-driven date input interaction.

Alternative: defer automatic date focus until the modal is visible. This is rejected because no automatic date focus is needed in the selected-city flow.

Alternative: focus immediately and force the calendar to recalculate its position. This is rejected because it still opens a date picker before the user requests it.

## Risks / Trade-offs

- [A refactor restores date focus in the selected-city flow] → cover the absence of focus and the closed calendar with a frontend regression test.
- [City selection loses its keyboard entry point] → cover automatic city-field focus when no city is selected.

## Migration Plan

1. Ship the focused frontend change with regression coverage.
2. No persisted data, API, or server-side migration is required.
3. Roll back by restoring the prior selected-city focus only if an accessibility regression is found.
