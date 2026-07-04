// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

document.addEventListener('DOMContentLoaded', () => {
    function scrollToFirstVisibleVisitedItem(modal) {
        const scrollContainer = modal.querySelector('[data-timeline-scroll-container]');
        const firstVisitedItem = modal.querySelector(
            '[data-timeline-first-visited]:not([hidden]), [data-timeline-item][data-timeline-year]:not([hidden])',
        );

        if (!(scrollContainer instanceof HTMLElement) || !(firstVisitedItem instanceof HTMLElement)) {
            return;
        }

        const firstVisitedTop = firstVisitedItem.getBoundingClientRect().top;
        const scrollContainerTop = scrollContainer.getBoundingClientRect().top;

        scrollContainer.scrollTop += firstVisitedTop - scrollContainerTop;
    }

    function applyYearFilter(modal) {
        const selectedYears = new Set(
            [...modal.querySelectorAll('[data-timeline-year-filter]:checked')].map((filter) => filter.value),
        );
        const timelineItems = modal.querySelectorAll('[data-timeline-item]');

        timelineItems.forEach((item) => {
            const itemYear = item.dataset.timelineYear;
            item.hidden = selectedYears.size > 0 && !selectedYears.has(itemYear);
        });

        requestAnimationFrame(() => scrollToFirstVisibleVisitedItem(modal));
    }

    document.querySelectorAll('[data-timeline-year-filter-form]').forEach((filterForm) => {
        filterForm.addEventListener('change', () => {
            const modal = filterForm.closest('dialog');

            if (modal instanceof HTMLDialogElement) {
                applyYearFilter(modal);
            }
        });

        filterForm.addEventListener('reset', () => {
            const modal = filterForm.closest('dialog');

            if (modal instanceof HTMLDialogElement) {
                requestAnimationFrame(() => applyYearFilter(modal));
            }
        });
    });

    document.querySelectorAll('[data-timeline-modal-trigger]').forEach((trigger) => {
        trigger.addEventListener('click', () => {
            const modalId = trigger.dataset.timelineModalTrigger;
            const modal = document.getElementById(modalId);

            if (!(modal instanceof HTMLDialogElement)) {
                return;
            }

            modal.showModal();

            requestAnimationFrame(() => {
                scrollToFirstVisibleVisitedItem(modal);
            });
        });
    });
});
