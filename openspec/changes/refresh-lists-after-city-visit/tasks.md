<!-- ---------------------------------------------
--
-- Copyright © Egor Vavilov (Shecspi)
-- Licensed under the Apache License, Version 2.0
--
-- ---------------------------------------------- -->

## 1. Shared Refresh Foundation

- [x] 1.1 Define a reusable refresh-container contract for list templates, including a stable selector and the fragment URL.
- [x] 1.2 Extract the city-list-only refresh behavior into a shared list-refresh entrypoint that does nothing when the active page has no refresh container.
- [x] 1.3 Preserve the current query string when requesting a fragment, atomically replace the validated container, and retain the prior DOM on any failed or incomplete response.
- [x] 1.4 Handle every successful visit creation, including repeat visits, while preserving exactly one success notification and existing map/detail-page event behavior.
- [x] 1.5 Add frontend unit tests for the shared success path, repeat visits, query-string preservation, and failed or incomplete fragment responses.
- [x] 1.6 Run the targeted frontend unit tests and present the foundation diff for approval before committing it.

## 2. Visited City List

- [x] 2.1 Apply the refresh-container contract to `/city/all/list` and retain its independently renderable fragment endpoint through `django-modern-rest` without introducing `django-rest-framework`.
- [x] 2.2 Migrate `/city/all/list` from page-specific refresh wiring to the shared entrypoint.
- [x] 2.3 Add or update Django integration tests for the city-list fragment, including filters, sorting, country, pagination, and template filters.
- [x] 2.4 Run targeted frontend and backend tests and present the city-list diff for approval before committing it.

## 3. Region Lists

- [x] 3.1 Add `django-modern-rest` fragment rendering and refresh-container support for `/region/<id>/list`, including status, progress, filters, pagination, and timeline data.
- [x] 3.2 Add `django-modern-rest` fragment rendering and refresh-container support for `/region/all/list`, including country-specific regional progress.
- [x] 3.3 Add Django integration tests for both region fragments and their query parameters.
- [x] 3.4 Run targeted tests and present the region-list diff for approval before committing it.

## 4. Thematic Collections

- [x] 4.1 Add `django-modern-rest` fragment rendering and refresh-container support for the thematic collection catalog at `/collection/`, including collection-card progress and previews.
- [x] 4.2 Add `django-modern-rest` fragment rendering and refresh-container support for `/collection/<id>/list`, including city status, filters, progress, pagination, and timeline data.
- [x] 4.3 Add Django integration tests for both thematic-collection fragments.
- [x] 4.4 Run targeted tests and present the thematic-collection diff for approval before committing it.

## 5. Personal Collections

- [x] 5.1 Add `django-modern-rest` fragment rendering and refresh-container support for the owner's personal collection catalog at `/collection/personal`.
- [x] 5.2 Add `django-modern-rest` fragment rendering and refresh-container support for `/collection/personal/<uuid>/list`, including collection membership, filters, progress, empty states, and pagination.
- [x] 5.3 Add Django integration tests for both personal-collection fragments and verify that the public personal-collection catalog remains outside the refresh contract.
- [x] 5.4 Run targeted tests and present the personal-collection diff for approval before committing it.

## 6. End-to-End Regression Verification

- [x] 6.1 Verify new and repeat visit creation across every supported list surface, including an active filter and an empty-state transition.
- [x] 6.2 Verify fragment error handling retains existing DOM and directs the user to manually refresh the page.
- [x] 6.3 Verify maps and city-detail visit history retain their existing local synchronization behavior.
- [x] 6.4 Run the full relevant backend/frontend test suites and required frontend build or static checks; present any resulting fixes for approval before committing them.
