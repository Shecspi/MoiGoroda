<!--
---------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
-->

## MODIFIED Requirements

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
