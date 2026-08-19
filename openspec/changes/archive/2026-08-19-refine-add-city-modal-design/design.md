<!--
---------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
-->

## Context

The add-city modal is rendered by a Django template and initialized by an existing web component. Its date input and shortcut buttons already expose stable element IDs used by the component to set dates and control the inline calendar. See `proposal.md` and `specs/add-city-modal/spec.md` for the behavioral scope.

## Goals / Non-Goals

**Goals:**
- Remove persistent primary coloration from idle controls without changing focus behavior.
- Make the date input and quick-date shortcuts one visual control.
- Preserve existing DOM hooks and calendar behavior.

**Non-Goals:**
- Change the date format, calendar library, keyboard behavior, or date-selection rules.
- Alter the add-city submission API, city selection, rating, or other modal sections.
- Redesign date fields outside this modal.

## Decisions

### Use existing neutral daisyUI controls

The template will use the base prefixed daisyUI input, select, textarea, and button styles rather than their persistent `primary` or `accent` color variants. This gives controls neutral idle styling while relying on the component focus state for feedback.

Alternative considered: custom CSS overrides for the primary variants. This is rejected because the styling is local, base components already express the desired neutral state, and overrides would compete with theme behavior.

### Compose the date control with `dui-join`

The date input and both existing shortcut buttons will become `dui-join-item` elements inside one `dui-join` container. The input remains the calendar trigger, and the buttons retain their IDs so the current web-component event listeners continue to work unchanged.

Alternative considered: place the buttons as absolutely positioned elements inside the input wrapper. This is rejected because it risks reducing the date input's usable width and does not communicate three peer controls as clearly as a joined group.

## Risks / Trade-offs

- [The compact group has less input width on narrow screens] → Keep the existing responsive width utilities and verify the produced asset build.
- [Markup changes could accidentally move the calendar outside its positioning wrapper] → Keep the calendar within the current relative wrapper and run existing calendar interaction tests.
- [Template regression checks encode the old color variants] → Update the checks to cover the agreed neutral and joined-control contract.
