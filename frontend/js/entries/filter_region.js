// Управление панелью фильтрации
document.addEventListener('DOMContentLoaded', function () {
    const openBtn = document.getElementById('btnOpenFilterSortPanel');
    const offcanvas = document.getElementById('offcanvasRight');
    const backdrop = document.querySelector('[data-hs-overlay-backdrop="#offcanvasRight"]');
    const closeBtn = offcanvas?.querySelector('[data-hs-overlay="#offcanvasRight"]');

    function openOffcanvas() {
        if (offcanvas && backdrop) {
            offcanvas.classList.remove('translate-x-full');
            offcanvas.classList.add('translate-x-0');
            backdrop.classList.remove('opacity-0', 'pointer-events-none');
            backdrop.classList.add('opacity-100', 'pointer-events-auto');
            document.body.style.overflow = 'hidden';
        }
    }

    function closeOffcanvas() {
        if (offcanvas && backdrop) {
            offcanvas.classList.remove('translate-x-0');
            offcanvas.classList.add('translate-x-full');
            backdrop.classList.remove('opacity-100', 'pointer-events-auto');
            backdrop.classList.add('opacity-0', 'pointer-events-none');
            document.body.style.overflow = '';
        }
    }

    if (openBtn) {
        openBtn.addEventListener('click', function(e) {
            e.preventDefault();
            openOffcanvas();
        });
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', function(e) {
            e.preventDefault();
            closeOffcanvas();
        });
    }

    if (backdrop) {
        backdrop.addEventListener('click', function() {
            closeOffcanvas();
        });
    }

    // Закрытие по Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && offcanvas?.classList.contains('translate-x-0')) {
            closeOffcanvas();
        }
    });
});

// Нажатие кнопки "Сбросить фильтры и сортировку"
document.addEventListener('DOMContentLoaded', function () {
    const resetBtn = document.getElementById('resetFilters');

    if (resetBtn) {
        resetBtn.addEventListener('click', function () {
            const filter = this.dataset.filter;
            const sort = this.dataset.sort;

            // Сброс фильтра
            if (filter || filter === "") {
                const filterInput = document.querySelector(`input[name="filter"][value="${filter}"]`);
                if (filterInput) filterInput.checked = true;
            }

            // Сброс сортировки
            if (sort) {
                const sortInput = document.querySelector(`input[name="sort"][value="${sort}"]`);
                if (sortInput) sortInput.checked = true;
            }
        });
    }
});

// Нажатие кнопки "Применить фильтры и сортировку"
document.addEventListener('DOMContentLoaded', function () {
    const applyBtn = document.getElementById('applyFilters');

    if (applyBtn) {
        applyBtn.addEventListener('click', function () {
            const filter = document.querySelector('input[name="filter"]:checked')?.value || '';
            const sort = document.querySelector('input[name="sort"]:checked')?.value || '';
            const defaultFilter = "";
            const defaultSort = "";

            // Устанавливаем filter и sort как undefined, если они совпадают с дефолтными значениями (пустая строка),
            // чтобы не помещать их в URL параметры
            const filterValue = (filter === defaultFilter) ? undefined : filter;
            const sortValue = (sort === defaultSort) ? undefined : sort;

            const params = new URLSearchParams();

            if (filterValue) params.set('filter', filterValue);
            if (sortValue) params.set('sort', sortValue);

            window.location.href = `${window.location.pathname}?${params.toString()}`;
        });
    }
});