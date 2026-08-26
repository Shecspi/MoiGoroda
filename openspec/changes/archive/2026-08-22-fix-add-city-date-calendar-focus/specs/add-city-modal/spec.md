<!--
---------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
-->

## ADDED Requirements

### Requirement: Initial focus follows city selection state
When the add-city modal opens with a city already selected, the system SHALL NOT automatically focus a form field. The visit-date calendar SHALL remain closed until the user activates the visit-date field. When the modal opens without a selected city, the system SHALL automatically focus the city field.

#### Scenario: Modal opens with a preselected city
- **WHEN** a user opens the add-city modal for a city that is already selected
- **THEN** no form field receives automatic focus
- **AND THEN** the visit-date calendar remains closed

#### Scenario: User opens the date picker for a preselected city
- **WHEN** the user activates the visit-date field after the modal has opened with a preselected city
- **THEN** the calendar is displayed at its normal position relative to the date input

#### Scenario: Modal opens without a selected city
- **WHEN** a user opens the add-city modal without a selected city
- **THEN** the city field receives automatic focus
