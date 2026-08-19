// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import {initCountrySelect} from "../components/initCountrySelect";

async function initializeRegionListPage() {
    await initCountrySelect({showAllOption: false});
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeRegionListPage, {once: true});
} else {
    initializeRegionListPage();
}

document.addEventListener('visited-city-list-refreshed', initializeRegionListPage);
