<!--
---------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
-->

## Why

The add-city modal gives all form fields and its heading a persistent blue accent, which competes with the primary action and makes unfocused controls appear selected. The date shortcuts are visually detached from the date field, making a single date-selection task look like separate controls.

## What Changes

- Render the add-city modal heading with the standard content color instead of a primary blue accent.
- Render idle country, region, city, date, and impression fields with neutral borders while preserving their focus indication.
- Group the date input with the "Сегодня" and "Вчера" shortcuts into one compact control.
- Render both date shortcuts as neutral joined buttons while retaining their existing date-selection behavior.

## Capabilities

### New Capabilities
- `add-city-modal`: Visual and interaction requirements for the modal used to add a visited city.

### Modified Capabilities

None.

## Impact

- Affects `templates/components/add-city-modal.html` and its template-level regression tests.
- May update the modal's frontend test fixture to reflect the new date-control structure; date selection and calendar behavior remain unchanged.
- Uses the existing prefixed daisyUI v5 `dui-join` component and introduces no API, data model, or dependency changes.
