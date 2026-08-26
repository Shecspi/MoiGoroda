<!--
---------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
-->

## Context

See `proposal.md` for motivation. The modal currently combines `CityCombobox`
with `CityCascadeSelector`: location selection can switch the combobox from
remote search to a preloaded local collection and synchronizes filters after a
remote choice. The same cascade module is also used by the standalone visit
form, so only its modal integration can be removed.

The shared `/api/city/search` endpoint already accepts one-character queries,
returns region and country display metadata, ranks prefix matches first, and
limits responses to 50. Other consumers depend on its optional `country`
parameter, and its optional `region` parameter is part of the documented API.

## Goals / Non-Goals

**Goals:**
- Make the modal's city-selection path a single global remote combobox.
- Keep short city names discoverable without issuing a request for every
  keystroke.
- Supply complete location text to predetermined-city and edit summaries.
- Preserve selection validity, keyboard behavior, stale-request protection,
  loading behavior, and the public search contract.

**Non-Goals:**
- Change city-search matching, ranking, response shape, or result limit.
- Change the toolbar or personal-collection search experiences.
- Remove `CityCascadeSelector` from the standalone visit form.
- Make the city editable while editing an existing visit.
- Add pagination, an inline error state, or persistent location text below an
  interactively selected city input.

## Decisions

### Keep the public API and simplify only the modal adapter

The modal will stop creating location filters and will send only `query` to the
existing endpoint. The endpoint retains `country`, `region`, and `limit` because
they are an established integration contract and `country` is actively used by
the city-list toolbar.

Alternative considered: remove unused modal filtering from the endpoint. This
would break a current consumer and turn a focused UI change into an API
migration.

### Remove the modal cascade integration, not the shared module

The country and region markup, modal-specific cascade setup, local city
collection path, and location synchronization after selection will be removed.
The standalone visit form continues importing the shared cascade unchanged.

Alternative considered: hide the selects but retain synchronization. This keeps
unnecessary requests and hidden state capable of filtering a supposedly global
search.

### Debounce global searches at the combobox boundary

`CityCombobox` will accept one significant character and schedule a trailing
request 300 milliseconds after the latest input. A new input clears the timer
and aborts an active request. Empty trimmed input clears results, loading state,
and selection without scheduling a request. The loading indicator starts only
when the request is issued, not during the debounce interval. Destroying the
combobox clears both timer and request.

Alternative considered: retain a two- or three-character threshold. The working
catalog contains one city with a one-character title and thirteen with
two-character titles, so either threshold excludes valid exact-name searches.

### Preserve selection as a city identifier, not free text

Choosing an item records its ID. Any subsequent input event invalidates that ID
and disables form submission until the user selects another suggestion. No
read-only card or persistent location line replaces the interactive input after
selection.

Alternative considered: retain the previous ID while text changes. That can
display one city title while submitting another city.

### Normalize predetermined location text at modal entry points

Predetermined create triggers will provide the country name alongside the
existing city and region data. Edit mode will use the location returned by the
visit detail response. The modal will compose the summary location from
non-empty region and country names, joining both with `, `, using the country
alone when the region is absent, and hiding the line when both are unavailable.

Alternative considered: fetch city details whenever a predetermined modal opens.
Existing trigger contexts and edit responses already hold the needed relation,
so an additional request would add latency and failure modes.

## Risks / Trade-offs

- [One-character queries can match thousands of cities and require a sequential
  scan] → A 300 ms trailing debounce limits request frequency, prefix ranking
  keeps exact short titles first, and the existing response limit remains 50.
- [A trigger can omit the new country attribute] → Treat location parts as
  optional and hide an empty summary line while updating every known trigger.
- [Removing modal cascade tests can accidentally reduce coverage of the shared
  standalone cascade] → Retain the dedicated `city_cascade_selector` suite and
  replace only modal integration cases with global-search behavior tests.
- [A cleared or superseded request can leave stale loading UI] → Make timer,
  request, results, and loading cleanup part of the same query lifecycle and
  cover it through the public combobox seam.

## Migration Plan

1. Update behavior tests at the `CityCombobox` and `AddCityModal` public seams.
2. Replace modal cascade markup and wiring with the global combobox path.
3. Add country metadata to predetermined triggers and edit summary state.
4. Run targeted frontend and Django checks, strict OpenSpec validation, and the
   production frontend build.

Rollback restores the modal template, cascade wiring, and previous combobox
threshold together; no data or API migration is required.
