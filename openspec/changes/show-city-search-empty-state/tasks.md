<!--
---------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
-->

## 1. Empty Search Result Feedback

- [x] 1.1 Update the add-city modal city combobox so a completed remote search with no cities renders a clear disabled result-list message, and verify it is visible after an empty search response.
- [x] 1.2 Preserve the existing selectable-city, loading, keyboard-navigation, and location-filter paths, and verify the focused city combobox test suite passes.

## 2. Regression Coverage

- [x] 2.1 Add a frontend functional test for the empty remote city-search response that verifies the message is non-selectable and no city identifier is selected.
- [x] 2.2 Run the targeted Vitest city-combobox tests and the frontend build, verifying both complete without errors.
