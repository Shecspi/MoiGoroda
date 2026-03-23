/**
 * Календарь выбора даты: в поле отображается дд.мм.гггг, внутри логики — ISO YYYY-MM-DD.
 * Разметка под frontend/css/preline-datepicker-vc.css.
 */

const pickerRegistry = new WeakMap();

const WEEK_SHORT_RU = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс'];

function pad2(n) {
    return String(n).padStart(2, '0');
}

/** @returns {string} YYYY-MM-DD */
export function isoFromParts(y, monthIndex, day) {
    return `${y}-${pad2(monthIndex + 1)}-${pad2(day)}`;
}

/** Отображение в поле ввода (дд.мм.гггг) */
export function isoToRuDisplay(iso) {
    if (!iso || !/^\d{4}-\d{2}-\d{2}$/.test(iso)) {
        return '';
    }
    const [y, m, d] = iso.split('-');
    return `${d}.${m}.${y}`;
}

/** Разбор значения из поля: поддерживаются дд.мм.гггг и устаревший ГГГГ-ММ-ДД */
export function valueFromInputToIso(raw) {
    const v = typeof raw === 'string' ? raw.trim() : '';
    if (!v) {
        return null;
    }
    if (/^\d{4}-\d{2}-\d{2}$/.test(v)) {
        return v;
    }
    const m = /^(\d{2})\.(\d{2})\.(\d{4})$/.exec(v);
    if (!m) {
        return null;
    }
    const d = Number(m[1]);
    const mo = Number(m[2]);
    const y = Number(m[3]);
    if (mo < 1 || mo > 12 || d < 1 || d > 31) {
        return null;
    }
    const dt = new Date(y, mo - 1, d);
    if (dt.getFullYear() !== y || dt.getMonth() !== mo - 1 || dt.getDate() !== d) {
        return null;
    }
    return isoFromParts(y, mo - 1, d);
}

function parseIsoLocal(iso) {
    if (!iso || !/^\d{4}-\d{2}-\d{2}$/.test(iso)) {
        return null;
    }
    const [y, m, d] = iso.split('-').map(Number);
    return new Date(y, m - 1, d);
}

/** Выравнивает отображаемый месяц календаря под датой (или текущий месяц, если даты нет). */
function syncPickerViewToIso(inst, iso) {
    if (!iso) {
        const now = new Date();
        inst.viewYear = now.getFullYear();
        inst.viewMonth = now.getMonth();
        return;
    }
    const p = parseIsoLocal(iso);
    if (p) {
        inst.viewYear = p.getFullYear();
        inst.viewMonth = p.getMonth();
    }
}

function todayIsoLocal() {
    const t = new Date();
    return isoFromParts(t.getFullYear(), t.getMonth(), t.getDate());
}

function monthTitleRu(year, monthIndex) {
    const d = new Date(year, monthIndex, 1);
    return new Intl.DateTimeFormat('ru-RU', { month: 'long', year: 'numeric' }).format(d);
}

function daysInMonth(year, monthIndex) {
    return new Date(year, monthIndex + 1, 0).getDate();
}

/** Понедельник = 0 … воскресенье = 6 */
function weekdayMondayFirst(date) {
    const wd = date.getDay();
    return (wd + 6) % 7;
}

/**
 * @param {HTMLInputElement} input
 * @param {string} [iso]
 */
export function setVisitDateInputValue(inputOrSelector, iso) {
    const input =
        typeof inputOrSelector === 'string'
            ? document.querySelector(inputOrSelector)
            : inputOrSelector;
    if (!input) {
        return;
    }
    const trimmed = (iso || '').trim();
    const normalizedIso = trimmed && /^\d{4}-\d{2}-\d{2}$/.test(trimmed) ? trimmed : '';
    input.value = normalizedIso ? isoToRuDisplay(normalizedIso) : '';
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.dispatchEvent(new Event('change', { bubbles: true }));
    const inst = pickerRegistry.get(input);
    if (inst) {
        inst.selectedIso = normalizedIso || null;
        syncPickerViewToIso(inst, normalizedIso);
        if (inst.panel && !inst.panel.hasAttribute('data-vc-calendar-hidden')) {
            inst.render();
        }
    }
}

/**
 * @param {HTMLInputElement} input
 */
export function clearVisitDateInput(inputOrSelector) {
    setVisitDateInputValue(inputOrSelector, '');
}

class VisitDatePickerController {
    /**
     * @param {HTMLInputElement} input
     */
    constructor(input) {
        this.input = input;
        this.minIso = input.getAttribute('data-visit-date-min') || '1900-01-01';
        this.maxIso = input.getAttribute('data-visit-date-max') || '2470-12-31';

        this._suppressNextClickToggle = false;

        const v = this.input.value.trim();
        this.selectedIso = valueFromInputToIso(v);
        if (this.selectedIso) {
            this.input.value = isoToRuDisplay(this.selectedIso);
        }

        const now = new Date();
        if (this.selectedIso) {
            const p = parseIsoLocal(this.selectedIso);
            if (p) {
                this.viewYear = p.getFullYear();
                this.viewMonth = p.getMonth();
            } else {
                this.viewYear = now.getFullYear();
                this.viewMonth = now.getMonth();
            }
        } else {
            this.viewYear = now.getFullYear();
            this.viewMonth = now.getMonth();
        }

        this.panel = null;
        this._docCapture = null;
        this._onKey = null;

        this._onPanelMouseDown = (e) => {
            e.stopPropagation();
        };

        this._onInputFocus = () => {
            if (!this.panel || this.panel.hasAttribute('data-vc-calendar-hidden')) {
                this.open();
                this._suppressNextClickToggle = true;
            }
        };
        this._onInputClick = (e) => {
            e.preventDefault();
            if (this._suppressNextClickToggle) {
                this._suppressNextClickToggle = false;
                return;
            }
            this.toggle();
        };
        this._onInputValue = () => {
            this.selectedIso = valueFromInputToIso(this.input.value);
            if (this.selectedIso) {
                syncPickerViewToIso(this, this.selectedIso);
            }
            if (this.panel && !this.panel.hasAttribute('data-vc-calendar-hidden')) {
                this.render();
            }
        };
        this.input.addEventListener('click', this._onInputClick);
        this.input.addEventListener('focus', this._onInputFocus);
        this.input.addEventListener('input', this._onInputValue);

        pickerRegistry.set(input, this);
    }

    toggle() {
        if (this.panel && !this.panel.hasAttribute('data-vc-calendar-hidden')) {
            this.close();
        } else {
            this.open();
        }
    }

    open() {
        if (!this.panel) {
            this.panel = document.createElement('div');
            this.panel.className = 'vc';
            this.panel.setAttribute('data-vc', 'calendar');
            this.panel.setAttribute('data-vc-type', 'default');
            this.panel.setAttribute('data-vc-input', '');
            this.panel.setAttribute('role', 'dialog');
            this.panel.setAttribute('aria-modal', 'true');
            document.body.appendChild(this.panel);
            this.panel.addEventListener('mousedown', this._onPanelMouseDown, true);
        }
        this.panel.removeAttribute('data-vc-calendar-hidden');
        if (this.selectedIso) {
            syncPickerViewToIso(this, this.selectedIso);
        }
        this.render();
        this.place();
        this.attachGlobalClose();
    }

    close() {
        if (this.panel) {
            this.panel.setAttribute('data-vc-calendar-hidden', '');
        }
        this.detachGlobalClose();
    }

    place() {
        if (!this.panel) {
            return;
        }
        const r = this.input.getBoundingClientRect();
        const gap = 4;
        let top = r.bottom + gap + window.scrollY;
        let left = r.left + window.scrollX;
        const pw = this.panel.offsetWidth || 280;
        const ph = this.panel.offsetHeight || 320;
        if (left + pw > window.scrollX + document.documentElement.clientWidth - 8) {
            left = window.scrollX + document.documentElement.clientWidth - pw - 8;
        }
        if (left < window.scrollX + 8) {
            left = window.scrollX + 8;
        }
        if (r.bottom + gap + ph > window.innerHeight && r.top > ph + gap) {
            top = r.top + window.scrollY - ph - gap;
        }
        this.panel.style.position = 'absolute';
        this.panel.style.top = `${top}px`;
        this.panel.style.left = `${left}px`;
    }

    attachGlobalClose() {
        this.detachGlobalClose();
        this._docCapture = (ev) => {
            const t = ev.target;
            if (t === this.input || this.panel.contains(t)) {
                return;
            }
            this.close();
        };
        document.addEventListener('mousedown', this._docCapture, true);
        this._onKey = (ev) => {
            if (ev.key === 'Escape') {
                this.close();
            }
        };
        document.addEventListener('keydown', this._onKey, true);
        this._onResizeOrScroll = () => this.place();
        window.addEventListener('resize', this._onResizeOrScroll);
        window.addEventListener('scroll', this._onResizeOrScroll, true);
    }

    detachGlobalClose() {
        if (this._docCapture) {
            document.removeEventListener('mousedown', this._docCapture, true);
            this._docCapture = null;
        }
        if (this._onKey) {
            document.removeEventListener('keydown', this._onKey, true);
            this._onKey = null;
        }
        if (this._onResizeOrScroll) {
            window.removeEventListener('resize', this._onResizeOrScroll);
            window.removeEventListener('scroll', this._onResizeOrScroll, true);
            this._onResizeOrScroll = null;
        }
    }

    isDateAllowed(iso) {
        return iso >= this.minIso && iso <= this.maxIso;
    }

    render() {
        if (!this.panel) {
            return;
        }
        const y = this.viewYear;
        const m = this.viewMonth;
        const first = new Date(y, m, 1);
        const startCol = weekdayMondayFirst(first);
        const dim = daysInMonth(y, m);
        const prevMonth = m === 0 ? 11 : m - 1;
        const prevYear = m === 0 ? y - 1 : y;
        const prevDim = daysInMonth(prevYear, prevMonth);
        const nextMonth = m === 11 ? 0 : m + 1;
        const nextYear = m === 11 ? y + 1 : y;

        const today = todayIsoLocal();

        const cells = [];

        for (let i = 0; i < startCol; i++) {
            const dayNum = prevDim - startCol + i + 1;
            const iso = isoFromParts(prevYear, prevMonth, dayNum);
            cells.push({ iso, month: 'prev', inRange: this.isDateAllowed(iso) });
        }
        for (let d = 1; d <= dim; d++) {
            const iso = isoFromParts(y, m, d);
            cells.push({ iso, month: 'current', inRange: this.isDateAllowed(iso) });
        }
        const tail = (7 - (cells.length % 7)) % 7;
        for (let d = 1; d <= tail; d++) {
            const iso = isoFromParts(nextYear, nextMonth, d);
            cells.push({ iso, month: 'next', inRange: this.isDateAllowed(iso) });
        }

        const header = `
      <div class="flex items-center justify-between gap-2 mb-3">
        <button type="button" class="vc-arrow vc-arrow_prev" data-act="prev" aria-label="Предыдущий месяц">
          <svg class="size-4 shrink-0" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m15 18-6-6 6-6"/></svg>
        </button>
        <span class="vc-month text-sm font-semibold">${monthTitleRu(y, m)}</span>
        <button type="button" class="vc-arrow vc-arrow_next" data-act="next" aria-label="Следующий месяц">
          <svg class="size-4 shrink-0" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m9 18 6-6-6-6"/></svg>
        </button>
      </div>`;

        const weekRow = `<div class="vc-week" role="row">
      ${WEEK_SHORT_RU.map((w) => `<span class="vc-week__day">${w}</span>`).join('')}
    </div>`;

        let datesHtml = '<div class="vc-dates grid grid-cols-7 gap-y-0.5" role="grid">';
        for (const cell of cells) {
            const sel = this.selectedIso === cell.iso;
            const isToday = cell.iso === today;
            const attrs = [`data-vc-date="${cell.iso}"`, `data-vc-date-month="${cell.month}"`];
            if (isToday) {
                attrs.push('data-vc-date-today');
            }
            if (sel) {
                attrs.push('data-vc-date-selected');
            }
            const disabled = !cell.inRange;
            const dayNum = Number(cell.iso.slice(8, 10));
            const btn = disabled
                ? `<span class="vc-date__btn opacity-40 cursor-not-allowed flex items-center justify-center" aria-disabled="true">${dayNum}</span>`
                : `<button type="button" class="vc-date__btn" data-vc-date-btn aria-label="${cell.iso}">${dayNum}</button>`;
            datesHtml += `<div class="vc-date" ${attrs.join(' ')}>${btn}</div>`;
        }
        datesHtml += '</div>';

        this.panel.innerHTML = header + weekRow + datesHtml;

        this.panel.querySelector('[data-act="prev"]')?.addEventListener('click', (e) => {
            e.stopPropagation();
            if (this.viewMonth === 0) {
                this.viewMonth = 11;
                this.viewYear -= 1;
            } else {
                this.viewMonth -= 1;
            }
            this.render();
            this.place();
        });
        this.panel.querySelector('[data-act="next"]')?.addEventListener('click', (e) => {
            e.stopPropagation();
            if (this.viewMonth === 11) {
                this.viewMonth = 0;
                this.viewYear += 1;
            } else {
                this.viewMonth += 1;
            }
            this.render();
            this.place();
        });

        this.panel.querySelectorAll('button[data-vc-date-btn]').forEach((btn) => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const cell = btn.closest('.vc-date');
                const iso = cell?.getAttribute('data-vc-date');
                if (!iso || !this.isDateAllowed(iso)) {
                    return;
                }
                this.selectedIso = iso;
                setVisitDateInputValue(this.input, iso);
                this.close();
            });
        });
    }

    destroy() {
        this.detachGlobalClose();
        this.input.removeEventListener('click', this._onInputClick);
        this.input.removeEventListener('focus', this._onInputFocus);
        this.input.removeEventListener('input', this._onInputValue);
        if (this.panel) {
            this.panel.removeEventListener('mousedown', this._onPanelMouseDown, true);
            this.panel.remove();
        }
        this.panel = null;
        pickerRegistry.delete(this.input);
    }
}

/**
 * @param {ParentNode} [root]
 */
export function initVisitDatePickers(root = document) {
    root.querySelectorAll('input[data-visit-date-picker]').forEach((el) => {
        if (!(el instanceof HTMLInputElement) || pickerRegistry.has(el)) {
            return;
        }
        new VisitDatePickerController(el);
    });
}
