<!--
---------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
-->

## 1. Dependencies and Markup

- [x] 1.1 Add the pinned compatible `@zag-js/combobox` and `@zag-js/vanilla` dependencies to the frontend manifests.
- [x] 1.2 Replace the city autocomplete template hooks with the DOM parts required by the Zag combobox, retaining daisyUI input, loading, list, and option styling inside the modal dialog.

## 2. Zag City Combobox

- [x] 2.1 Implement a modal-local Zag combobox controller that creates and destroys the vanilla machine, binds generated DOM properties, and selects city response objects by identifier.
- [x] 2.2 Implement remote search with a three-character trimmed threshold, automatic opening for non-empty current results, loading state, and city title/region/country result rendering.
- [x] 2.3 Preserve country and region filtering, clearing the selected city and collection on filter changes, and protect the UI from aborted or stale request results.
- [x] 2.4 Integrate the controller into create-mode setup, form reset, and custom-element disconnect paths without changing predetermined-city and edit-mode behavior.
- [x] 2.5 Preload selected region and country-without-regions cities, then support local filtering and click-to-open behavior in the city combobox.

## 3. Behavioral Coverage and Cleanup

- [x] 3.1 Add focused Vitest coverage for pointer and keyboard selection, automatic opening, Escape/outside dismissal, selected-city form state, and controller cleanup.
- [x] 3.2 Add regression coverage for country/region filters, request cancellation, and ignored stale responses in the Zag-based flow.
- [x] 3.3 Update add-city modal integration tests for the new combobox contract and remove `CityAutocomplete` with its superseded dedicated tests.
- [x] 3.4 Cover location-city preloading, local filtering, and the fallback remote-search mode.

## 4. Verification

- [x] 4.1 Run the affected Vitest suites from `frontend/`.
- [x] 4.2 Run the affected Django add-city modal template tests with `poetry run pytest`.
- [x] 4.3 Run `npm run build` from `frontend/` and verify the add-city modal entry builds successfully.
