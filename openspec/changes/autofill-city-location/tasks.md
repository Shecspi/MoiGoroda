<!--
---------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
-->

## 1. Search location metadata

- [x] 1.1 Extend the city-search result schema and serialization with additive country and nullable region codes, and verify `poetry run pytest city/tests/integration/api/test_city_search.py` passes.
- [x] 1.2 Add endpoint scenarios for cities with and without a region, and verify those tests assert the returned location codes.

## 2. Cascade synchronization

- [x] 2.1 Add an asynchronous cascade operation that selects a country, loads its regions, and selects the requested region while preserving an in-progress city choice; verify focused `city_cascade_selector` Vitest tests pass.
- [x] 2.2 Ensure obsolete programmatic location requests cannot overwrite a newer selection, and verify a regression test covers superseded responses.

## 3. Modal behavior

- [x] 3.1 Connect combobox city selection to cascade synchronization and commit the city identifier only after its location is synchronized; verify focused `add-city-modal` Vitest tests pass.
- [x] 3.2 Retain manual country and region changes as city-invalidating actions, and verify the modal clears its city identifier, input, and suggestions in a regression test.
- [x] 3.3 Cover selection of a city in a country without regions and verify the country remains selected, the region remains unavailable, and the city stays selected.
- [x] 3.4 Preserve the selected city title while programmatic location synchronization refreshes combobox filters, and verify a regression test observes no intermediate empty input value.

## 4. Verification

- [x] 4.1 Run `poetry run pytest city/tests/integration/api/test_city_search.py` and verify the city-search API contract passes.
- [x] 4.2 Run `npm --prefix frontend test -- components/add-city-modal/add-city-modal.test.js components/add-city-modal/city-combobox.test.js js/components/city_cascade_selector.test.js` and verify modal, combobox, and cascade behavior passes.
- [x] 4.3 Re-run `npm --prefix frontend test -- components/add-city-modal/add-city-modal.test.js components/add-city-modal/city-combobox.test.js js/components/city_cascade_selector.test.js` and verify the no-flicker regression remains covered with the existing location scenarios.
