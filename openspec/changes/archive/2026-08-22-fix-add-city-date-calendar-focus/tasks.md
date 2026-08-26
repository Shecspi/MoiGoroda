<!--
---------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
-->

## 1. Initial Focus Behavior

- [x] 1.1 Remove automatic visit-date focus for the preselected-city flow and designate the dialog as its native autofocus target; verify a preselected-city modal opens with no focused form field and a closed calendar.
- [x] 1.2 Preserve automatic city-field focus when the modal opens without a selected city; verify the city-selection flow remains keyboard-ready.

## 2. Regression Coverage

- [x] 2.1 Update the add-city-modal frontend tests to simulate native dialog autofocus and assert that a preselected-city modal focuses the dialog rather than a form field, keeps the calendar closed, and retains manual date activation and city-selection autofocus; verify with `npm test -- components/add-city-modal/add-city-modal.test.js` from `frontend/`.
- [x] 2.2 Build frontend assets to validate the changed module and bundled styles; verify with `npm run build` from `frontend/`.
