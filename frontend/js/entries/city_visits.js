/**
 * ---------------------------------------------
 *
 * Copyright © Egor Vavilov (Shecspi)
 * Licensed under the Apache License, Version 2.0
 *
 * ----------------------------------------------
 */

function formatDate(isoDate) {
    if (!isoDate) {
        return 'Не указана';
    }
    const [year, month, day] = isoDate.split('-');
    return `${day}.${month}.${year}`;
}

function createVisitCard(visit) {
    const card = document.createElement('article');
    card.className = 'dui-card border border-base-300 bg-base-100 shadow-sm';
    card.dataset.visitId = String(visit.id);
    card.innerHTML = `
        <div class="dui-card-body gap-3 p-4">
            <div class="flex flex-wrap items-start justify-between gap-3">
                <div class="space-y-1">
                    <p class="text-sm text-base-content/70">Дата посещения</p>
                    <p class="font-medium">${formatDate(visit.date_of_visit)}</p>
                </div>
                <div class="dui-rating dui-rating-sm" aria-label="Оценка: ${visit.rating} из 5">
                    ${Array.from({length: 5}, (_, index) => `<span class="dui-mask dui-mask-star-2 ${index < visit.rating ? 'bg-warning' : 'bg-base-300'}"></span>`).join('')}
                </div>
            </div>
            <div class="prose prose-sm max-w-none dark:prose-invert" data-visit-impression></div>
            <div class="dui-card-actions justify-end">
                <button type="button" class="btn btn-ghost-danger btn-sm delete_city"
                        data-delete_url="/city/delete/${visit.id}"
                        data-city_title="${visit.city_title || ''}"
                        data-hs-overlay="#deleteModal">
                    Удалить
                </button>
                <button type="button" class="dui-btn dui-btn-ghost dui-btn-sm"
                        data-action="edit-visited-city" data-visited-city-id="${visit.id}">
                    Редактировать
                </button>
            </div>
        </div>`;
    const impression = card.querySelector('[data-visit-impression]');
    if (visit.impression_html) {
        impression.innerHTML = visit.impression_html;
    } else {
        impression.textContent = `Вы не добавили описание поездки в город ${visit.city_title || ''}`;
    }
    return card;
}

function updateVisit(visit, {incrementCount = false} = {}) {
    const root = document.querySelector('#user-visits');
    if (!root || String(visit.city) !== root.dataset.cityId) {
        return;
    }
    const list = root.querySelector('#user-visits-list');
    if (!list) {
        return;
    }
    const card = createVisitCard(visit);
    const existing = list.querySelector(`[data-visit-id="${visit.id}"]`);
    if (existing) {
        const deleteButton = existing.querySelector('.delete_city');
        if (deleteButton) {
            card.querySelector('.dui-card-actions')?.prepend(deleteButton);
        }
        existing.replaceWith(card);
        return;
    }
    list.prepend(card);
    if (incrementCount) {
        const count = root.querySelector('#user-visits-count');
        count.textContent = String(Number(count.textContent || 0) + 1);
        root.querySelector('#user-visits-empty-state')?.remove();
        root.querySelector('#user-visits-heading')?.classList.remove('hidden');
    }
}

document.addEventListener('visited-city-created', (event) => {
    if (event.detail.visit) {
        updateVisit(event.detail.visit, {incrementCount: true});
    }
});

document.addEventListener('visited-city-updated', (event) => {
    if (event.detail.visit) {
        updateVisit(event.detail.visit);
    }
});
