// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-timeline-modal-trigger]').forEach((trigger) => {
        trigger.addEventListener('click', () => {
            const modalId = trigger.dataset.timelineModalTrigger;
            const modal = document.getElementById(modalId);

            if (!(modal instanceof HTMLDialogElement)) {
                return;
            }

            modal.showModal();

            requestAnimationFrame(() => {
                const scrollContainer = modal.querySelector('[data-timeline-scroll-container]');
                const firstVisitedItem = modal.querySelector('[data-timeline-first-visited]');

                if (!(scrollContainer instanceof HTMLElement) || !(firstVisitedItem instanceof HTMLElement)) {
                    return;
                }

                const firstVisitedTop = firstVisitedItem.getBoundingClientRect().top;
                const scrollContainerTop = scrollContainer.getBoundingClientRect().top;

                scrollContainer.scrollTop += firstVisitedTop - scrollContainerTop;
            });
        });
    });
});
