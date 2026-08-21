<!--
---------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
-->

## MODIFIED Requirements

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
