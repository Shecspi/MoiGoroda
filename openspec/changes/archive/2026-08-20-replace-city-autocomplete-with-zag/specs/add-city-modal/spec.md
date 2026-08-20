<!--
---------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
-->

## ADDED Requirements

### Requirement: City selection uses an accessible combobox
When the add-city modal is opened without a predetermined city, the system SHALL provide the city field as an accessible combobox. It SHALL not expose the manually entered city text as the form's selected city.

#### Scenario: Remote suggestions open after a sufficient query
- **WHEN** a user has not selected a region or country without regions, enters at least three non-whitespace characters in the city field, and matching cities are returned
- **THEN** the suggestion list opens automatically and presents each matching city's title with available region and country metadata

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
The city combobox SHALL use the cities preloaded for a selected region or country without regions. When no such local collection is available, it SHALL query remote suggestions using the currently selected region when one is selected; otherwise it SHALL use the currently selected country. A change to either location filter SHALL invalidate the selected city.

#### Scenario: User changes the country or region after selecting a city
- **WHEN** a user changes the country or region after selecting a city
- **THEN** the city field, its selected city identifier, and its visible suggestions are cleared before new suggestions can be selected

#### Scenario: A stale search completes after filters change
- **WHEN** a city search started for a previous country, region, or query completes after the active filters or query have changed
- **THEN** the stale search results are not displayed or selected
