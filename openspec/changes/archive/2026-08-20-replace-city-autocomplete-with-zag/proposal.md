<!--
---------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
-->

## Why

The city field in the add-city modal maintains a bespoke autocomplete implementation for combobox state, keyboard interaction, and accessibility. daisyUI supplies the visual language but no combobox behavior, so Zag.js will provide a maintained, accessible headless state machine while the modal retains its daisyUI appearance.

## What Changes

- Replace the add-city modal's `CityAutocomplete` implementation with a local Zag.js combobox integration.
- Preserve country and region selects as filters for the remote city search.
- Preload all cities after a region or a country without regions is selected, then filter that local collection in the combobox and open it on input click.
- Keep the three-character remote-search threshold, automatic result-list opening, result metadata, selection-to-city-id flow, and request cancellation behavior when no local location collection is available.
- Render the Zag.js combobox within the modal dialog and style its input, loading state, result list, and options with existing daisyUI and Tailwind classes.
- Remove the replaced bespoke autocomplete module and its tests after its behavior is covered by the Zag-based component tests.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `add-city-modal`: City selection in create mode uses an accessible remote combobox while retaining the established filtering and submission workflow.

## Impact

- Affected frontend: `frontend/components/add-city-modal/`, the city autocomplete module and its tests, and frontend dependency manifests.
- Adds `@zag-js/combobox` and the vanilla DOM adapter as frontend dependencies.
- Reuses `/api/city/search`; no backend API or persisted-data changes are required.
