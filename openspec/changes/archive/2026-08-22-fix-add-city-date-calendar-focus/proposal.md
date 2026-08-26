<!--
---------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
-->

## Why

When the add-city modal is opened with a city already selected, the visit-date field receives focus before the modal is visible. This opens and positions the calendar against an unfinished modal layout, so it briefly appears early and offset from its input.

## What Changes

- Do not automatically focus a form field when the add-city modal opens with a preselected city.
- Keep the visit-date calendar closed until the user explicitly activates the date field.
- Retain automatic focus on the city field only when the modal opens without a selected city.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `add-city-modal`: Define initial focus and calendar visibility for selected-city and city-selection modal flows.

## Impact

- Affected frontend add-city modal opening and initial field focus coordination.
- Existing modal accessibility and visit-date picker behavior must remain intact.
