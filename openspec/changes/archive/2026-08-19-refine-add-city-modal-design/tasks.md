<!--
---------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
-->

## 1. Modal markup

- [x] 1.1 Replace persistent primary color modifiers on the add-city modal heading and idle text controls with neutral component styling that preserves focus feedback.
- [x] 1.2 Restructure the visit-date input and the existing "Сегодня" and "Вчера" buttons as one neutral joined control without changing their IDs or calendar placement.

## 2. Regression coverage

- [x] 2.1 Update the add-city modal template regression checks for neutral idle controls and the joined date-control structure.
- [x] 2.2 Run the existing add-city modal frontend tests to confirm date shortcuts and calendar interactions remain functional.

## 3. Verification

- [x] 3.1 Run the targeted Django template test module.
- [x] 3.2 Build the frontend assets with `npm run build` from `frontend/`.
