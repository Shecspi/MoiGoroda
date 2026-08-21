<!--
---------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
-->

## Why

When a city query in the add-city modal has no matches, the suggestion popup contains no feedback. Users cannot distinguish an empty result from a failed or inactive search.

## What Changes

- Show a clear, non-selectable empty-state message inside the city combobox result list when a completed city search has no matching cities.
- Preserve existing loading, selection, keyboard navigation, and location-filter behavior.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `add-city-modal`: City search suggestions report an empty result set as a disabled list item.

## Impact

- Affects the add-city modal city-combobox frontend component and its functional tests.
- Does not change backend APIs, persisted data, or external dependencies.
