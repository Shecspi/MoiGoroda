<!--
---------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
-->

# Vanilla Calendar Pro In Add-City Modal

## Goal

Replace the modal's custom visit-date picker with Vanilla Calendar Pro styled by daisyUI's `vc` calendar class. The date field must be selectable only through the calendar or the quick-date buttons.

## Scope

- Add the `vanilla-calendar-pro` frontend dependency.
- Change only the add-city modal date field and its JavaScript controller.
- Leave the city creation page and its existing date picker unchanged.

## Behavior

- The date input is `readonly` and opens a single-date Vanilla Calendar Pro popup only when clicked or focused.
- The picker uses the Russian locale, daisyUI `vc` styling, `inputMode: true`, and automatic positioning relative to the input.
- Selecting a day writes an ISO `YYYY-MM-DD` value to the submitted form data.
- The field displays the selected date as `DD.MM.YYYY`.
- `Сегодня` and `Вчера` set both the input value and the calendar selection.
- Resetting or closing the modal clears the input and calendar selection.

## Verification

- Unit tests cover the readonly input, the required calendar setup and synchronization contract for quick-date buttons.
- Frontend unit tests cover the controller's calendar integration.
- Run the focused Python and frontend tests, linting, and `npm run build`.
