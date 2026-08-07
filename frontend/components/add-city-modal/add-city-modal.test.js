/**
 * ---------------------------------------------
 *
 * Copyright © Egor Vavilov (Shecspi)
 * Licensed under the Apache License, Version 2.0
 *
 * ----------------------------------------------
 */

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
import AddCityModal from './add-city-modal.js';

const modalTemplate = `
    <template id="add-city-modal-template">
        <dialog>
            <form id="form-add-city">
                <h4 id="city-title-in-modal"></h4>
                <p id="region-title-in-modal"></p>
                <input id="date-of-visit" name="date_of_visit" readonly>
                <div id="add-city-visit-calendar" class="vc absolute top-full start-0 z-10 w-fit mt-2" data-vc-calendar-hidden></div>
                <button type="button" id="today-button"></button>
                <button type="button" id="yesterday-button"></button>
                <button type="button" id="btn-close-modal"></button>
                <button id="btn_add-visited-city"></button>
                <input type="hidden" id="city-id" name="city" value="42">
                <input id="id_rating" name="rating">
                <div id="rating-container"><input type="radio" value="1"></div>
            </form>
        </dialog>
    </template>`;

describe('AddCityModal visit calendar', () => {
    beforeEach(() => {
        document.body.innerHTML = modalTemplate;
        Calendar.mockClear();
        vi.stubGlobal('fetch', vi.fn());
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
        });
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

    it('shows the calendar only when the date input is clicked', () => {
        const modal = new AddCityModal();
        document.body.appendChild(modal);
        const dateInput = modal.querySelector('#date-of-visit');
        const calendarElement = modal.querySelector('#add-city-visit-calendar');

        expect(calendarElement.hasAttribute('data-vc-calendar-hidden')).toBe(true);
        dateInput.click();
        expect(calendarElement.hasAttribute('data-vc-calendar-hidden')).toBe(false);
    });

    it('removes the hidden calendar from modal flow before it is opened', () => {
        const modal = new AddCityModal();
        document.body.appendChild(modal);
        const calendarElement = modal.querySelector('#add-city-visit-calendar');

        expect(calendarElement.style.position).toBe('absolute');
    });

    it('opens the calendar as an absolute overlay below the date input', () => {
        const modal = new AddCityModal();
        document.body.appendChild(modal);
        const dateInput = modal.querySelector('#date-of-visit');
        const calendarElement = modal.querySelector('#add-city-visit-calendar');

        dateInput.click();

        expect(calendarElement.style.position).toBe('absolute');
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

    it('moves focus to the close button when the dialog opens', () => {
        const modal = new AddCityModal();
        document.body.appendChild(modal);
        const dialog = modal.querySelector('dialog');
        const closeButton = modal.querySelector('#btn-close-modal');
        dialog.showModal = vi.fn();

        modal.open({cityId: 42, cityName: 'Тверь', regionName: 'Тверская область'});

        expect(dialog.showModal).toHaveBeenCalledOnce();
        expect(document.activeElement).toBe(closeButton);
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

    it('submits the calendar ISO date rather than the localized display value', async () => {
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
        expect(request.body.get('date_of_visit')).toBe('2026-08-05');
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
        expect(fetch.mock.calls[0][1].body.get('date_of_visit')).toBe('2026-08-05');
    });

});
