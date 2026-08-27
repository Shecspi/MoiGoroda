// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('vanilla-calendar-pro', () => ({
    Calendar: vi.fn().mockImplementation(function Calendar(element, options) {
        this.element = element;
        this.options = options;
        this.context = {selectedDates: options.selectedDates || []};
        this.init = vi.fn();
        this.set = vi.fn((settings) => {
            this.context.selectedDates = settings.selectedDates || [];
        });
        this.hide = vi.fn();
        this.destroy = vi.fn();
    }),
}));

vi.mock('../../js/components/get_cookie.js', () => ({
    getCookie: vi.fn(() => 'csrf-token'),
}));

vi.mock('../../js/components/toast.js', () => ({
    showDangerToast: vi.fn(),
    showSuccessToast: vi.fn(),
}));

import { Calendar } from 'vanilla-calendar-pro';
import { showSuccessToast } from '../../js/components/toast.js';
import AddCityModal from './add-city-modal.js';

const modalTemplate = `
    <template id="add-city-modal-template">
        <dialog>
            <div class="dui-modal-box">
                <h3 id="addCityModalLabel">Добавить посещённый город</h3>
                <form id="form-add-city">
                <div id="add-city-modal-content">
                    <div id="city-selection-fields" hidden>
                        <button type="button" data-city-search-back hidden>Назад</button>
                        <div data-city-combobox>
                            <div data-city-combobox-control>
                                <input id="add-city-city" data-city-combobox-input>
                                <span data-city-combobox-loading hidden></span>
                            </div>
                            <p data-city-search-instruction>Начните вводить название города</p>
                            <div data-city-combobox-positioner>
                                <ul data-city-combobox-content></ul>
                            </div>
                        </div>
                    </div>
                    <div id="visit-details">
                        <div id="city-summary-card">
                            <h4 id="city-title-in-modal"></h4>
                            <p id="region-title-in-modal"></p>
                            <button type="button" data-change-city hidden>Изменить</button>
                        </div>
                        <input id="date-of-visit" name="date_of_visit" readonly>
                        <div id="add-city-visit-calendar" class="vc absolute top-full start-0 z-10 w-fit mt-2" data-vc-calendar-hidden></div>
                        <button type="button" id="today-button"></button>
                        <button type="button" id="yesterday-button"></button>
                        <input id="id_rating" name="rating">
                        <input type="checkbox" id="magnet-checkbox" name="has_magnet">
                        <textarea id="impression" name="impression"></textarea>
                        <div id="rating-container"><input type="radio" value="1"></div>
                    </div>
                </div>
                <div id="add-city-modal-actions">
                    <button type="button" id="btn-close-modal"></button>
                    <button id="btn_add-visited-city"><span>Добавить</span></button>
                </div>
                <input type="hidden" id="city-id" name="city" value="42">
                </form>
            </div>
        </dialog>
    </template>`;

describe('AddCityModal visit calendar', () => {
    beforeEach(() => {
        document.body.innerHTML = modalTemplate;
        Calendar.mockClear();
        showSuccessToast.mockClear();
        vi.stubGlobal('fetch', vi.fn());
        vi.stubGlobal('innerWidth', 1024);
    });

    afterEach(() => {
        document.body.innerHTML = '';
        vi.unstubAllGlobals();
        vi.useRealTimers();
    });

    it('registers one opening handler only while connected across reconnect', () => {
        const modal = new AddCityModal();
        document.body.appendChild(modal);
        const open = vi.spyOn(modal, 'open').mockImplementation(() => {});
        const trigger = document.createElement('button');
        trigger.dataset.action = 'add-city';
        trigger.dataset.cityId = '42';
        trigger.dataset.cityName = 'Тверь';
        trigger.dataset.cityCountryName = 'Россия';
        document.body.appendChild(trigger);

        modal.remove();
        trigger.click();
        expect(open).not.toHaveBeenCalled();

        document.body.appendChild(modal);
        trigger.click();
        expect(open).toHaveBeenCalledOnce();
        expect(open).toHaveBeenCalledWith({
            cityId: 42,
            cityName: 'Тверь',
            regionName: '',
            countryName: 'Россия',
        });
    });

    it('opens the city-selection create mode when an add trigger has no city data', () => {
        const modal = new AddCityModal();
        document.body.appendChild(modal);
        const open = vi.spyOn(modal, 'open').mockImplementation(() => {});
        const trigger = document.createElement('button');
        trigger.dataset.action = 'add-city';
        trigger.dataset.surface = 'sidebar';
        document.body.appendChild(trigger);

        trigger.click();

        expect(open).toHaveBeenCalledWith({
            cityId: null,
            cityName: '',
            regionName: '',
            countryName: '',
            surface: 'sidebar',
        });
    });

    it('uses only global city search and invalidates a changed selection', async () => {
        fetch.mockResolvedValue({
            ok: true,
            json: vi.fn().mockResolvedValue([
                {id: 42, title: 'Ю', region: 'Штат Юта', country: 'США'},
            ]),
        });
        const modal = new AddCityModal();
        document.body.appendChild(modal);
        modal.querySelector('dialog').showModal = vi.fn();

        modal.open({cityId: null});

        expect(modal.querySelector('[data-city-country]')).toBeNull();
        expect(modal.querySelector('[data-city-region]')).toBeNull();
        const input = modal.querySelector('[data-city-combobox-input]');
        input.value = 'Ю';
        input.dispatchEvent(new Event('input', {bubbles: true}));
        await vi.waitFor(() => expect(modal.querySelector('[role="option"]')).not.toBeNull());
        expect(fetch).toHaveBeenCalledOnce();
        expect(fetch.mock.calls[0][0]).toBe('/api/city/search?query=%D0%AE');

        modal.querySelector('[role="option"]').click();
        await vi.waitFor(() => expect(modal.cityId).toBe(42));
        expect(modal.querySelector('#city-id').value).toBe('42');

        input.value = 'Юг';
        input.dispatchEvent(new Event('input', {bubbles: true}));
        expect(modal.cityId).toBeNull();
        expect(modal.querySelector('#city-id').value).toBe('');
    });

    it.each([
        ['region and country', 'Тверская область', 'Россия', 'Тверская область, Россия', false],
        ['country only', '', 'Россия', 'Россия', false],
        ['no location metadata', '', '', '', true],
    ])('renders a predetermined create summary with %s', (
        _caseName, regionName, countryName, expectedLocation, locationHidden,
    ) => {
        const modal = new AddCityModal();
        document.body.appendChild(modal);
        modal.querySelector('dialog').showModal = vi.fn();

        modal.open({cityId: 42, cityName: 'Тверь', regionName, countryName});

        expect(modal.querySelector('#city-title-in-modal').textContent).toBe('Тверь');
        const location = modal.querySelector('#region-title-in-modal');
        expect(location.textContent).toBe(expectedLocation);
        expect(location.hidden).toBe(locationHidden);
    });

    it.each([
        ['region and country', 'Тверская область', 'Россия', 'Тверская область, Россия', false],
        ['country only', null, 'Россия', 'Россия', false],
        ['no location metadata', null, null, '', true],
    ])('renders an edit summary with %s', async (
        _caseName, regionTitle, country, expectedLocation, locationHidden,
    ) => {
        fetch.mockResolvedValue({
            ok: true,
            json: vi.fn().mockResolvedValue({
                visit: {
                    id: 17,
                    city: 42,
                    city_title: 'Тверь',
                    region_title: regionTitle,
                    country,
                    date_of_visit: null,
                    has_magnet: false,
                    rating: 4,
                    impression: '',
                },
            }),
        });
        const modal = new AddCityModal();
        document.body.appendChild(modal);
        modal.querySelector('dialog').showModal = vi.fn();

        await modal.openEdit(17);

        expect(modal.querySelector('#city-title-in-modal').textContent).toBe('Тверь');
        const location = modal.querySelector('#region-title-in-modal');
        expect(location.textContent).toBe(expectedLocation);
        expect(location.hidden).toBe(locationHidden);
    });

    it('loads an existing visit into read-only-city edit mode', async () => {
        const modal = new AddCityModal();
        document.body.appendChild(modal);
        const dialog = modal.querySelector('dialog');
        dialog.showModal = vi.fn();
        fetch.mockResolvedValue({
            ok: true,
            json: vi.fn().mockResolvedValue({
                visit: {
                    id: 17,
                    city: 42,
                    city_title: 'Тверь',
                    region_title: 'Тверская область',
                    date_of_visit: '2026-08-05',
                    has_magnet: true,
                    rating: 4,
                    impression: 'Набережная',
                },
            }),
        });

        await modal.openEdit(17);

        expect(fetch).toHaveBeenCalledWith('/api/city/visited/17/');
        expect(modal.querySelector('#city-title-in-modal').textContent).toBe('Тверь');
        expect(modal.querySelector('#city-id').value).toBe('42');
        expect(modal.querySelector('#date-of-visit').value).toBe('05.08.2026');
        expect(modal.querySelector('#magnet-checkbox').checked).toBe(true);
        expect(modal.querySelector('#id_rating').value).toBe('4');
        expect(modal.querySelector('#impression').value).toBe('Набережная');
        expect(modal.querySelector('#city-selection-fields').hidden).toBe(true);
        expect(modal.querySelector('#btn_add-visited-city span').textContent).toBe('Сохранить');
    });

    it('focuses the dialog instead of the visit date when edit mode opens', async () => {
        const modal = new AddCityModal();
        document.body.appendChild(modal);
        const dialog = modal.querySelector('dialog');
        const dateInput = modal.querySelector('#date-of-visit');
        const calendarElement = modal.querySelector('#add-city-visit-calendar');
        dialog.showModal = vi.fn(() => {
            dialog.open = true;
            (dialog.hasAttribute('autofocus') ? dialog : dateInput).focus();
        });
        fetch.mockResolvedValue({
            ok: true,
            json: vi.fn().mockResolvedValue({
                visit: {
                    id: 17,
                    city: 42,
                    city_title: 'Тверь',
                    region_title: 'Тверская область',
                    date_of_visit: '2026-08-05',
                    has_magnet: false,
                    rating: 4,
                    impression: '',
                },
            }),
        });

        await modal.openEdit(17);

        expect(dialog.hasAttribute('autofocus')).toBe(true);
        expect(document.activeElement).toBe(dialog);
        expect(modal.querySelector('form').contains(document.activeElement)).toBe(false);
        expect(calendarElement.hasAttribute('data-vc-calendar-hidden')).toBe(true);
    });

    it('opens edit mode from a delegated visit trigger', () => {
        const modal = new AddCityModal();
        document.body.appendChild(modal);
        const openEdit = vi.spyOn(modal, 'openEdit').mockResolvedValue();
        const trigger = document.createElement('button');
        trigger.dataset.action = 'edit-visited-city';
        trigger.dataset.visitedCityId = '17';
        document.body.appendChild(trigger);

        trigger.click();

        expect(openEdit).toHaveBeenCalledWith(17);
    });

    it('syncs a clicked calendar date to the readonly input and redraws it', () => {
        const modal = new AddCityModal();
        document.body.appendChild(modal);

        const dateInput = modal.querySelector('#date-of-visit');
        const calendar = Calendar.mock.instances[0];
        const calendarOptions = Calendar.mock.calls[0][1];

        expect(dateInput.readOnly).toBe(true);
        expect(calendar.element).toBe(modal.querySelector('#add-city-visit-calendar'));
        expect(calendarOptions.inputMode).toBeUndefined();
        expect(calendarOptions.selectionDatesMode).toBe('single');
        expect(calendarOptions.locale).toBe('ru-RU');
        expect(calendarOptions.enableDateToggle).toBe(false);
        expect(calendarOptions.styles.calendar).not.toContain('hidden!');

        calendar.context.selectedDates = ['2026-08-05'];
        calendarOptions.onClickDate(calendar);
        expect(dateInput.value).toBe('05.08.2026');
        expect(calendar.context.selectedDates).toEqual(['2026-08-05']);
        expect(calendar.set).toHaveBeenCalledWith({selectedDates: ['2026-08-05']}, {dates: true});
    });

    it('does not limit available years', () => {
        const modal = new AddCityModal();
        document.body.appendChild(modal);
        const calendarOptions = Calendar.mock.calls[0][1];

        expect(calendarOptions.dateMax).toBeUndefined();
    });

    it('shows the calendar when the date input is clicked or focused', () => {
        const modal = new AddCityModal();
        document.body.appendChild(modal);
        const dateInput = modal.querySelector('#date-of-visit');
        const calendarElement = modal.querySelector('#add-city-visit-calendar');

        expect(calendarElement.hasAttribute('data-vc-calendar-hidden')).toBe(true);
        dateInput.focus();
        expect(calendarElement.hasAttribute('data-vc-calendar-hidden')).toBe(false);

        modal.hideVisitCalendar();
        dateInput.click();
        expect(calendarElement.hasAttribute('data-vc-calendar-hidden')).toBe(false);
    });

    it('hides the calendar when a click lands outside its input and popup', () => {
        const modal = new AddCityModal();
        document.body.appendChild(modal);
        const dateInput = modal.querySelector('#date-of-visit');
        const calendarElement = modal.querySelector('#add-city-visit-calendar');

        dateInput.click();
        expect(calendarElement.classList).not.toContain('hidden!');

        document.body.click();

        expect(calendarElement.hasAttribute('data-vc-calendar-hidden')).toBe(true);
    });

    it('keeps the calendar open when its year title rebuilds during a click', () => {
        const modal = new AddCityModal();
        document.body.appendChild(modal);
        const dateInput = modal.querySelector('#date-of-visit');
        const calendarElement = modal.querySelector('#add-city-visit-calendar');
        calendarElement.innerHTML = '<button type="button" id="calendar-year">2026</button>';
        const yearButton = calendarElement.querySelector('#calendar-year');

        dateInput.click();
        yearButton.addEventListener('click', () => yearButton.remove());
        yearButton.click();

        expect(calendarElement.hasAttribute('data-vc-calendar-hidden')).toBe(false);
    });

    it('does not focus a form field or open the calendar when a preselected city dialog opens', () => {
        const modal = new AddCityModal();
        document.body.appendChild(modal);
        const dialog = modal.querySelector('dialog');
        const dateInput = modal.querySelector('#date-of-visit');
        const calendarElement = modal.querySelector('#add-city-visit-calendar');
        dialog.showModal = vi.fn(() => {
            dialog.open = true;
            (dialog.hasAttribute('autofocus') ? dialog : dateInput).focus();
        });

        modal.open({cityId: 42, cityName: 'Тверь', regionName: 'Тверская область'});

        expect(dialog.showModal).toHaveBeenCalledOnce();
        expect(dialog.hasAttribute('autofocus')).toBe(true);
        expect(document.activeElement).toBe(dialog);
        expect(modal.querySelector('form').contains(document.activeElement)).toBe(false);
        expect(calendarElement.hasAttribute('data-vc-calendar-hidden')).toBe(true);
    });

    it('moves focus to the city search when city selection dialog opens', () => {
        const modal = new AddCityModal();
        document.body.appendChild(modal);
        const dialog = modal.querySelector('dialog');
        const cityInput = modal.querySelector('#add-city-city');
        dialog.showModal = vi.fn();

        modal.open({cityId: null});

        expect(dialog.showModal).toHaveBeenCalledOnce();
        expect(document.activeElement).toBe(cityInput);
    });

    it('opens a dedicated city search before the mobile keyboard appears', () => {
        vi.stubGlobal('innerWidth', 767);
        const modal = new AddCityModal();
        document.body.appendChild(modal);
        const dialog = modal.querySelector('dialog');
        const cityInput = modal.querySelector('#add-city-city');
        dialog.showModal = vi.fn();

        modal.open({cityId: null});

        expect(modal.querySelector('#addCityModalLabel').textContent).toBe('Выберите город');
        expect(modal.querySelector('#city-selection-fields').hidden).toBe(false);
        expect(modal.querySelector('[data-city-search-instruction]').hidden).toBe(false);
        expect(modal.querySelector('#visit-details').hidden).toBe(true);
        expect(modal.querySelector('#add-city-modal-actions').hidden).toBe(true);
        expect(document.activeElement).toBe(cityInput);
    });

    it('switches the create flow when the viewport crosses the mobile boundary', () => {
        vi.stubGlobal('innerWidth', 768);
        const modal = new AddCityModal();
        document.body.appendChild(modal);
        const dialog = modal.querySelector('dialog');
        dialog.showModal = vi.fn(() => {
            dialog.open = true;
        });

        modal.open({cityId: null});
        expect(modal.querySelector('#addCityModalLabel').textContent).toBe('Добавить посещённый город');
        expect(modal.querySelector('#visit-details').hidden).toBe(false);

        vi.stubGlobal('innerWidth', 767);
        window.dispatchEvent(new Event('resize'));
        expect(modal.querySelector('#addCityModalLabel').textContent).toBe('Выберите город');
        expect(modal.querySelector('#visit-details').hidden).toBe(true);

        vi.stubGlobal('innerWidth', 768);
        window.dispatchEvent(new Event('resize'));
        expect(modal.querySelector('#addCityModalLabel').textContent).toBe('Добавить посещённый город');
        expect(modal.querySelector('#visit-details').hidden).toBe(false);
        expect(modal.querySelector('#add-city-modal-actions').hidden).toBe(false);
    });

    it('moves from mobile city search to visit details after a result is selected', async () => {
        vi.stubGlobal('innerWidth', 767);
        fetch.mockResolvedValue({
            ok: true,
            json: vi.fn().mockResolvedValue([
                {id: 42, title: 'Тверь', region: 'Тверская область', country: 'Россия'},
            ]),
        });
        const modal = new AddCityModal();
        document.body.appendChild(modal);
        modal.querySelector('dialog').showModal = vi.fn();

        modal.open({cityId: null});
        const input = modal.querySelector('[data-city-combobox-input]');
        input.value = 'Тверь';
        input.dispatchEvent(new Event('input', {bubbles: true}));

        expect(modal.querySelector('[data-city-search-instruction]').hidden).toBe(true);
        await vi.waitFor(() => expect(modal.querySelector('[role="option"]')).not.toBeNull());
        modal.querySelector('[role="option"]').click();

        await vi.waitFor(() => expect(modal.cityId).toBe(42));
        expect(modal.querySelector('#city-id').value).toBe('42');
        expect(modal.querySelector('#city-title-in-modal').textContent).toBe('Тверь');
        expect(modal.querySelector('#region-title-in-modal').textContent).toBe('Тверская область, Россия');
        expect(modal.querySelector('#addCityModalLabel').textContent).toBe('Добавить посещённый город');
        expect(modal.querySelector('#city-selection-fields').hidden).toBe(true);
        expect(modal.querySelector('#visit-details').hidden).toBe(false);
        expect(modal.querySelector('#add-city-modal-actions').hidden).toBe(false);
        await vi.waitFor(() => expect(document.activeElement).not.toBe(input));
        expect(modal.querySelector('form').contains(document.activeElement)).toBe(false);
    });

    it('returns to the previous mobile city after cancelling a replacement search', async () => {
        vi.stubGlobal('innerWidth', 767);
        const modal = new AddCityModal();
        document.body.appendChild(modal);
        modal.querySelector('dialog').showModal = vi.fn();

        modal.open({
            cityId: 42,
            cityName: 'Тверь',
            regionName: 'Тверская область',
            countryName: 'Россия',
        });
        const changeButton = modal.querySelector('[data-change-city]');
        expect(changeButton.hidden).toBe(false);

        changeButton.click();
        const input = modal.querySelector('[data-city-combobox-input]');
        expect(modal.querySelector('#addCityModalLabel').textContent).toBe('Выберите город');
        expect(modal.querySelector('[data-city-search-back]').hidden).toBe(false);
        expect(modal.querySelector('#visit-details').hidden).toBe(true);
        expect(input.value).toBe('Тверь');
        expect(modal.querySelector('[data-city-search-instruction]').hidden).toBe(true);
        expect(document.activeElement).toBe(input);
        expect(input.selectionStart).toBe(0);
        expect(input.selectionEnd).toBe('Тверь'.length);

        input.value = 'Твер';
        input.dispatchEvent(new Event('input', {bubbles: true}));
        expect(modal.cityId).toBe(42);
        modal.querySelector('[data-city-search-back]').click();

        expect(modal.cityId).toBe(42);
        expect(modal.querySelector('#city-id').value).toBe('42');
        expect(modal.querySelector('#city-title-in-modal').textContent).toBe('Тверь');
        expect(modal.querySelector('#region-title-in-modal').textContent).toBe('Тверская область, Россия');
        expect(modal.querySelector('#visit-details').hidden).toBe(false);
        expect(modal.querySelector('#city-selection-fields').hidden).toBe(true);
        await vi.waitFor(() => expect(document.activeElement).not.toBe(input));
        expect(modal.querySelector('form').contains(document.activeElement)).toBe(false);
    });

    it('commits a replacement selected from the mobile city search', async () => {
        vi.stubGlobal('innerWidth', 767);
        fetch.mockResolvedValue({
            ok: true,
            json: vi.fn().mockResolvedValue([
                {id: 77, title: 'Ржев', region: 'Тверская область', country: 'Россия'},
            ]),
        });
        const modal = new AddCityModal();
        document.body.appendChild(modal);
        modal.querySelector('dialog').showModal = vi.fn();
        modal.open({cityId: 42, cityName: 'Тверь', regionName: 'Тверская область', countryName: 'Россия'});

        modal.querySelector('[data-change-city]').click();
        const input = modal.querySelector('[data-city-combobox-input]');
        input.value = 'Ржев';
        input.dispatchEvent(new Event('input', {bubbles: true}));
        expect(modal.cityId).toBe(42);
        await vi.waitFor(() => expect(modal.querySelector('[role="option"]')).not.toBeNull());
        modal.querySelector('[role="option"]').click();

        await vi.waitFor(() => expect(modal.cityId).toBe(77));
        expect(modal.querySelector('#city-id').value).toBe('77');
        expect(modal.querySelector('#city-title-in-modal').textContent).toBe('Ржев');
        expect(modal.querySelector('#region-title-in-modal').textContent).toBe('Тверская область, Россия');
        expect(modal.querySelector('#visit-details').hidden).toBe(false);
        expect(modal.querySelector('[data-change-city]').hidden).toBe(false);
        expect(modal.querySelector('[data-city-search-back]').hidden).toBe(true);
        expect(modal.previousCitySelection).toBeNull();
        await vi.waitFor(() => expect(document.activeElement).not.toBe(input));
        expect(modal.querySelector('form').contains(document.activeElement)).toBe(false);
    });

    it('sets today and yesterday through the quick-date button handlers', () => {
        vi.useFakeTimers();
        vi.setSystemTime(new Date(2026, 7, 5));
        const modal = new AddCityModal();
        document.body.appendChild(modal);

        const dateInput = modal.querySelector('#date-of-visit');
        const calendar = Calendar.mock.instances[0];
        const calendarElement = modal.querySelector('#add-city-visit-calendar');

        dateInput.click();
        modal.querySelector('#today-button').click();
        expect(dateInput.value).toBe('05.08.2026');
        expect(calendar.context.selectedDates).toEqual(['2026-08-05']);
        expect(calendarElement.hasAttribute('data-vc-calendar-hidden')).toBe(true);

        dateInput.click();
        modal.querySelector('#yesterday-button').click();
        expect(dateInput.value).toBe('04.08.2026');
        expect(calendar.context.selectedDates).toEqual(['2026-08-04']);
        expect(calendarElement.hasAttribute('data-vc-calendar-hidden')).toBe(true);
    });

    it('clears the display and calendar state when the form is reset', () => {
        const modal = new AddCityModal();
        document.body.appendChild(modal);
        const dateInput = modal.querySelector('#date-of-visit');
        const calendar = Calendar.mock.instances[0];

        modal.querySelector('#today-button').click();
        modal.resetForm();

        expect(dateInput.value).toBe('');
        expect(calendar.context.selectedDates).toEqual([]);
        expect(calendar.set).toHaveBeenLastCalledWith({selectedDates: []}, {dates: true});
    });

    it('clears the visit date when the dialog emits its native close event', () => {
        const modal = new AddCityModal();
        document.body.appendChild(modal);
        const dialog = modal.querySelector('dialog');
        const dateInput = modal.querySelector('#date-of-visit');
        const calendar = Calendar.mock.instances[0];

        modal.querySelector('#today-button').click();
        dialog.dispatchEvent(new Event('close'));

        expect(dateInput.value).toBe('');
        expect(calendar.context.selectedDates).toEqual([]);
    });

    it('clears the visit date when the explicit close button closes the dialog', () => {
        const modal = new AddCityModal();
        document.body.appendChild(modal);
        const dialog = modal.querySelector('dialog');
        const dateInput = modal.querySelector('#date-of-visit');
        const calendar = Calendar.mock.instances[0];
        dialog.close = () => dialog.dispatchEvent(new Event('close'));

        modal.querySelector('#today-button').click();
        modal.querySelector('#btn-close-modal').click();

        expect(dateInput.value).toBe('');
        expect(calendar.context.selectedDates).toEqual([]);
    });

    it('submits the calendar ISO date as a JSON DMR request', async () => {
        const modal = new AddCityModal();
        document.body.appendChild(modal);
        modal.close = vi.fn();
        const calendar = Calendar.mock.instances[0];
        calendar.context.selectedDates = ['2026-08-05'];
        fetch.mockResolvedValue({
            ok: true,
            json: vi.fn().mockResolvedValue({city: {city_title: 'Тверь'}}),
        });

        modal.querySelector('#form-add-city').dispatchEvent(new Event('submit', {
            bubbles: true,
            cancelable: true,
        }));

        await vi.waitFor(() => expect(fetch).toHaveBeenCalledOnce());
        const request = fetch.mock.calls[0][1];
        expect(request.headers).toMatchObject({
            'Content-Type': 'application/json',
            'X-CSRFToken': 'csrf-token',
        });
        expect(JSON.parse(request.body)).toMatchObject({
            city: '42',
            date_of_visit: '2026-08-05',
            has_magnet: false,
        });
    });

    it('does not show a modal toast when city-added is handled by the list', async () => {
        const modal = new AddCityModal();
        document.body.appendChild(modal);
        modal.close = vi.fn();
        modal.addEventListener('city-added', (event) => event.preventDefault());
        fetch.mockResolvedValue({
            ok: true,
            json: vi.fn().mockResolvedValue({city: {city_title: 'Тверь'}}),
        });

        modal.querySelector('#form-add-city').dispatchEvent(new Event('submit', {
            bubbles: true,
            cancelable: true,
        }));

        await vi.waitFor(() => expect(modal.close).toHaveBeenCalledOnce());

        expect(showSuccessToast).not.toHaveBeenCalled();
    });

    it('preserves the selected ISO date through reconnect for calendar state and submission', async () => {
        const modal = new AddCityModal();
        document.body.appendChild(modal);
        const firstCalendar = Calendar.mock.instances[0];
        const firstOptions = Calendar.mock.calls[0][1];

        firstCalendar.context.selectedDates = ['2026-08-05'];
        firstOptions.onClickDate(firstCalendar);

        modal.remove();
        expect(firstCalendar.destroy).toHaveBeenCalledOnce();
        expect(modal.visitCalendar).toBeNull();

        document.body.appendChild(modal);
        const replacementCalendar = Calendar.mock.instances[1];
        const replacementOptions = Calendar.mock.calls[1][1];
        expect(replacementOptions.selectedDates).toEqual(['2026-08-05']);
        expect(replacementCalendar.context.selectedDates).toEqual(['2026-08-05']);

        modal.close = vi.fn();
        fetch.mockResolvedValue({
            ok: true,
            json: vi.fn().mockResolvedValue({city: {city_title: 'Тверь'}}),
        });
        modal.querySelector('#form-add-city').dispatchEvent(new Event('submit', {
            bubbles: true,
            cancelable: true,
        }));

        await vi.waitFor(() => expect(fetch).toHaveBeenCalledOnce());
        expect(JSON.parse(fetch.mock.calls[0][1].body).date_of_visit).toBe('2026-08-05');
    });

});
