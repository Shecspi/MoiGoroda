/**
 * Компонент для отображения toast-уведомлений на основе daisyUI.
 *
 * ----------------------------------------------
 *
 * Copyright © Egor Vavilov (ShecSpi)
 * Licensed under the Apache License, Version 2.0
 *
 * ----------------------------------------------
 */

export const showDaisyToast = (type, message) => {
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

    const iconSvg = type === 'success'
        ? '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>'
        : '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path>';

    alertDiv.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="dui-alert-icon h-5 w-5 shrink-0 stroke-current">
            ${iconSvg}
        </svg>
        <span class="font-normal">${message}</span>
    `;

    container.appendChild(alertDiv);

    setTimeout(() => {
        alertDiv.remove();
        if (!container.hasChildNodes()) {
            container.remove();
        }
    }, 5000);
};
