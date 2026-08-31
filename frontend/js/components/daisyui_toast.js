/*
 * ----------------------------------------------
 *
 * Copyright © Egor Vavilov (Shecspi)
 * Licensed under the Apache License, Version 2.0
 *
 * ----------------------------------------------
 */

/**
 * Компонент для отображения toast-уведомлений на основе daisyUI.
 */
export const showDaisyToast = (options) => {
    if (!options || typeof options !== 'object') {
        throw new TypeError('showDaisyToast expects an options object');
    }
    const {type, content, duration, dismissible, pauseOnInteraction} = options;

    let container = document.getElementById('daisy-toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'daisy-toast-container';
        container.className = 'dui-toast dui-toast-top dui-toast-end z-[10000]';
        document.body.appendChild(container);
    }

    const alertDiv = document.createElement('div');
    alertDiv.setAttribute('role', 'alert');
    alertDiv.className = `dui-alert max-w-sm ${type === 'success' ? 'dui-alert-success' : 'dui-alert-error'}`;

    const iconSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    iconSvg.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
    iconSvg.setAttribute('fill', 'none');
    iconSvg.setAttribute('viewBox', '0 0 24 24');
    iconSvg.setAttribute('class', 'dui-alert-icon h-5 w-5 shrink-0 stroke-current');

    const iconPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    iconPath.setAttribute('stroke-linecap', 'round');
    iconPath.setAttribute('stroke-linejoin', 'round');
    iconPath.setAttribute('stroke-width', '2');
    iconPath.setAttribute(
        'd',
        type === 'success'
            ? 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z'
            : 'M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z'
    );
    iconSvg.appendChild(iconPath);

    const contentContainer = document.createElement('span');
    contentContainer.className = 'font-normal';
    if (typeof content === 'string') {
        contentContainer.textContent = content;
    } else {
        contentContainer.append(content);
    }

    alertDiv.append(iconSvg, contentContainer);

    let timeoutId;
    let timerStartedAt;
    let remainingTime = duration;
    let isHovered = false;
    let hasFocusWithin = false;
    const removeToast = () => {
        clearTimeout(timeoutId);
        alertDiv.remove();
        if (!container.hasChildNodes()) {
            container.remove();
        }
    };
    const startTimer = () => {
        timerStartedAt = Date.now();
        timeoutId = setTimeout(removeToast, remainingTime);
    };
    const pauseTimer = () => {
        if (timeoutId === undefined) {
            return;
        }
        clearTimeout(timeoutId);
        timeoutId = undefined;
        remainingTime = Math.max(0, remainingTime - (Date.now() - timerStartedAt));
    };
    const resumeTimer = () => {
        if (timeoutId === undefined && !isHovered && !hasFocusWithin) {
            startTimer();
        }
    };

    if (dismissible) {
        const closeButton = document.createElement('button');
        closeButton.type = 'button';
        closeButton.className = 'dui-btn dui-btn-ghost dui-btn-sm dui-btn-circle shrink-0';
        closeButton.setAttribute('aria-label', 'Закрыть уведомление');
        closeButton.textContent = '×';
        closeButton.addEventListener('click', removeToast);
        alertDiv.append(closeButton);
    }

    container.appendChild(alertDiv);

    if (pauseOnInteraction) {
        alertDiv.addEventListener('mouseenter', () => {
            isHovered = true;
            pauseTimer();
        });
        alertDiv.addEventListener('mouseleave', () => {
            isHovered = false;
            resumeTimer();
        });
        alertDiv.addEventListener('focusin', () => {
            hasFocusWithin = true;
            pauseTimer();
        });
        alertDiv.addEventListener('focusout', (event) => {
            hasFocusWithin = alertDiv.contains(event.relatedTarget);
            resumeTimer();
        });
    }

    startTimer();
};
