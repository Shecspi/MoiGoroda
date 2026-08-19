<!--
---------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
-->

## Purpose

Defines a focused, visually coherent form for recording a visited city without changing the existing city and visit-date workflow.

## ADDED Requirements

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
