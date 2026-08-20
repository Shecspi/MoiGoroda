<!--
---------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
-->

## Context

See `proposal.md` for motivation. The add-city modal is a light-DOM custom element whose template is supplied by Django and whose city field currently delegates remote search, keyboard navigation, ARIA attributes, and result rendering to `CityAutocomplete`. Country and region remain native selects controlled by `CityCascadeSelector`. The frontend is vanilla JavaScript bundled by Vite; daisyUI provides styles with the `dui-` prefix.

The city result list lives inside a native `<dialog>`. It must remain within that dialog's DOM subtree because the dialog traps focus and a portalled list would be inaccessible to keyboard navigation.

## Goals / Non-Goals

**Goals:**

- Use Zag.js as the single owner of the city field's combobox state, keyboard behavior, dismiss handling, and ARIA attributes.
- Use a preloaded local city collection after a region or country without regions is selected, while retaining remote search for an unbounded location.
- Keep the existing daisyUI visual language without adding a custom stylesheet for standard combobox states.
- Ensure opening, closing, and disconnecting the modal does not retain event listeners, machines, or in-flight searches.

**Non-Goals:**

- Migrating the legacy `frontend/ui-lib` comboboxes or altering their API.
- Replacing country and region native selects.
- Changing `/api/city/search`, its response schema, server-side search ranking, or the visited-city submission API.
- Introducing a reusable project-wide abstraction over Zag.js.

## Decisions

### Use the Zag vanilla adapter for one modal-scoped combobox

The implementation will add `@zag-js/combobox` and `@zag-js/vanilla`. A small modal-local controller will create a combobox machine on create-mode initialization, subscribe to its state, and apply its generated DOM properties to the existing light-DOM elements. It will destroy the machine when the selection form resets or the custom element disconnects.

The machine collection will contain city response objects. City `id` is the item value and `title` is the display string; option rendering retains region and country as secondary metadata.

Alternative considered: extend `frontend/ui-lib/components/combobox.js`. It already duplicates this behavior and is being retired, so extending it increases the surface being phased out. Alternative considered: use a framework adapter. The project has no matching framework runtime and the modal is a native web component.

### Use location-aware local and remote data sources outside the Zag machine

The cascade selector will optionally provide all cities for a newly selected region or country without regions. The combobox will retain this collection, open it on input click, and filter it locally as the user types. When no local location collection is available, it will retain the existing remote lifecycle: no request below three trimmed characters, an `AbortController` for every active search, and a monotonically current request identity. When location filters change, it will clear both the selected city and local collection before loading replacement data.

Alternative considered: always use remote search. This would fail the required immediate browsing of cities in a selected location. The local collection is limited to one selected region or country without regions rather than the full catalog.

### Render and CSS-position the list in the dialog, with daisyUI styles

The Django template will retain a `relative` city-field container. The result list and optional loading indicator will be direct descendants of it. The list uses a CSS anchor (`absolute top-full start-0`) rather than Zag/Floating UI positioning, because the daisyUI modal's transform creates a containing block that makes viewport coordinates incorrect. The input keeps `dui-input dui-input-bordered`; the list uses a one-column `flex flex-col` container plus existing semantic surface, border, radius, and shadow utilities. It does not use `dui-menu`, whose column-wrap behavior conflicts with a scrollable result list. Each option uses daisyUI-compatible styling and a state-dependent active treatment supplied during rendering.

Alternative considered: use a daisyUI dropdown. daisyUI supplies presentation but does not provide the required combobox keyboard, active-descendant, remote-collection, and dismissal state machine.

### Preserve selection as the only source of a city identifier

Typing, clearing, closing the list, or changing a location filter will leave the hidden `city` field empty. Only the combobox value-change callback writes a city identifier and updates the modal submit state. This preserves the existing rule that a rating alone cannot submit the form.

## Risks / Trade-offs

- [Zag DOM properties are re-applied as search results change] → Keep result nodes recreated only after the collection changes and bind current machine properties after each state transition.
- [The custom element is reconnected after removal from the DOM] → Centralize cleanup in the same reset/disconnect paths already used by the modal and cover reconnect behavior in tests.
- [A menu positioned outside a native dialog breaks focus trapping] → Do not use a portal; retain the positioned list in the dialog subtree.
- [Adding a headless dependency increases bundle size] → Import only combobox and vanilla packages in the add-city modal entry; no project-wide adapter or style package is introduced.
- [The user sees stale results during rapid changes] → Abort active requests, track request identity, and clear the collection before requesting replacement results.

## Migration Plan

1. Add the Zag packages to the frontend dependency manifests.
2. Replace the modal template's bespoke autocomplete hooks with the Zag-compatible DOM parts while retaining its daisyUI styling.
3. Replace `CityAutocomplete` initialization with the modal-local Zag controller and preserve the existing country/region callback contract.
4. Move behavioral coverage to the new controller and modal integration tests, then remove `CityAutocomplete` and its dedicated tests.
5. Build frontend assets and run affected Vitest and Django template tests.

Rollback is a revert of the frontend dependency and modal changes; the server API and stored data are unchanged.
