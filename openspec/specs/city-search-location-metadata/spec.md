<!--
---------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
-->

# City Search Location Metadata Specification

## Purpose

Provides location-aware city search results so clients can synchronize selected city data with country and region controls.

## Requirements

### Requirement: Search result location identifiers
The city search endpoint SHALL include the selected city's country code and region code in every city result when those relations exist. The identifiers SHALL be stable values accepted by the location-filter interfaces.

#### Scenario: Search result has a country and region
- **WHEN** a city search returns a city associated with a country and region
- **THEN** that result includes the city's country code and region code in addition to its existing identity and display fields

#### Scenario: Search result has no region
- **WHEN** a city search returns a city associated with a country but no region
- **THEN** that result includes the country's code and represents the region code as absent
