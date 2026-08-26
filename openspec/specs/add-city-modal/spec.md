<!--
---------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
-->

# Add City Modal Specification

## Purpose

Defines a focused, visually coherent form for recording a visited city without changing the existing city and visit-date workflow.

## Requirements

### Requirement: Neutral idle form appearance
The add-city modal SHALL render its title and unfocused city, date, and impression fields with the standard content and control colors. A field SHALL present its focus indication only while it is focused.

#### Scenario: Modal opens with no focused field
- **WHEN** a user opens the add-city modal and no form field is focused
- **THEN** the modal title and field borders use neutral colors rather than a persistent primary accent

#### Scenario: User focuses a form field
- **WHEN** a user focuses the city, date, or impression field
- **THEN** the focused field presents the control focus indication

### Requirement: Predetermined city summary identifies its location
When the modal is opened with a predetermined city or while editing an existing visit, the system SHALL display a read-only summary whose first line is the city title and whose second line contains the available region and country names separated by a comma.

#### Scenario: Predetermined city has a region and country
- **WHEN** the modal opens with a predetermined city that has both a region and a country
- **THEN** the summary displays the city title on the first line and `region, country` on the second line

#### Scenario: Predetermined city has no region
- **WHEN** the modal opens with a predetermined city that has a country but no region
- **THEN** the summary displays only the country on the second line

#### Scenario: Predetermined city has no location metadata
- **WHEN** the modal opens with a predetermined city whose region and country names are both unavailable
- **THEN** the summary omits the empty location line

### Requirement: City selection uses a global accessible combobox
When the add-city modal is opened without a predetermined city, the system SHALL provide the city field as an accessible editable combobox and SHALL NOT display country or region filter controls. The system SHALL not expose manually entered city text as the form's selected city.

#### Scenario: Remote suggestions open after one significant character
- **WHEN** a user enters at least one non-whitespace character in the city field, pauses input for 300 milliseconds, and matching cities are returned
- **THEN** the system issues a global city-search request containing only the trimmed query and opens a suggestion list that presents each matching city's title with available region and country metadata

#### Scenario: User continues typing during the debounce interval
- **WHEN** a user changes the city query again before 300 milliseconds have elapsed
- **THEN** the pending search is replaced and no request is issued for the superseded query

#### Scenario: User clears the city query
- **WHEN** the city field is empty or contains only whitespace
- **THEN** the system does not issue a city-search request and closes the suggestion list

#### Scenario: Remote search returns no matching cities
- **WHEN** a completed global search returns no matching cities
- **THEN** the open suggestion list displays `Города не найдены` as a non-selectable item

#### Scenario: Remote search is in progress
- **WHEN** the debounce interval has elapsed and the city-search request has been issued but not completed
- **THEN** the system displays the loading indicator without preventing further input

#### Scenario: Remote search fails
- **WHEN** the active city-search request fails because of an HTTP or network error
- **THEN** the suggestion list closes and the system displays `Не удалось найти город. Попробуйте ещё раз.`

#### Scenario: User selects a suggested city with a pointer
- **WHEN** a user selects a city suggestion with a pointer
- **THEN** the editable input displays that city's title, the form records its city identifier, and the suggestion list closes

#### Scenario: User selects a suggested city with a keyboard
- **WHEN** a user navigates the open suggestion list with arrow keys and confirms the active city with Enter
- **THEN** the system selects that city with the same result as pointer selection

#### Scenario: User edits a selected city title
- **WHEN** a user changes the city input after selecting a suggestion
- **THEN** the form clears the selected city identifier and prevents submission until another suggestion is selected

#### Scenario: User dismisses the suggestion list
- **WHEN** a user presses Escape or interacts outside the city combobox
- **THEN** the suggestion list closes without selecting a city

#### Scenario: A stale search completes after the query changes
- **WHEN** a city search for a previous query completes after the active query has changed
- **THEN** the stale search results are not displayed or selected

### Requirement: Unified date shortcuts
The add-city modal SHALL present the visit-date field and the "Сегодня" and "Вчера" shortcuts as one joined date control. Both shortcuts SHALL use the same neutral visual treatment.

#### Scenario: User views the date control
- **WHEN** a user opens the add-city modal
- **THEN** the date input, "Сегодня", and "Вчера" appear as adjacent parts of one control group

### Requirement: Date shortcut behavior remains available
The add-city modal SHALL retain the existing visit-date interactions after the controls are visually joined.

#### Scenario: User selects today's date
- **WHEN** a user activates "Сегодня"
- **THEN** the visit-date field receives today's date and the calendar is closed

#### Scenario: User selects yesterday's date
- **WHEN** a user activates "Вчера"
- **THEN** the visit-date field receives yesterday's date and the calendar is closed

#### Scenario: User opens the date picker
- **WHEN** a user activates the visit-date field
- **THEN** the calendar is displayed for selecting a date

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
