/**
 * Web Component для модального окна добавления посещённого города.
 * Использует Light DOM и daisyUI для стилизации.
 * HTML размещён в <template> в Django-шаблоне для подсветки синтаксиса и валидации.
 *
 * ----------------------------------------------
 *
 * Copyright © Egor Vavilov (ShecSci)
 * Licensed under the Apache License, Version 2.0
 *
 * ----------------------------------------------
 */

import {City} from "../../js/components/schemas.js";
import {showDangerToast, showSuccessToast} from "../../js/components/toast.js";
import {getCookie} from "../../js/components/get_cookie.js";
import {
    clearVisitDateInput,
    initVisitDatePickers,
    isoFromParts,
    setVisitDateInputValue,
    valueFromInputToIso
} from "../../js/components/visit_date_picker.js";

class AddCityModal extends HTMLElement {
    constructor() {
        super();
        this.cityId = null;
        this.cityName = '';
        this.regionName = '';
        this.form = null;
        this.dialog = null;
        this.submitButton = null;
        this.ratingInput = null;
        this.ratingStars = [];
        this.selectedRating = 0;
    }

    connectedCallback() {
        this.cloneTemplate();
        this.initElements();
        this.initEventListeners();
        this.initGlobalClickListener();
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
        this.ratingStars = Array.from(this.querySelectorAll('.rating-star'));
        
        this.initRating();
        this.initDatePicker();
    }

    initRating() {
        this.ratingStars.forEach(star => {
            star.addEventListener('click', () => {
                const rating = parseInt(star.getAttribute('data-rating'));
                this.ratingInput.value = rating;
                this.selectedRating = rating;
                this.updateRatingStars(rating);
                this.updateSubmitButtonState();
            });
            
            star.addEventListener('mouseenter', () => {
                const hoverRating = parseInt(star.getAttribute('data-rating'));
                this.highlightStars(hoverRating);
            });
        });
        
        this.querySelector('#rating-container').addEventListener('mouseleave', () => {
            if (this.selectedRating > 0) {
                this.updateRatingStars(this.selectedRating);
            } else {
                this.updateRatingStars(0);
            }
        });
    }

    updateRatingStars(rating) {
        this.ratingStars.forEach(star => {
            const starRating = parseInt(star.getAttribute('data-rating'));
            if (starRating <= rating && rating > 0) {
                star.classList.add('dui-btn-warning');
                star.classList.remove('dui-btn-ghost');
            } else {
                star.classList.remove('dui-btn-warning');
                star.classList.add('dui-btn-ghost');
            }
        });
    }

    highlightStars(rating) {
        this.ratingStars.forEach(star => {
            const starRating = parseInt(star.getAttribute('data-rating'));
            if (starRating <= rating) {
                star.classList.add('dui-btn-warning');
                star.classList.remove('dui-btn-ghost');
            } else {
                star.classList.remove('dui-btn-warning');
                star.classList.add('dui-btn-ghost');
            }
        });
    }

    initDatePicker() {
        const dateInput = this.querySelector('#date-of-visit');
        if (!dateInput) return;
        
        const syncEmptyAppearance = () => {
            dateInput.classList.toggle('form-input-date-empty', !dateInput.value);
        };
        syncEmptyAppearance();
        dateInput.addEventListener('input', syncEmptyAppearance);
        dateInput.addEventListener('change', syncEmptyAppearance);
        
        initVisitDatePickers(this);
        
        this.querySelector('#today-button')?.addEventListener('click', () => {
            const t = new Date();
            setVisitDateInputValue('#date-of-visit', isoFromParts(t.getFullYear(), t.getMonth(), t.getDate()));
        });
        
        this.querySelector('#yesterday-button')?.addEventListener('click', () => {
            const t = new Date();
            t.setDate(t.getDate() - 1);
            setVisitDateInputValue('#date-of-visit', isoFromParts(t.getFullYear(), t.getMonth(), t.getDate()));
        });
    }

    initEventListeners() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        this.querySelector('#btn-close-modal').addEventListener('click', () => this.close());
        
        this.ratingInput.addEventListener('input', () => this.updateSubmitButtonState());
        this.ratingInput.addEventListener('change', () => this.updateSubmitButtonState());
    }

    updateSubmitButtonState() {
        const hasRating = this.ratingInput.value && parseInt(this.ratingInput.value) > 0;
        this.submitButton.disabled = !hasRating;
    }

    initGlobalClickListener() {
        document.addEventListener('click', (e) => {
            const button = e.target.closest('[data-action="add-city"]');
            if (button) {
                e.preventDefault();
                e.stopPropagation();
                
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
                    
                    this.open({
                        cityId: parseInt(cityId, 10),
                        cityName: cityName,
                        regionName: cityRegion
                    });
                }
            }
        });
    }

    open({cityId, cityName, regionName}) {
        this.cityId = cityId;
        this.cityName = cityName;
        this.regionName = regionName || '';
        
        this.querySelector('#city-title-in-modal').textContent = cityName;
        this.querySelector('#region-title-in-modal').textContent = regionName || '';
        this.querySelector('#city-id').value = cityId;
        
        this.resetForm();
        this.dialog.showModal();
    }

    close() {
        this.dialog.close();
    }

    resetForm() {
        this.form.reset();
        this.ratingInput.value = '';
        this.selectedRating = 0;
        this.updateRatingStars(0);
        this.updateSubmitButtonState();
        clearVisitDateInput('#date-of-visit');
        
        const magnetCheckbox = this.querySelector('#magnet-checkbox');
        if (magnetCheckbox) {
            magnetCheckbox.checked = false;
        }
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(this.form);
        formData.set('has_magnet', formData.has('has_magnet') ? '1' : '0');
        const csrfToken = formData.get('csrfmiddlewaretoken') || getCookie('csrftoken');
        const rawVisitDate = formData.get('date_of_visit');
        
        if (typeof rawVisitDate === 'string' && rawVisitDate.trim()) {
            const normalizedVisitDate = valueFromInputToIso(rawVisitDate);
            if (!normalizedVisitDate) {
                showDangerToast('Ошибка', 'Укажите корректную дату посещения в формате дд.мм.гггг');
                return;
            }
            formData.set('date_of_visit', normalizedVisitDate);
        }
        
        this.submitButton.disabled = true;
        this.submitButton.innerHTML = '<span class="dui-loading dui-loading-spinner dui-loading-sm"></span><span>Загрузка...</span>';
        
        try {
            const response = await fetch('/api/city/visited/add', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken
                },
                body: formData
            });
            
            if (!response.ok) {
                const error = new Error(`HTTP error! status: ${response.status}`);
                error.status = response.status;
                throw error;
            }
            
            const data = await response.json();
            
            this.close();
            this.resetForm();
            
            showSuccessToast('Успешно', `Город ${data.city.city_title} успешно добавлен как посещённый`);
            
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
            
            this.dispatchEvent(new CustomEvent('city-added', {
                detail: {
                    city,
                    isNewCity: isAddedNewCity
                },
                bubbles: true,
                composed: true
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
            this.submitButton.innerHTML = '<span>Добавить</span>';
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
