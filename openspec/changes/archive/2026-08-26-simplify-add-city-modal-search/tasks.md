<!--
---------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
-->

## 1. Global City Search

- [x] 1.1 Add a failing `CityCombobox` behavior test for one-character trailing-debounce search, timer replacement, request cancellation, and loading cleanup; verify red with `npm test -- components/add-city-modal/city-combobox.test.js` from `frontend/`
- [x] 1.2 Implement the 300 ms global remote-search lifecycle and one-character threshold in `CityCombobox`; verify green with `npm test -- components/add-city-modal/city-combobox.test.js` from `frontend/`

## 2. Modal Selection Flow

- [x] 2.1 Add a failing `AddCityModal` behavior test proving selector mode renders no country/region controls, makes only an unfiltered city-search request, and invalidates a selected city after input changes; verify red with `npm test -- components/add-city-modal/add-city-modal.test.js` from `frontend/`
- [x] 2.2 Remove modal-only cascade markup, imports, synchronization, and local-collection wiring while preserving the shared standalone cascade; verify green with `npm test -- components/add-city-modal/add-city-modal.test.js` from `frontend/`

## 3. Predetermined City Summary

- [x] 3.1 Add failing modal behavior cases for `region, country`, country-only, and empty location summaries in predetermined create and edit modes; verify red with `npm test -- components/add-city-modal/add-city-modal.test.js` from `frontend/`
- [x] 3.2 Pass country metadata through every predetermined-city trigger and the edit response, compose the optional second summary line, and verify green with `npm test -- components/add-city-modal/add-city-modal.test.js` from `frontend/`
- [x] 3.3 Update the modal template contract checks for the single city field and location summary; verify with `poetry run pytest city/tests/unit/test_add_city_modal_template.py -q`

## 4. Verification

- [x] 4.1 Run the combined targeted frontend suite with `npm test -- components/add-city-modal/city-combobox.test.js components/add-city-modal/add-city-modal.test.js js/components/city_cascade_selector.test.js` from `frontend/`
- [x] 4.2 Validate planning artifacts with `openspec validate simplify-add-city-modal-search --strict`
- [x] 4.3 Build production frontend assets with `npm run build` from `frontend/`
- [x] 4.4 Inspect `git diff` from baseline `98f6b3db932a4b77f0cf47f703ba1a2361b42dcf` and confirm the public `/api/city/search` contract and standalone `CityCascadeSelector` remain unchanged
