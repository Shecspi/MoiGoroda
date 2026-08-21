<!--
---------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
-->

## Context

The add-city modal composes a location cascade with an accessible city combobox. The cascade currently propagates only from country and region to city candidates; the combobox returns a selected city to the modal, which stores only its identifier. See `proposal.md` for motivation and the delta specs for required behavior.

## Goals / Non-Goals

**Goals:**

- Synchronize country and region controls from a city selected in unfiltered search results.
- Preserve the existing invalidation rule for user-driven country or region changes.
- Keep in-flight location and city-search responses from restoring stale state.
- Support countries with no regions.

**Non-Goals:**

- Changing visit creation or edit-mode behavior.
- Changing the visible search ranking, minimum query length, or result limit.
- Replacing the existing cascade or combobox library.

## Decisions

### Add stable location identifiers to city-search items

The city-search response will carry country and region codes alongside its display names. These are the same code formats already used by the cascade's location-filter requests, avoiding a fragile lookup by localized names.

Alternative: infer the selected options from returned country and region names. This is rejected because names are not stable identifiers and can be duplicated or renamed.

### Give the cascade an explicit asynchronous location-selection operation

The cascade will expose one operation that accepts country and region codes, selects the country, loads its regions, then selects the region when applicable. It will preserve a supplied city selection through this programmatic synchronization.

Alternative: have the modal manipulate the select elements and duplicate cascade fetch sequencing. This is rejected because it would split request cancellation, option state, and stale-response protection across two owners.

### Distinguish programmatic synchronization from manual filter changes

The modal will keep the selected city's title in the combobox while location synchronization is pending, but will commit its hidden identifier only after synchronization completes. The combobox's filter update will accept an explicit preservation boundary for this programmatic transition, so that it replaces candidate collections without clearing the pending title. User-generated `change` events retain the current behavior of invalidating the city.

Alternative: restore the title only after each filter update. This is rejected because the input remains visibly empty until asynchronous work completes and therefore preserves the flicker.

## Risks / Trade-offs

- [A country or region response arrives after a new user action] → retain request ownership or version checks and ignore results that are no longer current.
- [A selected city has incomplete location relations] → treat missing region as a country-without-region selection and do not fabricate a region value.
- [API clients rely on an exact result shape] → extend the response additively and cover the new fields with endpoint integration tests.
- [Programmatic country selection triggers the existing city-clearing path] → make synchronization an explicit cascade operation with documented preservation semantics and test it separately from manual events.
- [A preservation boundary also keeps a city after a manual location change] → scope it to one programmatic synchronization token and retain the normal clearing path for user events.

## Migration Plan

1. Deploy the additive city-search fields and frontend support together.
2. Existing clients continue to read their current result fields; no data migration is required.
3. Roll back by reverting the frontend synchronization. The additional response fields remain backward compatible.
