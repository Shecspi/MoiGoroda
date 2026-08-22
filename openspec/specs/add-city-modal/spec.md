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
The add-city modal SHALL render its title and unfocused country, region, city, date, and impression fields with the standard content and control colors. A field SHALL present its focus indication only while it is focused.

#### Scenario: Modal opens with no focused field
- **WHEN** a user opens the add-city modal and no form field is focused
- **THEN** the modal title and field borders use neutral colors rather than a persistent primary accent

#### Scenario: User focuses a form field
- **WHEN** a user focuses a country, region, city, date, or impression field
- **THEN** the focused field presents the control focus indication

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

### Requirement: City selection uses an accessible combobox
When the add-city modal is opened without a predetermined city, the system SHALL provide the city field as an accessible combobox. It SHALL not expose the manually entered city text as the form's selected city.

#### Scenario: Remote suggestions open after a sufficient query
- **WHEN** a user has not selected a region or country without regions, enters at least three non-whitespace characters in the city field, and matching cities are returned
- **THEN** the suggestion list opens automatically and presents each matching city's title with available region and country metadata

#### Scenario: Remote search returns no matching cities
- **WHEN** a user has not selected a region or country without regions, enters at least three non-whitespace characters in the city field, and the completed remote search returns no matching cities
- **THEN** the open suggestion list displays a message that no cities were found as a non-selectable item

#### Scenario: A selected location preloads cities
- **WHEN** a user selects a region or a country that has no regions
- **THEN** the system loads that location's cities into the city combobox without requiring a text query

#### Scenario: User opens preloaded location cities
- **WHEN** a user clicks an empty city field after cities have been loaded for the selected region or country without regions
- **THEN** the suggestion list opens and presents the location's loaded cities

#### Scenario: User filters preloaded location cities
- **WHEN** a user enters text in the city field after cities have been loaded for the selected region or country without regions
- **THEN** the suggestion list filters the loaded cities locally without issuing a remote city-search request

#### Scenario: User selects a suggested city with a pointer
- **WHEN** a user selects a city suggestion with a pointer
- **THEN** the input displays that city's title, the form records its city identifier, and the suggestion list closes

#### Scenario: User selects a suggested city with a keyboard
- **WHEN** a user navigates the open suggestion list with arrow keys and confirms the active city with Enter
- **THEN** the system selects that city with the same result as pointer selection

#### Scenario: User dismisses the suggestion list
- **WHEN** a user presses Escape or interacts outside the city combobox
- **THEN** the suggestion list closes without selecting a city

### Requirement: City suggestions honour location filters
The city combobox SHALL use the cities preloaded for a selected region or country without regions. When no such local collection is available, it SHALL query remote suggestions using the currently selected region when one is selected; otherwise it SHALL use the currently selected country. A manual change to either location filter SHALL invalidate the selected city. Selecting a city suggestion SHALL synchronize the country and, when the selected city belongs to a region, the region filters with that city's location.

#### Scenario: User selects a city without a selected location
- **WHEN** a user selects a city suggestion while no country or region is selected
- **THEN** the modal selects the city's country and region before retaining the city as the selected form value

#### Scenario: Location synchronization keeps the selected city visible
- **WHEN** the modal is loading the country or region required by a selected city suggestion
- **THEN** the city field continuously displays the selected city's title without an intermediate empty value

#### Scenario: User selects a city in a country without regions
- **WHEN** a user selects a city suggestion whose country has no regions
- **THEN** the modal selects that country, leaves the disabled region field indicating that no regions exist, and retains the selected city

#### Scenario: User changes the country or region after selecting a city
- **WHEN** a user manually changes the country or region after selecting a city
- **THEN** the city field, its selected city identifier, and its visible suggestions are cleared before new suggestions can be selected

#### Scenario: A stale search completes after filters change
- **WHEN** a city search started for a previous country, region, or query completes after the active filters or query have changed
- **THEN** the stale search results are not displayed or selected

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
