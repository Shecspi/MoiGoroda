// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

function initializeRegionFilters() {
    const openBtn = document.getElementById('btnOpenFilterSortPanel');
    const offcanvas = document.getElementById('offcanvasRight');
    const backdrop = document.querySelector('[data-hs-overlay-backdrop="#offcanvasRight"]');
    const closeBtn = offcanvas?.querySelector('[data-hs-overlay="#offcanvasRight"]');
    const resetBtn = document.getElementById('resetFilters');
    const applyBtn = document.getElementById('applyFilters');

    function openOffcanvas() {
        if (!offcanvas || !backdrop) {
            return;
        }

        offcanvas.classList.replace('translate-x-full', 'translate-x-0');
        backdrop.classList.replace('opacity-0', 'opacity-100');
        backdrop.classList.replace('pointer-events-none', 'pointer-events-auto');
        document.body.style.overflow = 'hidden';
    }

    function closeOffcanvas() {
        if (!offcanvas || !backdrop) {
            return;
        }

        offcanvas.classList.replace('translate-x-0', 'translate-x-full');
        backdrop.classList.replace('opacity-100', 'opacity-0');
        backdrop.classList.replace('pointer-events-auto', 'pointer-events-none');
        document.body.style.overflow = '';
    }

    openBtn?.addEventListener('click', (event) => {
        event.preventDefault();
        openOffcanvas();
    });
    closeBtn?.addEventListener('click', (event) => {
        event.preventDefault();
        closeOffcanvas();
    });
    backdrop?.addEventListener('click', closeOffcanvas);

    resetBtn?.addEventListener('click', function () {
        const filterInput = document.querySelector(`input[name="filter"][value="${this.dataset.filter}"]`);
        const sortInput = document.querySelector(`input[name="sort"][value="${this.dataset.sort}"]`);

        if (filterInput) {
            filterInput.checked = true;
        }
        if (sortInput) {
            sortInput.checked = true;
        }
    });

    applyBtn?.addEventListener('click', () => {
        const filter = document.querySelector('input[name="filter"]:checked')?.value;
        const sort = document.querySelector('input[name="sort"]:checked')?.value;
        const params = new URLSearchParams();

        if (filter && filter !== 'no_filter') {
            params.set('filter', filter);
        }
        if (sort && sort !== 'last_visit_date_down') {
            params.set('sort', sort);
        }

        window.location.href = `${window.location.pathname}?${params.toString()}`;
    });
}

function closeOpenRegionOffcanvasOnEscape(event) {
    const offcanvas = document.getElementById('offcanvasRight');
    const backdrop = document.querySelector('[data-hs-overlay-backdrop="#offcanvasRight"]');
    if (event.key !== 'Escape' || !offcanvas?.classList.contains('translate-x-0') || !backdrop) {
        return;
    }

    offcanvas.classList.replace('translate-x-0', 'translate-x-full');
    backdrop.classList.replace('opacity-100', 'opacity-0');
    backdrop.classList.replace('pointer-events-auto', 'pointer-events-none');
    document.body.style.overflow = '';
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeRegionFilters, {once: true});
} else {
    initializeRegionFilters();
}

// This listener is installed once per entrypoint, not for every fragment refresh.
document.addEventListener('keydown', closeOpenRegionOffcanvasOnEscape);
document.addEventListener('visited-city-list-refreshed', initializeRegionFilters);
