<!-- ---------------------------------------------
--
-- Copyright © Egor Vavilov (Shecspi)
-- Licensed under the Apache License, Version 2.0
--
-- ---------------------------------------------- -->

## Context

See `proposal.md` for motivation and
`specs/visited-city-surface-synchronization/spec.md` for the behavioural
contract. The shared modal already emits `city-added`, `visited-city-created`
and `visited-city-updated`; list pages replace a complete server fragment, but
the city detail page builds a second card representation in the browser.

The complete city-map payload identifies a country by its display name, while
the active map filter is a country code. This prevents a reliable decision on
whether the displayed country progress should change.

## Goals / Non-Goals

**Goals:**
- Give the city detail page one server-owned representation of a user's visits.
- Keep map state and progress accurate after a successful modal save.
- Preserve the current list-fragment and collection/region-map contracts.

**Non-Goals:**
- Redesign the modal, visit card, map visual language, or the global dashboard.
- Replace the existing public API or reload the whole browser page.
- Refactor unrelated city-list filters and pagination.
- Создать источник city polygon для города без региона; это выделено в GitHub
  issue #303.

## Decisions

### Detail visits use a dedicated complete server fragment

Expose an authenticated fragment endpoint for the `#user-visits` surface and
make its template self-contained, including empty state, visit actions and the
add button. On relevant create and update events, the detail entry point fetches
and atomically replaces the whole surface; it initializes new UI controls only
after replacement and preserves the prior surface on an invalid response.

This removes the duplicate client card renderer and guarantees the same order,
markup and action wiring as a browser reload. It is intentionally a dedicated
selector and entry point, rather than extending the list refresher's generic
selector, because a city-detail fragment has a different authorization, URL and
lifecycle contract.

Alternative considered: make the existing JavaScript card renderer match the
template and manually bind actions. Rejected because it would retain two
renderers whose date, Markdown, accessibility and future template changes can
diverge again.

### Detail-map state is event-driven and retained before initialization

The detail map entry point will keep the current visited state and references to
created marker and city polygon layers. It will subscribe to the shared save
events for its city, update the retained state immediately, and restyle existing
layers when the map is open. Map initialization reads that retained state, so a
save that occurs before the first opening is also reflected.

Alternative considered: destroy and recreate the map on every save. Rejected
because it repeats geometry requests and risks stale asynchronous map creation.

### Country identity is an additive event field

The create/update response and the modal's event city summary will carry the
city's stable country code in addition to its existing display name. The city
map compares this code with its selected-country filter before mutating the
country counter. The total counter changes only for a first visit; both affected
labels are derived from the new counter values rather than retaining server-time
word forms.

The additive field preserves the existing response contract for old clients.

### Existing surface handlers remain isolated

List pages continue to own fragment refresh through `city-added`. Region and
collection maps continue to update only when their marker collection contains
the event city. Detail-only event consumers verify the city id before fetching
or changing map layers. This avoids a sidebar-triggered save modifying a page's
unrelated region, collection or detail content.

## Risks / Trade-offs

- [Fragment request fails after a successful save] → Retain the old detail
  surface and show an explicit manual-refresh error, matching list behaviour.
- [A stale asynchronous map initialization completes after a save] → Apply the
  retained current visited state when each layer is created.
- [New country-code field is absent in a malformed response] → Do not mutate the
  selected-country counter; total progress can still use the first-visit flag.
- [Fragment replacement discards third-party UI state] → Destroy controls within
  the old root and initialize only the replacement root using the established
  UI lifecycle.

## Migration Plan

1. Deploy the additive API/event country code and detail fragment endpoint.
2. Deploy consumers that use the new field and fragment.
3. Rollback remains safe: older clients ignore the additive field and use their
   current rendering; the endpoint is additive and can remain deployed.
