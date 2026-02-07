import * as L from 'leaflet';

import {create_map} from '../components/map';
import {
    icon_visited_pin,
    icon_place_not_visited_pin,
    icon_purple_pin
} from "../components/icons";
import {showDangerToast, showSuccessToast} from '../components/toast';
import {getCookie} from '../components/get_cookie.js';

window.add_place = add_place;
window.delete_place = delete_place;
window.update_place = update_place;
window.switch_popup_elements = switch_popup_elements;
window.toggleNewCollectionField = toggleNewCollectionField;

// Карта, на которой будут отображаться все объекты
// const [center_lat, center_lon, zoom] = calculate_center_of_coordinates()
let map = create_map([55, 37], 5);

// Массив, хранящий в себе промисы, в которых загружаются необходимые данные с сервера
const allPromises = [];

// Массив, хранящий в себе информацию обо всех местах.
// Может динамически меняться и хранит в себе всю самую актуальную информацию.
// На основе этого массива можно отрисовывать маркера на карте.
const allPlaces = new Map();

// Массив, хранящий в себе все добавленные на карту маркеры.
const allMarkers = [];
const allCategories = [];
const allPlaceCollections = [];

/** Текущий фильтр по категории: '__all__' или имя категории */
let selectedCategoryName = '__all__';
/** Текущий фильтр по коллекции: null = все, иначе id коллекции */
let selectedCollectionId = null;

let moved_lat = undefined;
let moved_lon = undefined;

// Словарь, хранящий в себе все известные OSM теги и типы объектов, которые ссылаются на указанные теги
const tags = new Map();
let marker = undefined;

// Классы полей ввода и выпадающих списков (как на тулбаре /city/districts/98/map)
const FORM_INPUT_CLASS = 'w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-800 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:outline-none dark:bg-neutral-900 dark:border-neutral-700 dark:text-neutral-200 dark:focus:border-blue-500 dark:focus:ring-blue-500 h-10';
const FORM_INPUT_PLACEHOLDER_CLASS = FORM_INPUT_CLASS + ' dark:placeholder-neutral-400';
const POPUP_WIDTH = 300;

/** SVG галочки для выбранного пункта (как на /region/all/map) */
const CHECK_ICON_HTML = '<svg class="shrink-0 size-4 text-blue-600 dark:text-blue-500" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M12.736 3.97a.733.733 0 0 1 1.047 0c.286.289.29.756.01 1.05L7.88 12.01a.733.733 0 0 1-1.065.02L3.217 8.384a.757.757 0 0 1 0-1.06.733.733 0 0 1 1.047 0l3.052 3.093 5.4-6.425a.247.247 0 0 1 .02-.022Z"/></svg>';

/**
 * Экранирует строку для безопасной вставки в HTML (защита от XSS).
 * @param {string|number|null|undefined} text - значение для экранирования
 * @returns {string}
 */
function escapeHtml(text) {
    if (text == null || text === undefined) return '';
    const s = String(text);
    return s
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

/**
 * Выставляет класс start-0 или end-0 у меню, чтобы оно не выходило за пределы экрана.
 * @param {HTMLElement} trigger - кнопка, открывающая выпадающий список
 * @param {HTMLElement} menu - элемент ul.hs-dropdown-menu
 */
function positionDropdownInViewport(trigger, menu) {
    if (!trigger || !menu) return;
    const triggerRect = trigger.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const gap = 8;
    // Ширина меню: по классу sm:min-w-[280px], можно измерить после показа
    const menuWidth = menu.offsetWidth || 280;
    const spaceOnRight = viewportWidth - triggerRect.left;
    const spaceOnLeft = triggerRect.right;
    if (spaceOnRight >= menuWidth + gap) {
        menu.classList.remove('end-0');
        menu.classList.add('start-0');
    } else if (spaceOnLeft >= menuWidth + gap) {
        menu.classList.remove('start-0');
        menu.classList.add('end-0');
    } else {
        menu.classList.remove('end-0');
        menu.classList.add('start-0');
    }
}

function updateDropdownCheckmarks(menuEl, selectedValue) {
    if (!menuEl) return;
    const valueStr = selectedValue === null || selectedValue === undefined ? '' : String(selectedValue);
    menuEl.querySelectorAll('li[data-value]').forEach(li => {
        const check = li.querySelector('.place-filter-check');
        if (check) {
            if (li.getAttribute('data-value') === valueStr) {
                check.classList.remove('hidden');
            } else {
                check.classList.add('hidden');
            }
        }
    });
}

function updateFilterBadges() {
    const badgeCategory = document.getElementById('badge-filter-category');
    const badgeCollection = document.getElementById('badge-filter-collection');
    if (badgeCategory) {
        if (selectedCategoryName !== '__all__') {
            badgeCategory.classList.remove('hidden');
        } else {
            badgeCategory.classList.add('hidden');
        }
    }
    if (badgeCollection) {
        if (selectedCollectionId !== null && selectedCollectionId !== undefined) {
            badgeCollection.classList.remove('hidden');
        } else {
            badgeCollection.classList.add('hidden');
        }
    }
    const collectionButtonText = document.getElementById('btn-filter-collection-text');
    if (collectionButtonText) {
        if (selectedCollectionId !== null && selectedCollectionId !== undefined) {
            const coll = allPlaceCollections.find(c => String(c.id) === String(selectedCollectionId));
            const title = coll ? coll.title : 'Коллекции';
            collectionButtonText.textContent = title;
            collectionButtonText.title = title;
        } else {
            collectionButtonText.textContent = 'Коллекции';
            collectionButtonText.title = 'Коллекции';
        }
    }
    const viewContextEl = document.getElementById('place-map-view-context');
    if (viewContextEl) {
        if (selectedCollectionId !== null && selectedCollectionId !== undefined) {
            const coll = allPlaceCollections.find(c => String(c.id) === String(selectedCollectionId));
            viewContextEl.textContent = coll ? `Коллекция: «${coll.title}»` : 'Все коллекции';
        } else {
            viewContextEl.textContent = 'Все коллекции';
        }
    }
    updateCollectionToolbarActions();
}

/** Показывает блок «Публичная коллекция», «Поделиться» и «Редактировать»; при «все коллекции» элементы неактивны. */
function updateCollectionToolbarActions() {
    const block = document.getElementById('toolbar-collection-actions');
    const checkbox = document.getElementById('toolbar-collection-is-public');
    const shareBtn = document.getElementById('toolbar-collection-share');
    const editBtn = document.getElementById('toolbar-collection-edit');
    const deleteBtn = document.getElementById('toolbar-collection-delete');
    if (!block || !checkbox || !shareBtn) return;

    const hasCollection = selectedCollectionId != null && allPlaceCollections.find(
        c => String(c.id) === String(selectedCollectionId)
    );

    if (!hasCollection) {
        checkbox.disabled = true;
        shareBtn.disabled = true;
        if (editBtn) editBtn.disabled = true;
        if (deleteBtn) deleteBtn.disabled = true;
        checkbox.checked = false;
        return;
    }

    const collection = allPlaceCollections.find(
        c => String(c.id) === String(selectedCollectionId)
    );
    checkbox.disabled = false;
    checkbox.checked = collection.is_public === true;
    shareBtn.disabled = !collection.is_public;
    if (editBtn) editBtn.disabled = false;
    if (deleteBtn) deleteBtn.disabled = false;

    if (!shareBtn.dataset.collectionActionsBound) {
        shareBtn.dataset.collectionActionsBound = '1';
        checkbox.addEventListener('change', function () {
            const newPublic = checkbox.checked;
            fetch(`/api/place/collections/${selectedCollectionId}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json;charset=utf-8',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ is_public: newPublic })
            })
                .then(response => {
                    if (!response.ok) throw new Error('Не удалось обновить коллекцию');
                    return response.json();
                })
                .then(updated => {
                    const idx = allPlaceCollections.findIndex(c => String(c.id) === String(updated.id));
                    if (idx !== -1) allPlaceCollections[idx] = updated;
                    updateCollectionToolbarActions();
                    showSuccessToast('Сохранено', newPublic ? 'Коллекция теперь публичная' : 'Коллекция теперь приватная');
                })
                .catch(() => {
                    checkbox.checked = !newPublic;
                    showDangerToast('Ошибка', 'Не удалось изменить видимость коллекции');
                });
        });
        shareBtn.addEventListener('click', function () {
            if (shareBtn.disabled) return;
            const coll = allPlaceCollections.find(c => String(c.id) === String(selectedCollectionId));
            if (!coll || !coll.is_public) return;
            const shareData = {
                title: coll.title,
                text: `Коллекция мест: ${coll.title}`,
                url: window.location.href
            };
            if (navigator.share) {
                navigator.share(shareData)
                    .then(() => showSuccessToast('Готово', 'Ссылка передана'))
                    .catch(err => {
                        if (err.name !== 'AbortError') {
                            showDangerToast('Ошибка', 'Не удалось поделиться');
                        }
                    });
            } else {
                navigator.clipboard.writeText(window.location.href).then(
                    () => showSuccessToast('Скопировано', 'Ссылка на коллекцию скопирована в буфер обмена'),
                    () => showDangerToast('Ошибка', 'Не удалось скопировать ссылку')
                );
            }
        });
    }
}

/** Модальное окно редактирования названия коллекции */
function setupEditCollectionModal() {
    const modal = document.getElementById('modal-edit-place-collection');
    const form = document.getElementById('form-edit-place-collection');
    const titleInput = document.getElementById('modal-edit-place-collection-title');
    const submitBtn = document.getElementById('modal-edit-place-collection-submit');
    if (!modal || !form || !titleInput || !submitBtn) return;

    modal.addEventListener('open.hs.overlay', function () {
        if (selectedCollectionId === null || selectedCollectionId === undefined) return;
        const coll = allPlaceCollections.find(c => String(c.id) === String(selectedCollectionId));
        titleInput.value = coll ? (coll.title || '') : '';
    });

    // Preline перехватывает Enter и блокирует submit формы. Явно обрабатываем Enter в поле ввода:
    titleInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            e.stopPropagation();
            form.requestSubmit();
        }
    });

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        const title = titleInput.value.trim();
        if (!title) {
            showDangerToast('Ошибка', 'Введите название коллекции');
            return;
        }
        if (selectedCollectionId === null || selectedCollectionId === undefined) return;
        const coll = allPlaceCollections.find(c => String(c.id) === String(selectedCollectionId));
        if (!coll) return;
        if (title === (coll.title || '')) {
            document.querySelector('[data-hs-overlay="#modal-edit-place-collection"]')?.click();
            return;
        }
        submitBtn.disabled = true;
        fetch(`/api/place/collections/${selectedCollectionId}/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json;charset=utf-8',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ title: title })
        })
            .then(response => {
                if (!response.ok) throw new Error('Не удалось переименовать коллекцию');
                return response.json();
            })
            .then(updated => {
                const idx = allPlaceCollections.findIndex(c => String(c.id) === String(updated.id));
                if (idx !== -1) allPlaceCollections[idx] = updated;
                updateFilterBadges();
                const viewContextEl = document.getElementById('place-map-view-context');
                if (viewContextEl && String(selectedCollectionId) === String(updated.id)) {
                    viewContextEl.textContent = `Коллекция: «${updated.title}»`;
                }
                showSuccessToast('Сохранено', 'Название коллекции обновлено');
                document.querySelector('[data-hs-overlay="#modal-edit-place-collection"]')?.click();
            })
            .catch(() => {
                showDangerToast('Ошибка', 'Не удалось переименовать коллекцию');
            })
            .finally(() => {
                submitBtn.disabled = false;
            });
    });
}
setupEditCollectionModal();

/** Модальное окно удаления коллекции */
function setupDeleteCollectionModal() {
    const modal = document.getElementById('modal-delete-place-collection');
    const form = document.getElementById('form-delete-place-collection');
    const nameDisplay = document.getElementById('modal-delete-place-collection-name-display');
    const nameInput = document.getElementById('modal-delete-place-collection-confirm-name');
    const deletePlacesCheckbox = document.getElementById('modal-delete-place-collection-delete-places');
    const submitBtn = document.getElementById('modal-delete-place-collection-submit');
    if (!modal || !form || !nameInput || !submitBtn) return;

    function checkConfirmName() {
        if (selectedCollectionId == null) return;
        const coll = allPlaceCollections.find(c => String(c.id) === String(selectedCollectionId));
        const expected = coll ? (coll.title || '').trim() : '';
        submitBtn.disabled = nameInput.value.trim() !== expected;
    }

    const nameCopyWrap = document.getElementById('modal-delete-place-collection-name-copy');
    if (nameCopyWrap && nameDisplay) {
        nameCopyWrap.addEventListener('click', function () {
            const text = nameDisplay.textContent;
            if (!text || text === '—') return;
            navigator.clipboard.writeText(text).then(
                () => showSuccessToast('Скопировано', 'Название коллекции скопировано в буфер обмена'),
                () => showDangerToast('Ошибка', 'Не удалось скопировать')
            );
        });
        nameCopyWrap.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                nameCopyWrap.click();
            }
        });
    }

    modal.addEventListener('open.hs.overlay', function () {
        if (selectedCollectionId === null || selectedCollectionId === undefined) return;
        const coll = allPlaceCollections.find(c => String(c.id) === String(selectedCollectionId));
        if (!coll) return;
        if (nameDisplay) nameDisplay.textContent = coll.title || '—';
        nameInput.value = '';
        nameInput.placeholder = coll.title || '';
        if (deletePlacesCheckbox) deletePlacesCheckbox.checked = false;
        submitBtn.disabled = true;
    });

    nameInput.addEventListener('input', checkConfirmName);
    nameInput.addEventListener('change', checkConfirmName);

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        if (selectedCollectionId === null || selectedCollectionId === undefined) return;
        const coll = allPlaceCollections.find(c => String(c.id) === String(selectedCollectionId));
        if (!coll || nameInput.value.trim() !== (coll.title || '').trim()) return;
        const deletePlaces = deletePlacesCheckbox ? deletePlacesCheckbox.checked : false;
        submitBtn.disabled = true;
        fetch(`/api/place/collections/${selectedCollectionId}/`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json;charset=utf-8',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ delete_places: deletePlaces })
        })
            .then(response => {
                if (!response.ok) throw new Error('Не удалось удалить коллекцию');
            })
            .then(() => {
                const deletedId = String(selectedCollectionId);
                const idx = allPlaceCollections.findIndex(c => String(c.id) === deletedId);
                if (idx !== -1) allPlaceCollections.splice(idx, 1);
                if (String(selectedCollectionId) === deletedId) {
                    selectedCollectionId = null;
                    updateCollectionUrl();
                }
                if (deletePlaces) {
                    const idsToDelete = [];
                    allPlaces.forEach((place, id) => {
                        if ((place.collection_detail && String(place.collection_detail.id) === deletedId) ||
                            (place.collection != null && String(place.collection) === deletedId)) {
                            idsToDelete.push(id);
                        }
                    });
                    idsToDelete.forEach(id => allPlaces.delete(id));
                } else {
                    allPlaces.forEach((place, id) => {
                        if ((place.collection_detail && String(place.collection_detail.id) === deletedId) ||
                            (place.collection != null && String(place.collection) === deletedId)) {
                            place.collection = null;
                            place.collection_detail = null;
                            allPlaces.set(id, place);
                        }
                    });
                }
                updateMarkers();
                const dropdownMenuCollection = document.getElementById('dropdown-menu-filter-collection');
                if (dropdownMenuCollection) {
                    dropdownMenuCollection.querySelectorAll('li[data-value]').forEach(li => {
                        if (li.getAttribute('data-value') === deletedId) li.remove();
                    });
                }
                updateFilterBadges();
                if (initialCollectionUuid && String(initialCollectionUuid) === deletedId) {
                    window.history.replaceState(null, '', window.location.pathname);
                }
                showSuccessToast('Удалено', 'Коллекция удалена');
                const modal = document.getElementById('modal-delete-place-collection');
                const closeBtn = modal?.querySelector('[data-hs-overlay="#modal-delete-place-collection"]');
                if (closeBtn) closeBtn.click();
            })
            .catch(() => {
                showDangerToast('Ошибка', 'Не удалось удалить коллекцию');
            })
            .finally(() => {
                submitBtn.disabled = false;
            });
    });
}
setupDeleteCollectionModal();

/**
 * Обновляет URL в адресной строке по текущему выбранному фильтру коллекции:
 * при выбранной коллекции — ?collection=<uuid>, при «Все коллекции» — параметр collection убирается.
 */
function updateCollectionUrl() {
    const params = new URLSearchParams(window.location.search);
    if (selectedCollectionId === null || selectedCollectionId === undefined) {
        params.delete('collection');
    } else {
        params.set('collection', String(selectedCollectionId));
    }
    const search = params.toString();
    const url = window.location.pathname + (search ? '?' + search : '');
    window.history.replaceState(null, '', url);
}

const isAuthenticated = window.PLACE_MAP_USER_AUTHENTICATED !== false;
const initialCollectionUuid = typeof window.PLACE_MAP_COLLECTION_UUID === 'string' && window.PLACE_MAP_COLLECTION_UUID.trim() !== ''
    ? window.PLACE_MAP_COLLECTION_UUID.trim()
    : null;
const placeMapTooltipOnly = window.PLACE_MAP_TOOLTIP_ONLY === true;
if (initialCollectionUuid) {
    // Открыта страница конкретной коллекции (своей или чужой) — запрашиваем места этой коллекции
    allPromises.push(loadPlacesFromServer(initialCollectionUuid));
    if (isAuthenticated) {
        allPromises.push(loadCategoriesFromServer());
        allPromises.push(loadPlaceCollectionsFromServer());
    } else {
        allPromises.push(Promise.resolve([]));
        allPromises.push(Promise.resolve([]));
    }
} else if (isAuthenticated) {
    allPromises.push(loadPlacesFromServer(null));
    allPromises.push(loadCategoriesFromServer());
    allPromises.push(loadPlaceCollectionsFromServer());
} else {
    allPromises.push(Promise.resolve([]));
    allPromises.push(Promise.resolve([]));
    allPromises.push(Promise.resolve([]));
}
Promise.all([...allPromises]).then(([places, categories, collections]) => {
    // Получаем все категории и заполняем фильтр по ним (элементы есть только у авторизованных)
    const button = document.getElementById('btn-filter-category');
    const select_filter_by_category = document.getElementById('dropdown-menu-filter-category');

    if (button && select_filter_by_category) {
    button.disabled = false;
    // Убираем спиннер
    const spinner = button.querySelector('span[role="status"]');
    if (spinner) {
        spinner.remove();
    }
    // Показываем иконку
    const iconContainer = document.getElementById('btn-filter-category-icon');
    if (iconContainer) {
        iconContainer.classList.remove('hidden');
    }
    // Показываем текст на кнопке
    const buttonText = document.getElementById('btn-filter-category-text');
    if (buttonText) {
        buttonText.classList.remove('hidden');
    }

    (collections || []).forEach(coll => {
        allPlaceCollections.push(coll);
    });

    categories.forEach(category => {
        allCategories.push(category);
        category.tags_detail.forEach(tag => {
            tags.set(tag.name, category.name);
        });

        const li = document.createElement('li');
        li.setAttribute('data-value', category.name);
        const filter_by_category_item = document.createElement('a');
        filter_by_category_item.classList.add('flex', 'items-center', 'justify-between', 'gap-x-2', 'rounded-lg', 'px-3', 'py-2', 'text-sm', 'text-gray-800', 'hover:bg-gray-100', 'dark:text-neutral-200', 'dark:hover:bg-neutral-700');
        filter_by_category_item.innerHTML = `<span class="flex items-center min-h-5">${escapeHtml(category.name)}</span><span class="place-filter-check hidden shrink-0 inline-flex items-center">${CHECK_ICON_HTML}</span>`;
        filter_by_category_item.style.cursor = 'pointer';
        filter_by_category_item.addEventListener('click', () => {
            selectedCategoryName = category.name;
            updateMarkers();
            updateDropdownCheckmarks(select_filter_by_category, selectedCategoryName);
            updateFilterBadges();
        });
        li.appendChild(filter_by_category_item);
        select_filter_by_category.appendChild(li);
    });

    // Добавляем пункт "Все категории"
    const divider = document.createElement('hr');
    divider.classList.add('my-2', 'border-gray-200', 'dark:border-neutral-700');
    const dividerLi = document.createElement('li');
    dividerLi.appendChild(divider);
    select_filter_by_category.appendChild(dividerLi);

    const allCategoriesLi = document.createElement('li');
    allCategoriesLi.setAttribute('data-value', '__all__');
    const all_categories = document.createElement('a');
    all_categories.classList.add('flex', 'items-center', 'justify-between', 'gap-x-2', 'rounded-lg', 'px-3', 'py-2', 'text-sm', 'text-gray-800', 'hover:bg-gray-100', 'dark:text-neutral-200', 'dark:hover:bg-neutral-700');
    all_categories.innerHTML = '<span class="flex items-center min-h-5">Показать все категории</span><span class="place-filter-check hidden shrink-0 inline-flex items-center">' + CHECK_ICON_HTML + '</span>';
    all_categories.style.cursor = 'pointer';
    allCategoriesLi.appendChild(all_categories);
    select_filter_by_category.appendChild(allCategoriesLi);
    all_categories.addEventListener('click', () => {
        selectedCategoryName = '__all__';
        updateMarkers();
        updateDropdownCheckmarks(select_filter_by_category, selectedCategoryName);
        updateFilterBadges();
    });
    updateDropdownCheckmarks(select_filter_by_category, selectedCategoryName);
    updateFilterBadges();

    // Выпадающий список коллекций
    const btnFilterCollection = document.getElementById('btn-filter-collection');
    const dropdownMenuCollection = document.getElementById('dropdown-menu-filter-collection');
    if (btnFilterCollection && dropdownMenuCollection) {
        btnFilterCollection.disabled = false;
        const spinnerColl = btnFilterCollection.querySelector('span[role="status"]');
        if (spinnerColl) spinnerColl.remove();
        const iconColl = document.getElementById('btn-filter-collection-icon');
        if (iconColl) iconColl.classList.remove('hidden');
        const textColl = document.getElementById('btn-filter-collection-text');
        if (textColl) textColl.classList.remove('hidden');

        const allCollectionsLi = document.createElement('li');
        allCollectionsLi.setAttribute('data-value', '');
        const allCollectionsItem = document.createElement('a');
        allCollectionsItem.classList.add('flex', 'items-center', 'justify-between', 'gap-x-2', 'rounded-lg', 'px-3', 'py-2', 'text-sm', 'text-gray-800', 'hover:bg-gray-100', 'dark:text-neutral-200', 'dark:hover:bg-neutral-700');
        allCollectionsItem.innerHTML = '<span class="flex items-center min-h-5">Все коллекции</span><span class="place-filter-check hidden shrink-0 inline-flex items-center">' + CHECK_ICON_HTML + '</span>';
        allCollectionsItem.style.cursor = 'pointer';
        allCollectionsLi.appendChild(allCollectionsItem);
        dropdownMenuCollection.appendChild(allCollectionsLi);
        allCollectionsItem.addEventListener('click', () => {
            selectedCollectionId = null;
            updateMarkers();
            updateDropdownCheckmarks(dropdownMenuCollection, selectedCollectionId === null ? '' : selectedCollectionId);
            updateFilterBadges();
            updateCollectionUrl();
        });

        (allPlaceCollections || []).forEach(coll => {
            const li = document.createElement('li');
            li.setAttribute('data-value', String(coll.id));
            const item = document.createElement('a');
            item.classList.add('flex', 'items-center', 'justify-between', 'gap-x-2', 'rounded-lg', 'px-3', 'py-2', 'text-sm', 'text-gray-800', 'hover:bg-gray-100', 'dark:text-neutral-200', 'dark:hover:bg-neutral-700');
            item.innerHTML = `<span class="flex items-center min-h-5">${escapeHtml(coll.title)}</span><span class="place-filter-check hidden shrink-0 inline-flex items-center">${CHECK_ICON_HTML}</span>`;
            item.style.cursor = 'pointer';
            li.appendChild(item);
            dropdownMenuCollection.appendChild(li);
            item.addEventListener('click', () => {
                selectedCollectionId = coll.id;
                updateMarkers();
                updateDropdownCheckmarks(dropdownMenuCollection, selectedCollectionId === null ? '' : selectedCollectionId);
                updateFilterBadges();
                updateCollectionUrl();
            });
        });
        updateDropdownCheckmarks(dropdownMenuCollection, selectedCollectionId === null ? '' : selectedCollectionId);
        updateFilterBadges();

        const initialCollectionUuid = typeof window.PLACE_MAP_COLLECTION_UUID === 'string' && window.PLACE_MAP_COLLECTION_UUID.trim() !== ''
            ? window.PLACE_MAP_COLLECTION_UUID.trim()
            : null;
        if (initialCollectionUuid) {
            selectedCollectionId = initialCollectionUuid;
            updateMarkers();
            updateDropdownCheckmarks(dropdownMenuCollection, selectedCollectionId === null ? '' : selectedCollectionId);
            updateFilterBadges();
        }

        dropdownMenuCollection.classList.remove('hidden');
        dropdownMenuCollection.classList.add('opacity-0', 'pointer-events-none');

        const dropdownElementCollection = btnFilterCollection.closest('.hs-dropdown');
        btnFilterCollection.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const isHidden = dropdownMenuCollection.classList.contains('opacity-0');
            if (isHidden) {
                // Закрываем выпадающий список категорий, если открыт
                dropdownMenu.classList.remove('opacity-100');
                dropdownMenu.classList.add('opacity-0', 'pointer-events-none');
                button.setAttribute('aria-expanded', 'false');
                const wrapCategory = document.getElementById('dropdown-category-wrap');
                const wrapCollection = document.getElementById('dropdown-collection-wrap');
                if (wrapCategory) wrapCategory.classList.remove('z-[50]');
                if (wrapCollection) wrapCollection.classList.add('z-[50]');
                positionDropdownInViewport(btnFilterCollection, dropdownMenuCollection);
                dropdownMenuCollection.classList.remove('opacity-0', 'pointer-events-none');
                dropdownMenuCollection.classList.add('opacity-100');
                btnFilterCollection.setAttribute('aria-expanded', 'true');
            } else {
                const wrapCollection = document.getElementById('dropdown-collection-wrap');
                if (wrapCollection) wrapCollection.classList.remove('z-[50]');
                dropdownMenuCollection.classList.remove('opacity-100');
                dropdownMenuCollection.classList.add('opacity-0', 'pointer-events-none');
                btnFilterCollection.setAttribute('aria-expanded', 'false');
            }
        });
        document.addEventListener('click', function(e) {
            if (dropdownElementCollection && !dropdownElementCollection.contains(e.target)) {
                const wrapCollection = document.getElementById('dropdown-collection-wrap');
                if (wrapCollection) wrapCollection.classList.remove('z-[50]');
                dropdownMenuCollection.classList.remove('opacity-100');
                dropdownMenuCollection.classList.add('opacity-0', 'pointer-events-none');
                btnFilterCollection.setAttribute('aria-expanded', 'false');
            }
        });
    }

    // Инициализируем Preline UI dropdown после добавления элементов
    const dropdownElement = button.closest('.hs-dropdown');
    const dropdownMenu = select_filter_by_category;
    
    // Убираем класс hidden и используем opacity для анимации
    dropdownMenu.classList.remove('hidden');
    dropdownMenu.classList.add('opacity-0', 'pointer-events-none');
    
    // Добавляем обработчик клика для открытия/закрытия dropdown
    button.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const isHidden = dropdownMenu.classList.contains('opacity-0');
        if (isHidden) {
            // Закрываем выпадающий список коллекций, если открыт
            if (dropdownMenuCollection) {
                dropdownMenuCollection.classList.remove('opacity-100');
                dropdownMenuCollection.classList.add('opacity-0', 'pointer-events-none');
                if (btnFilterCollection) btnFilterCollection.setAttribute('aria-expanded', 'false');
            }
            const wrapCategory = document.getElementById('dropdown-category-wrap');
            const wrapCollection = document.getElementById('dropdown-collection-wrap');
            if (wrapCollection) wrapCollection.classList.remove('z-[50]');
            if (wrapCategory) wrapCategory.classList.add('z-[50]');
            positionDropdownInViewport(button, dropdownMenu);
            dropdownMenu.classList.remove('opacity-0', 'pointer-events-none');
            dropdownMenu.classList.add('opacity-100');
            button.setAttribute('aria-expanded', 'true');
        } else {
            const wrapCategory = document.getElementById('dropdown-category-wrap');
            if (wrapCategory) wrapCategory.classList.remove('z-[50]');
            dropdownMenu.classList.remove('opacity-100');
            dropdownMenu.classList.add('opacity-0', 'pointer-events-none');
            button.setAttribute('aria-expanded', 'false');
        }
    });
    
    // Закрываем dropdown при клике вне его
    document.addEventListener('click', function(e) {
        if (!dropdownElement.contains(e.target)) {
            const wrapCategory = document.getElementById('dropdown-category-wrap');
            if (wrapCategory) wrapCategory.classList.remove('z-[50]');
            dropdownMenu.classList.remove('opacity-100');
            dropdownMenu.classList.add('opacity-0', 'pointer-events-none');
            button.setAttribute('aria-expanded', 'false');
        }
    });
    
    // Инициализируем Preline UI dropdown для правильной работы
    if (window.HSStaticMethods && typeof window.HSStaticMethods.autoInit === 'function') {
        window.HSStaticMethods.autoInit();
    }
    }

    // Расставляем метки
    places.forEach(place => {
        allPlaces.set(place.id, place);
    });
    addMarkers();

    if (places.length === 0) {
        map.setView([55.751426, 37.618879], 12);
    } else {
        const group = new L.featureGroup([...allMarkers]);
        map.fitBounds(group.getBounds());
    }

    handleClickOnMap(map);
});

function updateBlockQtyPlaces(qty_places) {
    const block_qty_places_text = document.getElementById('block-qty_places-text');
    if (!block_qty_places_text) return;
    block_qty_places_text.innerHTML = `Отмечено мест: <strong>${qty_places}</strong>`;
}

function loadCategoriesFromServer() {
    return fetch('/api/place/category/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Произошла ошибка при получении данных с сервера');
            }
            return response.json();
        })
        .then(data => {
            return data;
        });
}

function loadPlacesFromServer(collectionUuid) {
    const url = collectionUuid
        ? `/api/place/?collection=${encodeURIComponent(collectionUuid)}`
        : '/api/place/';
    return fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Произошла ошибка при получении данных с сервера');
            }
            return response.json();
        })
        .then(places => {
            return places;
        });
}

function loadPlaceCollectionsFromServer() {
    return fetch('/api/place/collections/')
        .then(response => {
            if (!response.ok) {
                return [];
            }
            return response.json();
        })
        .then(data => {
            return data;
        });
}

/**
 * HTML переключателя (toggle) как на странице персональной коллекции: уменьшенный, с иконками крестика и галочки.
 */
function toggleSwitchHtml(id, name, checked, onchangeAttr) {
    const checkedStr = checked ? ' checked' : '';
    return '<label for="' + id + '" class="relative inline-block w-10 h-5 cursor-pointer shrink-0">' +
        '<input type="checkbox" id="' + id + '" name="' + name + '" class="peer sr-only"' + checkedStr + onchangeAttr + '>' +
        '<span class="absolute inset-0 bg-gray-200 rounded-full transition-colors duration-200 ease-in-out peer-checked:bg-blue-600 dark:bg-neutral-700 dark:peer-checked:bg-blue-500 peer-disabled:opacity-50 peer-disabled:pointer-events-none"></span>' +
        '<span class="absolute top-1/2 start-0.5 -translate-y-1/2 size-4 bg-white rounded-full shadow-xs transition-transform duration-200 ease-in-out peer-checked:translate-x-5 dark:bg-neutral-400 dark:peer-checked:bg-white"></span>' +
        '<span class="absolute top-1/2 start-0.5 -translate-y-1/2 flex justify-center items-center size-4 text-gray-500 peer-checked:text-white transition-colors duration-200 dark:text-neutral-500">' +
        '<svg class="shrink-0 size-2.5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"></path><path d="m6 6 12 12"></path></svg>' +
        '</span>' +
        '<span class="absolute top-1/2 end-0.5 -translate-y-1/2 flex justify-center items-center size-4 text-gray-500 peer-checked:text-blue-600 transition-colors duration-200 dark:text-neutral-500">' +
        '<svg class="shrink-0 size-2.5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>' +
        '</span>' +
        '</label>';
}

function toggleNewCollectionField(checkbox) {
    const dropdownWrap = document.getElementById('place-collection-dropdown-wrap');
    const inputWrap = document.getElementById('place-new-collection-wrap');
    if (!dropdownWrap || !inputWrap) return;
    if (checkbox.checked) {
        dropdownWrap.classList.add('hidden');
        inputWrap.classList.remove('hidden');
    } else {
        dropdownWrap.classList.remove('hidden');
        inputWrap.classList.add('hidden');
    }
}

/**
 * Добавляет пункт коллекции в выпадающий список «Коллекции» (при создании новой коллекции при добавлении места).
 */
function appendCollectionToDropdown(coll) {
    const dropdownMenuCollection = document.getElementById('dropdown-menu-filter-collection');
    if (!dropdownMenuCollection) return;
    const li = document.createElement('li');
    li.setAttribute('data-value', String(coll.id));
    const item = document.createElement('a');
    item.classList.add('flex', 'items-center', 'justify-between', 'gap-x-2', 'rounded-lg', 'px-3', 'py-2', 'text-sm', 'text-gray-800', 'hover:bg-gray-100', 'dark:text-neutral-200', 'dark:hover:bg-neutral-700');
    item.innerHTML = `<span class="flex items-center min-h-5">${escapeHtml(coll.title)}</span><span class="place-filter-check hidden shrink-0 inline-flex items-center">${CHECK_ICON_HTML}</span>`;
    item.style.cursor = 'pointer';
    li.appendChild(item);
    dropdownMenuCollection.appendChild(li);
    item.addEventListener('click', () => {
        selectedCollectionId = coll.id;
        updateMarkers();
        updateDropdownCheckmarks(dropdownMenuCollection, selectedCollectionId === null ? '' : selectedCollectionId);
        updateFilterBadges();
        updateCollectionUrl();
    });
}

/**
 * Возвращает Promise с id коллекции для места:
 * если отмечено «Добавить новую коллекцию» и введено название — создаёт коллекцию через API;
 * иначе возвращает выбранное значение из выпадающего списка или null.
 */
function resolveCollectionIdForPlace() {
    const addNewCheckbox = document.getElementById('form-add-new-collection');
    const useNewCollection = addNewCheckbox && addNewCheckbox.checked;
    const newTitleEl = document.getElementById('form-new-collection-title');
    const newTitle = newTitleEl ? newTitleEl.value.trim() : '';
    const collectionEl = document.getElementById('form-collection');
    const rawCollection = collectionEl ? collectionEl.value : '';
    const dropdownValue = rawCollection.trim() === '' ? null : rawCollection.trim();

    if (useNewCollection && newTitle) {
        return fetch('/api/place/collections/create/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json;charset=utf-8',
                'X-CSRFToken': getCookie("csrftoken")
            },
            body: JSON.stringify({ title: newTitle, is_public: false })
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Не удалось создать коллекцию');
                }
                return response.json();
            })
            .then(collection => {
                allPlaceCollections.push(collection);
                appendCollectionToDropdown(collection);
                return collection.id;
            });
    }
    return Promise.resolve(dropdownValue);
}

function handleClickOnMap(map) {
    if (placeMapTooltipOnly) {
        return;
    }
    map.addEventListener('click', function (ev) {
        const lat = ev.latlng.lat;
        const lon = ev.latlng.lng;
        moved_lon = undefined;
        moved_lat = undefined;

        if (marker !== undefined) {
            map.removeLayer(marker);
        }

        // Сразу показываем маркер и попап с заглушкой, не ждём ответа API
        marker = L.marker(
            [lat, lon],
            {
                icon: icon_purple_pin,
                draggable: true,
                bounceOnAdd: true
            }
        ).addTo(map);

        allMarkers.push(marker);

        let content = '<form id="place-form">';
        content += generatePopupContentForNewPlace('Загрузка…', lat, lon, undefined, false);
        content += '<p class="mt-3 flex gap-2">';
        content += `<button type="button" class="py-2 px-4 inline-flex items-center justify-center gap-x-2 text-sm font-semibold rounded-lg border border-transparent bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-50 disabled:pointer-events-none focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 dark:focus:ring-offset-neutral-800" id="btn-add-place" onclick="add_place();">Добавить</button>`;
        content += '</p>';
        content += '</form>';

        marker.bindPopup(content, { minWidth: POPUP_WIDTH, maxWidth: POPUP_WIDTH });
        marker.on('popupopen', function () {
            const popupForm = this.getPopup().getElement().querySelector('#place-form');
            if (popupForm && !popupForm.dataset.submitBound) {
                popupForm.dataset.submitBound = '1';
                popupForm.addEventListener('submit', function (e) {
                    e.preventDefault();
                    add_place();
                });
            }
        });
        marker.openPopup();

        marker.on("dragend", function (e) {
            moved_lat = e.target.getLatLng().lat;
            moved_lon = e.target.getLatLng().lng;
        });

        // Запрос к Nominatim в фоне; по ответу обновляем попап
        const url = `https://nominatim.openstreetmap.org/reverse?email=shecspi@yandex.ru&format=jsonv2&lat=${lat}&lon=${lon}&addressdetails=0&zoom=18&layer=natural,poi`;
        fetch(url)
            .then(response => response.json())
            .then(data => {
                let name;
                let lat_marker;
                let lon_marker;
                let type_marker;

                if (data.hasOwnProperty('error')) {
                    name = 'Неизвестный объект';
                    lat_marker = lat;
                    lon_marker = lon;
                } else {
                    if (data.name !== '') {
                        name = data.name;
                    } else if (data.display_name !== '') {
                        name = data.display_name;
                    } else {
                        name = 'Неизвестный объект';
                    }
                    lat_marker = data.lat;
                    lon_marker = data.lon;
                }

                if (data.type !== undefined && tags.has(data.type)) {
                    type_marker = tags.get(data.type);
                }

                if (marker && marker.setLatLng) {
                    marker.setLatLng([lat_marker, lon_marker]);
                }
                // Обновляем поля попапа без замены разметки, чтобы интерфейс не скакал
                if (marker && marker.getPopup()) {
                    const el = marker.getPopup().getElement();
                    if (el) {
                        const nameInput = el.querySelector('#form-name');
                        if (nameInput) nameInput.value = name;
                        const latInput = el.querySelector('#form-latitude');
                        if (latInput) latInput.value = lat_marker;
                        const lonInput = el.querySelector('#form-longitude');
                        if (lonInput) lonInput.value = lon_marker;
                        const coordsP = el.querySelector('#popup-coords');
                        if (coordsP) {
                            coordsP.innerHTML = '<span class="font-semibold text-gray-900 dark:text-white">Широта:</span> ' + escapeHtml(lat_marker) + '<br>' +
                                '<span class="font-semibold text-gray-900 dark:text-white">Долгота:</span> ' + escapeHtml(lon_marker);
                        }
                        const categorySelect = el.querySelector('#form-type-object');
                        if (categorySelect && type_marker !== undefined) {
                            for (let i = 0; i < categorySelect.options.length; i++) {
                                if (categorySelect.options[i].text === type_marker) {
                                    categorySelect.selectedIndex = i;
                                    break;
                                }
                            }
                        }
                    }
                }
            });
    });
}

function generatePopupContentForNewPlace(name, latitude, longitude, place_category, showCoordinates) {
    if (showCoordinates === undefined) {
        showCoordinates = true;
    }
    const nameSafe = name ?? '';
    const latSafe = latitude ?? '';
    const lonSafe = longitude ?? '';
    let content = `<div class="w-full" style="min-width: ${POPUP_WIDTH}px;">`;
    content += '<p class="text-sm">';
    content += '<span class="font-semibold text-gray-900 dark:text-white">Название:</span> ';
    content += `<input type="text" id="form-name" name="name" value="${escapeHtml(nameSafe)}" class="mt-1 ${FORM_INPUT_CLASS}">`;
    content += '</p>';

    content += `<input type="text" id="form-latitude" name="latitude" value="${escapeHtml(latSafe)}" hidden>`;
    content += `<input type="text" id="form-longitude" name="longitude" value="${escapeHtml(lonSafe)}" hidden>`;
    content += '<p id="popup-coords" class="text-sm mt-2">';
    content += '<span class="font-semibold text-gray-900 dark:text-white">Широта:</span> ';
    content += showCoordinates ? `${escapeHtml(latSafe)}<br>` : '—<br>';
    content += '<span class="font-semibold text-gray-900 dark:text-white">Долгота:</span> ';
    content += showCoordinates ? escapeHtml(lonSafe) : '—';
    content += '</p>';

    content += '<p id="category_select_form" class="text-sm mt-2">';
    content += '<span class="font-semibold text-gray-900 dark:text-white">Категория:</span> ';
    content += `<select name="category" id="form-type-object" class="mt-1 ${FORM_INPUT_CLASS}">`;
    content += '<option value="" selected disabled>Выберите категорию...</option>';
    allCategories.forEach(category => {
        if (category.name === place_category) {
            content += `<option value="${escapeHtml(category.id)}" selected>${escapeHtml(category.name)}</option>`;
        } else {
            content += `<option value="${escapeHtml(category.id)}">${escapeHtml(category.name)}</option>`;
        }
    });
    content += '</select>';
    content += '</p>';

    content += '<p class="text-sm mt-2 flex items-center gap-2">';
    content += toggleSwitchHtml('form-is-visited', 'is_visited', false, '');
    content += '<label for="form-is-visited" class="cursor-pointer"><span class="font-semibold text-gray-900 dark:text-white">Посещено</span></label>';
    content += '</p>';

    content += '<p id="place-collection-dropdown-wrap" class="text-sm mt-2 min-h-[4.5rem]">';
    content += '<span class="font-semibold text-gray-900 dark:text-white">Коллекция:</span> ';
    content += `<select name="collection" id="form-collection" class="mt-1 ${FORM_INPUT_CLASS}">`;
    content += '<option value="">Без коллекции</option>';
    allPlaceCollections.forEach(coll => {
        content += `<option value="${escapeHtml(coll.id)}">${escapeHtml(coll.title)}</option>`;
    });
    content += '</select>';
    content += '</p>';
    content += '<p id="place-new-collection-wrap" class="text-sm mt-2 hidden min-h-[4.5rem]">';
    content += '<span class="font-semibold text-gray-900 dark:text-white">Название новой коллекции:</span> ';
    content += `<input type="text" id="form-new-collection-title" name="new_collection_title" placeholder="Введите название" class="mt-1 ${FORM_INPUT_PLACEHOLDER_CLASS}">`;
    content += '</p>';
    content += '<p class="text-sm mt-2 flex items-center gap-2">';
    content += toggleSwitchHtml('form-add-new-collection', 'add_new_collection', false, ' onchange="toggleNewCollectionField(this)"');
    content += '<label for="form-add-new-collection" class="cursor-pointer"><span class="font-semibold text-gray-900 dark:text-white">Добавить новую коллекцию</span></label>';
    content += '</p>';
    content += '</div>';

    return content;
}

function generatePopupContent(place) {
    const name = place.name ?? '';
    const place_category = place.category_detail?.name;
    const is_visited = place.is_visited === true;
    const collection_title = place.collection_detail?.title || null;

    let content = '';
    content += `<div class="w-full" style="min-width: ${POPUP_WIDTH}px;">`;
    content += '<div class="text-lg">';
    content += `<div id="place_name_text">${escapeHtml(name)}</div>`;
    content += '<div id="place_name_input_form" class="hidden w-full">';
    content += `<input type="text" id="form-name" name="name" value="${escapeHtml(name)}" class="${FORM_INPUT_CLASS}">`;
    content += '</div>';
    content += '</div>';

    content += '<p class="text-sm text-gray-600 dark:text-neutral-400">';
    content += `<span class="font-semibold text-gray-900 dark:text-white">Широта:</span> ${escapeHtml(place.latitude)}<br>`;
    content += `<input type="text" id="form-latitude" name="latitude" value="${escapeHtml(place.latitude)}" hidden>`;
    content += `<span class="font-semibold text-gray-900 dark:text-white">Долгота:</span> ${escapeHtml(place.longitude)}`;
    content += `<input type="text" id="form-longitude" name="longitude" value="${escapeHtml(place.longitude)}" hidden>`;
    content += '</p>';

    content += '<p id="category_select_form" class="hidden text-sm">';
    content += '<span class="font-semibold text-gray-900 dark:text-white">Категория:</span> ';
    content += `<select name="category" id="form-type-object" class="mt-1 ${FORM_INPUT_CLASS}">`;
    content += '<option value="" disabled>Выберите категорию...</option>';
    allCategories.forEach(category => {
        if (category.name === place_category) {
            content += `<option value="${escapeHtml(category.id)}" selected>${escapeHtml(category.name)}</option>`;
        } else {
            content += `<option value="${escapeHtml(category.id)}">${escapeHtml(category.name)}</option>`;
        }
    });
    content += '</select>';
    content += '</p>';

    content += '<p id="category_place" class="text-sm text-gray-600 dark:text-neutral-400">';
    content += '<span class="font-semibold text-gray-900 dark:text-white">Категория:</span> ';
    content += ` ${place_category !== undefined ? escapeHtml(place_category) : 'Не известно'}`;
    content += '</p>';

    content += '<p id="place_visited_collection_view" class="text-sm text-gray-600 dark:text-neutral-400">';
    content += '<span class="font-semibold text-gray-900 dark:text-white">Посещено:</span> ' + (is_visited ? 'да' : 'нет') + '<br>';
    content += '<span class="font-semibold text-gray-900 dark:text-white">Коллекция:</span> ' + escapeHtml(collection_title || 'Без коллекции');
    content += '</p>';

    content += '<div id="place_visited_collection_edit" class="hidden text-sm mt-2">';
    content += '<p class="flex items-center gap-2 mb-2">';
    content += toggleSwitchHtml('form-is-visited', 'is_visited', is_visited, '');
    content += '<label for="form-is-visited" class="cursor-pointer"><span class="font-semibold text-gray-900 dark:text-white">Посещено</span></label>';
    content += '</p>';
    content += '<div id="place-collection-dropdown-wrap" class="text-sm mt-2 mb-2 min-h-[4.5rem]">';
    content += '<span class="font-semibold text-gray-900 dark:text-white">Коллекция:</span> ';
    content += `<select name="collection" id="form-collection" class="mt-1 ${FORM_INPUT_CLASS}">`;
    content += '<option value="">Без коллекции</option>';
    const current_collection_id = place.collection_detail?.id ?? place.collection ?? null;
    allPlaceCollections.forEach(coll => {
        const sel = (current_collection_id && String(coll.id) === String(current_collection_id)) ? ' selected' : '';
        content += `<option value="${escapeHtml(coll.id)}"${sel}>${escapeHtml(coll.title)}</option>`;
    });
    content += '</select>';
    content += '</div>';
    content += '<div id="place-new-collection-wrap" class="text-sm mt-2 hidden min-h-[4.5rem] mb-2">';
    content += '<span class="font-semibold text-gray-900 dark:text-white">Название новой коллекции:</span> ';
    content += `<input type="text" id="form-new-collection-title" name="new_collection_title" placeholder="Введите название" class="mt-1 ${FORM_INPUT_PLACEHOLDER_CLASS}">`;
    content += '</div>';
    content += '<p class="flex items-center gap-2 mb-2">';
    content += toggleSwitchHtml('form-add-new-collection', 'add_new_collection', false, ' onchange="toggleNewCollectionField(this)"');
    content += '<label for="form-add-new-collection" class="cursor-pointer"><span class="font-semibold text-gray-900 dark:text-white">Добавить новую коллекцию</span></label>';
    content += '</p>';
    content += '</div>';
    content += '</div>';

    return content;
}

function update_place(id) {
    const btn_update_place = document.getElementById('btn-update-place');
    if (!btn_update_place || btn_update_place.classList.contains('hidden')) {
        return;
    }

    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
        });
    }

    const category_el = document.getElementById('form-type-object');
    if (!category_el) {
        return;
    }
    const category_id = category_el.value;
    const isVisitedEl = document.getElementById('form-is-visited');

    const data = {
        name: document.getElementById('form-name').value,
        category: category_id,
        is_visited: isVisitedEl ? isVisitedEl.checked : true,
        collection: null
    };

    resolveCollectionIdForPlace()
        .then(collectionId => {
            data.collection = collectionId;
            return fetch(`/api/place/update/${id}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json;charset=utf-8',
                    'X-CSRFToken': getCookie("csrftoken")
                },
                body: JSON.stringify(data)
            });
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Произошла ошибка при редактировании места');
            }
            return response.json();
        })
        .then(updated => {
            allPlaces.set(id, updated);
            updateMarkers();
            showSuccessToast('Изменено', 'Указанное Вами место успешно отредактировано');
        })
        .catch(() => {
            showDangerToast('Ошибка', 'Произошла неизвестная ошибка и отредактировать место не получилось. Пожалуйста, обновите страницу и попробуйте ещё раз');
        });
}

function delete_place(id) {
    document.querySelector('form').addEventListener('submit', function(event) {
        event.preventDefault();
    });

    fetch(`/api/place/delete/${id}`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': getCookie("csrftoken")
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Произошла ошибка при удалении');
            }
            if (response.status === 204) {
                allPlaces.delete(id);
                updateMarkers();
                showSuccessToast('Удалено', 'Указанное Вами место успешно удалено')
            } else {
                showDangerToast('Ошибка', 'Произошла неизвестная ошибка и удалить место не получилось. Пожалуйста, обновите страницу и попробуйте ещё раз');
                throw new Error('Произошла неизвестная ошибка и удалить место не получилось');
            }
        })
}

function add_place() {
    const isVisitedEl = document.getElementById('form-is-visited');
    const data = {
        name: document.getElementById('form-name').value,
        category: document.getElementById('form-type-object').value,
        is_visited: isVisitedEl ? isVisitedEl.checked : false,
        collection: null
    };

    // В зависимости от того, был перемещён маркер или нет, используются разные источники для координат
    if (moved_lat === undefined) {
        data.latitude = document.getElementById('form-latitude').value;
        data.longitude = document.getElementById('form-longitude').value;
    } else {
        data.latitude = moved_lat;
        data.longitude = moved_lon;
    }

    if (data.latitude === "" || data.longitude === "") {
        showDangerToast('Ошибка', 'Не указаны <strong>координаты</strong> объекта.<br>Странно, это поле не доступно для редактирования пользователям. Признавайтесь, вы что-то замышляете? 🧐');
        return false;
    }

    if (data.name === "" || data.category === "") {
        showDangerToast('Ошибка', 'Для добавления места необходимо указать его <strong>имя</strong> и <strong>категорию</strong>.<br>Пожалуйста, заполните соответствующие поля перед добавлением.');
        return false;
    }

    resolveCollectionIdForPlace()
        .then(collectionId => {
            data.collection = collectionId;
            return fetch('/api/place/create/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json;charset=utf-8',
                    'X-CSRFToken': getCookie("csrftoken")
                },
                body: JSON.stringify(data)
            });
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Произошла ошибка при получении данных с сервера');
            }
            return response.json();
        })
        .then(created => {
            allPlaces.set(created.id, created);
            updateMarkers();
            showSuccessToast('Добавлено', 'Указанное Вами место успешно добавлено.');
        })
        .catch(() => {
            showDangerToast('Ошибка', 'Не удалось добавить место. Проверьте название новой коллекции или попробуйте выбрать существующую.');
        });
}

/**
 * Удаляет все маркеры с карты и добавляет их заново по текущим фильтрам (категория и коллекция).
 */
function updateMarkers() {
    allMarkers.forEach(m => {
        map.removeLayer(m);
    });
    addMarkers();
}

/**
 * Добавляет на карту маркеры с учётом выбранной категории и коллекции.
 */
function addMarkers() {
    allMarkers.length = 0;
    allPlaces.forEach(place => {
        const matchCategory = selectedCategoryName === '__all__' || (place.category_detail && place.category_detail.name === selectedCategoryName);
        const matchCollection = selectedCollectionId === null ||
            (place.collection_detail && place.collection_detail.id === selectedCollectionId) ||
            (place.collection != null && Number(place.collection) === Number(selectedCollectionId));
        if (matchCategory && matchCollection) {
            const placeIcon = place.is_visited ? icon_visited_pin : icon_place_not_visited_pin;
            const marker = L.marker(
                [place.latitude, place.longitude],
                {
                    icon: placeIcon
                }).addTo(map);
            marker.bindTooltip(place.name, {direction: 'top'});
            if (!placeMapTooltipOnly) {
                marker.on('popupopen', function () {
                    this.closeTooltip();
                });
                let content = '<form id="place-form">';
                content += generatePopupContent(place);
                content += '<p class="mt-3 flex gap-2">';
                content += `<button type="button" class="py-2 px-4 inline-flex items-center justify-center gap-x-2 text-sm font-semibold rounded-lg border border-transparent bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 disabled:pointer-events-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-neutral-800" id="btn-edit-place" onclick="event.preventDefault(); switch_popup_elements(); return false;">Изменить</button>`;
                content += `<button type="button" class="hidden py-2 px-4 inline-flex items-center justify-center gap-x-2 text-sm font-semibold rounded-lg border border-transparent bg-neutral-200 text-gray-800 hover:bg-neutral-300 dark:bg-neutral-700 dark:text-neutral-200 dark:hover:bg-neutral-600 focus:outline-none focus:ring-2 focus:ring-neutral-500 focus:ring-offset-2 dark:focus:ring-offset-neutral-800" id="btn-cancel-place" onclick="event.preventDefault(); switch_popup_elements(); return false;">Отменить</button>`;
                content += `<button type="button" class="hidden py-2 px-4 inline-flex items-center justify-center gap-x-2 text-sm font-semibold rounded-lg border border-transparent bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-50 disabled:pointer-events-none focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 dark:focus:ring-offset-neutral-800" id="btn-update-place" onclick="update_place(${place.id}); return false;">Сохранить</button>`;
                content += `<button type="button" class="py-2 px-4 inline-flex items-center justify-center gap-x-2 text-sm font-semibold rounded-lg border border-transparent bg-red-600 text-white hover:bg-red-700 disabled:opacity-50 disabled:pointer-events-none focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 dark:focus:ring-offset-neutral-800" id="btn-delete-place" onclick="delete_place(${place.id}); return false;">Удалить</button>`;
                content += '</p>';
                content += '</form>';
                marker.bindPopup(content, { minWidth: POPUP_WIDTH, maxWidth: POPUP_WIDTH });
            }
            allMarkers.push(marker);
        }
    });

    updateBlockQtyPlaces(allMarkers.length);
}

function switch_popup_elements() {
    const place_name_text = document.getElementById('place_name_text');
    if (place_name_text) {
        place_name_text.classList.toggle('hidden');
    }

    const place_name_input_form = document.getElementById('place_name_input_form');
    if (place_name_input_form) {
        place_name_input_form.classList.toggle('hidden');
    }

    const category_place = document.getElementById('category_place');
    if (category_place) {
        category_place.classList.toggle('hidden');
    }

    const category_select_form = document.getElementById('category_select_form');
    if (category_select_form) {
        category_select_form.classList.toggle('hidden');
    }

    const place_visited_collection_view = document.getElementById('place_visited_collection_view');
    if (place_visited_collection_view) {
        place_visited_collection_view.classList.toggle('hidden');
    }

    const place_visited_collection_edit = document.getElementById('place_visited_collection_edit');
    if (place_visited_collection_edit) {
        place_visited_collection_edit.classList.toggle('hidden');
    }

    const btn_edit_place = document.getElementById('btn-edit-place');
    if (btn_edit_place) {
        btn_edit_place.classList.toggle('hidden');
    }

    const btn_cancel_place = document.getElementById('btn-cancel-place');
    if (btn_cancel_place) {
        btn_cancel_place.classList.toggle('hidden');
    }

    const btn_delete_place = document.getElementById('btn-delete-place');
    if (btn_delete_place) {
        btn_delete_place.classList.toggle('hidden');
    }

    const btn_update_place = document.getElementById('btn-update-place');
    if (btn_update_place) {
        btn_update_place.classList.toggle('hidden');
    }
}