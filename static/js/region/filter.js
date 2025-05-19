const btn = document.getElementById('btnOpenFilterSortPanel');
const offcanvasElement = document.getElementById('offcanvasRight');

// Нажатие кнопки "Сбросить фильтры и сортировку"
document.addEventListener('DOMContentLoaded', function () {
    const resetBtn = document.getElementById('resetFilters');

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
});

// Нажатие кнопки "Применить фильтры и сортировку"
document.getElementById('applyFilters').addEventListener('click', function () {
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

document.getElementById('btnOpenFilterSortPanel').addEventListener('click', function () {
    const tooltip = bootstrap.Tooltip.getInstance(btn);

    if (tooltip) {
        tooltip.hide();
    }
});

offcanvasElement.addEventListener('hidden.bs.offcanvas', () => {
    const tooltip = bootstrap.Tooltip.getInstance(btn);

    if (tooltip) {
        tooltip.hide(); // Включаем обратно при закрытии
        tooltip.disable(); // Блокируем автоматическое появление
        // Принудительное обновление компонента
        setTimeout(() => {
            tooltip.enable();
            tooltip.update();
        }, 50);
    }
});

// Этот костыль нужен для того, чтобы отображение и скрытие tooltip правильно
// отрабатывало при открытии и скрытии панели offcanvas
btn.addEventListener('mouseenter', () => {
    const tooltip = bootstrap.Tooltip.getInstance(btn);

    if (tooltip) {
        tooltip.hide();
        tooltip.disable();
        tooltip.enable();
        tooltip.show();
    }
});
btn.addEventListener('mouseleave', () => {
    const tooltip = bootstrap.Tooltip.getInstance(btn);

    if (tooltip) {
        tooltip.hide();
        tooltip.disable();
        tooltip.enable();
    }
});