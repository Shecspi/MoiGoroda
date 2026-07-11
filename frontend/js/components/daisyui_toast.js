/**
 * Компонент для отображения toast-уведомлений на основе daisyUI.
 *
 * ----------------------------------------------
 *
 * Copyright © Egor Vavilov (Shecspi)
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

    const messageSpan = document.createElement('span');
    messageSpan.className = 'font-normal';
    messageSpan.textContent = String(message);

    alertDiv.append(iconSvg, messageSpan);

    container.appendChild(alertDiv);

    setTimeout(() => {
        alertDiv.remove();
        if (!container.hasChildNodes()) {
            container.remove();
        }
    }, 5000);
};
