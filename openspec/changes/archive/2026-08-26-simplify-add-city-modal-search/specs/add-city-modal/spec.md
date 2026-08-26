<!--
---------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
-->

## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: Neutral idle form appearance
The add-city modal SHALL render its title and unfocused city, date, and impression fields with the standard content and control colors. A field SHALL present its focus indication only while it is focused.

#### Scenario: Modal opens with no focused field
- **WHEN** a user opens the add-city modal and no form field is focused
- **THEN** the modal title and field borders use neutral colors rather than a persistent primary accent

#### Scenario: User focuses a form field
- **WHEN** a user focuses the city, date, or impression field
- **THEN** the focused field presents the control focus indication

## REMOVED Requirements

### Requirement: City selection uses an accessible combobox
**Reason**: The location-aware local/remote selection contract is replaced by a global server-side combobox contract that supports every valid city-title length.

**Migration**: Modal consumers use the new `City selection uses a global accessible combobox` requirement. Pointer, keyboard, dismissal, stale-result, and selected-ID safety behavior remains available under the replacement requirement.

### Requirement: City suggestions honour location filters
**Reason**: The modal no longer exposes country or region filters and always searches the global city catalogue.

**Migration**: Modal consumers select a city directly from global suggestions. The public city-search API retains its optional `country` and `region` parameters for non-modal consumers.
