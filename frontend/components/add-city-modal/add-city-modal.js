// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

/**
 * Web Component для модального окна добавления посещённого города.
 * Использует Light DOM и daisyUI для стилизации.
 * HTML размещён в <template> в Django-шаблоне для подсветки синтаксиса и валидации.
 */

import {City} from "../../js/components/schemas.js";
import {showDangerToast, showSuccessToast} from "../../js/components/toast.js";
import {getCookie} from "../../js/components/get_cookie.js";
import {Calendar} from 'vanilla-calendar-pro';
import 'vanilla-calendar-pro/styles/index.css';
import {isoFromParts, isoToRuDisplay} from '../../js/components/visit_date_picker.js';
import {CityCascadeSelector} from '../../js/components/city_cascade_selector.js';
import {CityCombobox} from './city-combobox.js';

class AddCityModal extends HTMLElement {
    constructor() {
        super();
        this.cityId = null;
        this.cityName = '';
        this.regionName = '';
        this.mode = 'create';
        this.visitedCityId = null;
        this.surface = '';
        this.cityCascadeSelector = null;
        this.cityCombobox = null;
        this.form = null;
        this.dialog = null;
        this.submitButton = null;
        this.ratingInput = null;
        this.ratingStars = [];
        this.selectedRating = 0;
        this.visitCalendar = null;
        this.visitDateForReconnect = '';
        this.globalClickHandler = null;
        this.calendarOutsideClickHandler = null;
    }

    connectedCallback() {
        if (this.dialog) {
            this.initVisitCalendar();
            this.initCalendarOutsideClickListener();
            this.initGlobalClickListener();
            return;
        }

        this.cloneTemplate();
        this.initElements();
        this.initEventListeners();
        this.initGlobalClickListener();
    }

    disconnectedCallback() {
        if (this.globalClickHandler) {
            document.removeEventListener('click', this.globalClickHandler);
            this.globalClickHandler = null;
        }
        if (this.calendarOutsideClickHandler) {
            document.removeEventListener('click', this.calendarOutsideClickHandler, true);
            this.calendarOutsideClickHandler = null;
        }
        this.visitDateForReconnect = this.visitCalendar?.context.selectedDates[0] || '';
        this.visitCalendar?.destroy();
        this.visitCalendar = null;
        this.cityCombobox?.destroy();
        this.cityCombobox = null;
    }

    cloneTemplate() {
        const template = document.getElementById('add-city-modal-template');
        if (template) {
            const content = template.content.cloneNode(true);
            this.appendChild(content);
        } else {
            console.error('Template #add-city-modal-template not found');
        }
    }

    initElements() {
        this.dialog = this.querySelector('dialog');
        this.form = this.querySelector('#form-add-city');
        this.submitButton = this.querySelector('#btn_add-visited-city');
        this.ratingInput = this.querySelector('#id_rating');
        this.ratingContainer = this.querySelector('#rating-container');
        this.ratingRadios = Array.from(this.ratingContainer.querySelectorAll('input[type="radio"]'));
        this.citySelectionFields = this.querySelector('#city-selection-fields');
        this.citySummaryCard = this.querySelector('#city-summary-card');
        
        this.initRating();
        this.initDatePicker();
    }

    initRating() {
        this.ratingRadios.forEach(radio => {
            radio.addEventListener('change', () => {
                const rating = parseInt(radio.value);
                this.ratingInput.value = rating;
                this.selectedRating = rating;
                this.updateSubmitButtonState();
            });
        });
    }

    initDatePicker() {
        this.initVisitCalendar();

        this.querySelector('#today-button')?.addEventListener('click', () => {
            const t = new Date();
            this.setVisitDate(isoFromParts(t.getFullYear(), t.getMonth(), t.getDate()));
            this.hideVisitCalendar();
        });

        this.querySelector('#yesterday-button')?.addEventListener('click', () => {
            const t = new Date();
            t.setDate(t.getDate() - 1);
            this.setVisitDate(isoFromParts(t.getFullYear(), t.getMonth(), t.getDate()));
            this.hideVisitCalendar();
        });

        const dateInput = this.querySelector('#date-of-visit');
        dateInput?.addEventListener('click', () => {
            this.showVisitCalendar();
        });
        dateInput?.addEventListener('focus', () => {
            this.showVisitCalendar();
        });
        this.initCalendarOutsideClickListener();
    }

    initVisitCalendar() {
        const calendarElement = this.querySelector('#add-city-visit-calendar');
        if (!calendarElement) return;

        this.visitCalendar = new Calendar(calendarElement, {
            locale: 'ru-RU',
            selectionDatesMode: 'single',
            enableDateToggle: false,
            selectedDates: this.visitDateForReconnect ? [this.visitDateForReconnect] : [],
            styles: {
                calendar: 'vc fixed z-[1001] w-fit bg-base-100 border border-base-300 shadow-lg rounded-xl',
            },
            onClickDate: (self) => {
                this.setVisitDate(self.context.selectedDates[0] || '');
                this.hideVisitCalendar();
            },
        });
        this.visitDateForReconnect = '';
        this.visitCalendar.init();
        calendarElement.style.position = 'fixed';
    }

    showVisitCalendar() {
        const calendarElement = this.querySelector('#add-city-visit-calendar');
        if (!calendarElement) return;

        const inputBounds = this.querySelector('#date-of-visit')?.getBoundingClientRect();
        if (inputBounds) {
            calendarElement.style.top = `${inputBounds.bottom + 8}px`;
            calendarElement.style.left = `${inputBounds.left}px`;
        }
        calendarElement.style.position = 'fixed';
        calendarElement.removeAttribute('data-vc-calendar-hidden');
    }

    hideVisitCalendar() {
        this.querySelector('#add-city-visit-calendar')?.setAttribute('data-vc-calendar-hidden', '');
    }

    initCalendarOutsideClickListener() {
        if (this.calendarOutsideClickHandler) {
            return;
        }

        this.calendarOutsideClickHandler = (event) => {
            const calendarElement = this.querySelector('#add-city-visit-calendar');
            const dateInput = this.querySelector('#date-of-visit');
            if (!calendarElement?.contains(event.target) && event.target !== dateInput) {
                this.hideVisitCalendar();
            }
        };
        document.addEventListener('click', this.calendarOutsideClickHandler, true);
    }

    setVisitDate(iso) {
        const value = iso || '';
        this.querySelector('#date-of-visit').value = value ? isoToRuDisplay(value) : '';
        this.visitCalendar.set({selectedDates: value ? [value] : []}, {dates: true});
    }

    clearVisitDate() {
        this.setVisitDate('');
        this.hideVisitCalendar();
    }

    initEventListeners() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        this.dialog.addEventListener('close', () => this.resetForm());
        this.querySelector('#btn-close-modal').addEventListener('click', () => this.close());
        
        this.ratingInput.addEventListener('input', () => this.updateSubmitButtonState());
        this.ratingInput.addEventListener('change', () => this.updateSubmitButtonState());
    }

    updateSubmitButtonState() {
        const hasRating = this.ratingInput.value && parseInt(this.ratingInput.value) > 0;
        this.submitButton.disabled = !hasRating || !this.cityId;
    }

    initGlobalClickListener() {
        if (this.globalClickHandler) {
            return;
        }

        this.globalClickHandler = (e) => {
            const button = e.target.closest('[data-action="add-city"], [data-action="edit-visited-city"]');
            if (button) {
                e.preventDefault();
                e.stopPropagation();
                
                const editVisitId = button.getAttribute('data-visited-city-id');
                if (button.getAttribute('data-action') === 'edit-visited-city' && editVisitId) {
                    this.openEdit(parseInt(editVisitId, 10));
                    return;
                }

                const cityName = button.getAttribute('data-city-name');
                const cityId = button.getAttribute('data-city-id');
                const cityRegion = button.getAttribute('data-city-region') || '';
                
                if (cityName && cityId) {
                    if (window.MG_MAIN_MAP && typeof window.MG_MAIN_MAP.closePopup === 'function') {
                        try {
                            window.MG_MAIN_MAP.closePopup();
                        } catch (err) {
                            console.error('Ошибка при закрытии popup карты:', err);
                        }
                    }
                    
                    const openOptions = {
                        cityId: parseInt(cityId, 10),
                        cityName: cityName,
                        regionName: cityRegion
                    };
                    const surface = button.getAttribute('data-surface');
                    if (surface) {
                        openOptions.surface = surface;
                    }
                    this.open(openOptions);
                } else {
                    const openOptions = {
                        cityId: null,
                        cityName: '',
                        regionName: '',
                    };
                    const surface = button.getAttribute('data-surface');
                    if (surface) {
                        openOptions.surface = surface;
                    }
                    this.open(openOptions);
                }
            }
        };
        document.addEventListener('click', this.globalClickHandler);
    }

    open({cityId = null, cityName = '', regionName = '', surface = ''}) {
        this.resetForm();
        this.mode = 'create';
        this.visitedCityId = null;
        this.cityId = cityId;
        this.cityName = cityName;
        this.regionName = regionName || '';
        this.surface = surface;

        this.querySelector('#city-title-in-modal').textContent = cityName;
        this.querySelector('#region-title-in-modal').textContent = regionName || '';
        this.querySelector('#city-id').value = cityId || '';
        this.toggleCitySelection(!cityId);
        this.setModeLabels();

        if (!cityId) {
            this.initCityCascadeSelector();
        }
        this.dialog.showModal();
        this.querySelector(cityId ? '#date-of-visit' : '[data-city-combobox-input]')?.focus();
        this.updateSubmitButtonState();
    }

    async openEdit(visitedCityId) {
        try {
            const response = await fetch(`/api/city/visited/${visitedCityId}/`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            const visit = data.visit;

            this.resetForm();
            this.mode = 'edit';
            this.visitedCityId = visitedCityId;
            this.cityId = visit.city;
            this.cityName = visit.city_title;
            this.regionName = visit.region_title || '';
            this.querySelector('#city-title-in-modal').textContent = this.cityName;
            this.querySelector('#region-title-in-modal').textContent = this.regionName;
            this.querySelector('#city-id').value = String(this.cityId);
            this.querySelector('#magnet-checkbox').checked = Boolean(visit.has_magnet);
            this.querySelector('#impression').value = visit.impression || '';
            this.ratingInput.value = String(visit.rating);
            this.ratingRadios.forEach((radio) => {
                radio.checked = Number(radio.value) === Number(visit.rating);
            });
            this.setVisitDate(visit.date_of_visit || '');
            this.toggleCitySelection(false);
            this.setModeLabels();
            this.dialog.showModal();
            this.querySelector('#date-of-visit')?.focus();
            this.updateSubmitButtonState();
        } catch (error) {
            console.error('Ошибка при загрузке посещённого города:', error);
            showDangerToast('Ошибка', 'Не удалось загрузить посещение. Попробуйте ещё раз.');
        }
    }

    toggleCitySelection(show) {
        if (this.citySelectionFields) {
            this.citySelectionFields.hidden = !show;
        }
        if (this.citySummaryCard) {
            this.citySummaryCard.hidden = show;
        }
    }

    setModeLabels() {
        const label = this.querySelector('#addCityModalLabel');
        if (label) {
            label.textContent = this.mode === 'edit' ? 'Редактировать посещение города' : 'Добавить посещённый город';
        }
        const submitText = this.submitButton?.querySelector('span');
        if (submitText) {
            submitText.textContent = this.mode === 'edit' ? 'Сохранить' : 'Добавить';
        }
    }

    initCityCascadeSelector() {
        this.cityCascadeSelector?.destroy();
        this.cityCombobox?.destroy();
        this.cityCombobox = new CityCombobox(this, {
            onSelect: async (city) => {
                if (!city) {
                    this.cityCascadeSelector?.cancelLocationSelection();
                    this.cityId = null;
                    this.querySelector('#city-id').value = '';
                    this.updateSubmitButtonState();
                    return;
                }

                if (city.country_code) {
                    const synchronized = await this.cityCascadeSelector.selectLocation({
                        countryCode: city.country_code,
                        regionCode: city.region_code || '',
                    });
                    if (!synchronized) {
                        return;
                    }
                    this.cityCombobox.restoreSelection(city);
                }

                this.cityId = Number(city.id);
                this.querySelector('#city-id').value = String(city.id);
                this.updateSubmitButtonState();
            },
            onError: () => {
                showDangerToast('Ошибка', 'Не удалось найти город. Попробуйте ещё раз.');
            },
        });
        this.cityCombobox.init();
        this.cityCascadeSelector = new CityCascadeSelector(this, {
            locationValueMode: 'code',
            onChange: ({countryCode, regionCode, preserveCity}) => {
                if (!preserveCity) {
                    this.cityId = null;
                    this.querySelector('#city-id').value = '';
                    this.updateSubmitButtonState();
                }
                this.cityCombobox.setFilters({
                    country: countryCode,
                    region: regionCode,
                    preserveInput: preserveCity,
                });
            },
            onCitiesChange: (cities) => this.cityCombobox.setCities(cities),
            onError: () => {
                showDangerToast('Ошибка', 'Не удалось загрузить список городов. Попробуйте ещё раз.');
            },
        });
        this.cityCascadeSelector.init();
    }

    close() {
        this.dialog.close();
    }

    resetForm() {
        this.form.reset();
        this.cityCascadeSelector?.destroy();
        this.cityCascadeSelector = null;
        this.cityCombobox?.destroy();
        this.cityCombobox = null;
        this.cityId = null;
        this.visitedCityId = null;
        this.surface = '';
        this.ratingInput.value = '';
        this.selectedRating = 0;
        this.ratingRadios.forEach(radio => radio.checked = false);
        this.updateSubmitButtonState();
        this.clearVisitDate();
        
        const magnetCheckbox = this.querySelector('#magnet-checkbox');
        if (magnetCheckbox) {
            magnetCheckbox.checked = false;
        }
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(this.form);
        const csrfToken = formData.get('csrfmiddlewaretoken') || getCookie('csrftoken');
        const payload = Object.fromEntries(formData.entries());
        delete payload.csrfmiddlewaretoken;
        payload.has_magnet = formData.has('has_magnet');
        payload.date_of_visit = this.visitCalendar.context.selectedDates[0] || null;
        if (this.surface) {
            payload.from = this.surface;
        }

        const isEdit = this.mode === 'edit';
        if (isEdit) {
            delete payload.city;
            delete payload.from;
        }
        
        this.submitButton.disabled = true;
        this.submitButton.innerHTML = '<span class="dui-loading dui-loading-spinner dui-loading-sm"></span><span>Загрузка...</span>';
        
        try {
            const response = await fetch(
                isEdit ? `/api/city/visited/${this.visitedCityId}/` : '/api/city/visited/add',
                {
                method: isEdit ? 'PATCH' : 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify(payload),
                }
            );
            
            if (!response.ok) {
                const error = new Error(`HTTP error! status: ${response.status}`);
                error.status = response.status;
                throw error;
            }
            
            const data = await response.json();
            
            if (isEdit) {
                this.close();
                showSuccessToast('Успешно', 'Посещение города успешно обновлено');
                const updatedCity = data.city && data.visit
                    ? {...data.city, date_of_visit: data.visit.date_of_visit}
                    : data.city;
                this.dispatchEvent(new CustomEvent('visited-city-updated', {
                    detail: {...data, city: updatedCity},
                    bubbles: true,
                    composed: true,
                }));
                return;
            }

            this.close();
            
            const city = new City();
            city.id = data.city.city;
            city.name = data.city.city_title;
            city.region = data.city.region_title;
            city.country = data.city.country;
            city.lat = data.city.lat;
            city.lon = data.city.lon;
            city.number_of_visits = data.city.number_of_visits;
            city.first_visit_date = data.city.first_visit_date;
            city.last_visit_date = data.city.last_visit_date;
            city.date_of_visit = data.city.date_of_visit;
            city.number_of_users_who_visit_city = data.city.number_of_users_who_visit_city;
            city.number_of_visits_all_users = data.city.number_of_visits_all_users;
            
            const isAddedNewCity = city.number_of_visits === 1;
            
            const cityAddedEvent = new CustomEvent('city-added', {
                detail: {
                    city,
                    isNewCity: isAddedNewCity
                },
                bubbles: true,
                cancelable: true,
                composed: true,
            });
            this.dispatchEvent(cityAddedEvent);
            if (!cityAddedEvent.defaultPrevented) {
                showSuccessToast('Успешно', `Город ${data.city.city_title} успешно добавлен как посещённый`);
            }

            this.dispatchEvent(new CustomEvent('visited-city-created', {
                detail: {
                    city,
                    visit: data.visit || null,
                    isNewCity: isAddedNewCity,
                },
                bubbles: true,
                composed: true,
            }));
            
            this.updateToolbarCounts(isAddedNewCity);
            
        } catch (error) {
            console.error('Ошибка при добавлении города:', error);
            
            if (error.status === 409) {
                showDangerToast('Ошибка', 'Вы уже посещали город в указанную дату');
            } else {
                showDangerToast('Ошибка', 'Что-то пошло не так. Попробуйте ещё раз.');
            }
        } finally {
            this.submitButton.disabled = false;
            this.submitButton.innerHTML = `<span>${isEdit ? 'Сохранить' : 'Добавить'}</span>`;
            this.updateSubmitButtonState();
        }
    }

    updateToolbarCounts(isAddedNewCity) {
        const numberOfVisitedCities = document.getElementById('number_of_visited_cities');
        if (numberOfVisitedCities) {
            const oldQty = numberOfVisitedCities.textContent;
            const newQty = isAddedNewCity ? Number(oldQty) + 1 : oldQty;
            numberOfVisitedCities.textContent = newQty.toString();
        }
        
        if (isAddedNewCity) {
            const numberOfVisitedCitiesInCountry = document.getElementById('number_of_visited_cities_in_country');
            if (numberOfVisitedCitiesInCountry) {
                const oldQty = numberOfVisitedCitiesInCountry.textContent;
                numberOfVisitedCitiesInCountry.textContent = (Number(oldQty) + 1).toString();
            }
        }
    }
}

customElements.define('add-city-modal', AddCityModal);

export default AddCityModal;
