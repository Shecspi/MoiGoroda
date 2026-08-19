// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import {getCookie} from '../components/get_cookie.js';
import {showDangerToast, showSuccessToast} from '../components/toast.js';

function bindFavoriteButton(button) {
    if (button.dataset.mgFavoriteBound) {
        return;
    }

    button.dataset.mgFavoriteBound = '1';
    button.addEventListener('click', async (event) => {
        event.preventDefault();
        event.stopPropagation();

        const collectionId = button.dataset.collectionId;
        const isFavorite = button.dataset.isFavorite === 'true';
        const icon = button.querySelector('svg');
        const textSpan = button.querySelector('.favorite-text');
        const card = document.getElementById(`collection-card-${collectionId}`);
        const setFavoriteText = (newText) => {
            if (!textSpan) {
                return;
            }
            textSpan.classList.add('opacity-0');
            setTimeout(() => {
                textSpan.textContent = newText;
                textSpan.classList.remove('opacity-0');
            }, 120);
        };

        try {
            const response = await fetch(`/api/collection/favorite/${collectionId}`, {
                method: isFavorite ? 'DELETE' : 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                const errorData = await response.json();
                showDangerToast('Ошибка', errorData.detail || 'Не удалось выполнить операцию');
                return;
            }

            const data = await response.json();
            button.dataset.isFavorite = data.is_favorite ? 'true' : 'false';
            if (data.is_favorite) {
                if (icon) {
                    icon.outerHTML = '<svg class="size-4" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="m12 17.27 5.18 3.11-1.64-5.81L20 10.5l-5.92-.5L12 4.5l-2.08 5.5L4 10.5l4.46 4.07-1.64 5.81z"/></svg>';
                }
                setFavoriteText('Удалить из избранного');
                button.classList.remove('border-amber-300', 'bg-amber-50', 'text-amber-700', 'hover:bg-amber-100', 'dark:border-amber-600', 'dark:bg-amber-500/10', 'dark:text-amber-400', 'dark:hover:bg-amber-500/20');
                button.classList.add('border-rose-300', 'bg-rose-50', 'text-rose-700', 'hover:bg-rose-100', 'dark:border-rose-600', 'dark:bg-rose-500/10', 'dark:text-rose-400', 'dark:hover:bg-rose-500/20');
                if (card) {
                    card.classList.remove('border-gray-200', 'bg-white', 'dark:border-neutral-700', 'dark:bg-neutral-900');
                    card.classList.add('border-amber-300', 'bg-amber-50/50', 'dark:border-amber-600', 'dark:bg-amber-950/30');
                    card.classList.add('ring-2', 'ring-amber-300', 'ring-offset-2', 'ring-offset-transparent');
                    setTimeout(() => {
                        card.classList.remove('ring-2', 'ring-amber-300', 'ring-offset-2', 'ring-offset-transparent');
                    }, 250);
                }
                button.classList.add('scale-105', 'shadow-lg');
                setTimeout(() => button.classList.remove('scale-105', 'shadow-lg'), 150);
                showSuccessToast('Успешно', 'Коллекция добавлена в избранное');
            } else {
                if (icon) {
                    icon.outerHTML = '<svg class="size-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m12 17.27 5.18 3.11-1.64-5.81L20 10.5l-5.92-.5L12 4.5l-2.08 5.5L4 10.5l4.46 4.07-1.64 5.81z"/></svg>';
                }
                setFavoriteText('Добавить в избранное');
                button.classList.remove('border-rose-300', 'bg-rose-50', 'text-rose-700', 'hover:bg-rose-100', 'dark:border-rose-600', 'dark:bg-rose-500/10', 'dark:text-rose-400', 'dark:hover:bg-rose-500/20');
                button.classList.add('border-amber-300', 'bg-amber-50', 'text-amber-700', 'hover:bg-amber-100', 'dark:border-amber-600', 'dark:bg-amber-500/10', 'dark:text-amber-400', 'dark:hover:bg-amber-500/20');
                if (card) {
                    card.classList.remove('border-amber-300', 'bg-amber-50/50', 'dark:border-amber-600', 'dark:bg-amber-950/30');
                    card.classList.add('border-gray-200', 'bg-white', 'dark:border-neutral-700', 'dark:bg-neutral-900');
                    card.classList.add('ring-2', 'ring-rose-300', 'ring-offset-2', 'ring-offset-transparent');
                    setTimeout(() => {
                        card.classList.remove('ring-2', 'ring-rose-300', 'ring-offset-2', 'ring-offset-transparent');
                    }, 250);
                }
                button.classList.add('scale-95', 'shadow-md');
                setTimeout(() => button.classList.remove('scale-95', 'shadow-md'), 150);
                showSuccessToast('Успешно', 'Коллекция удалена из избранного');
            }
        } catch (error) {
            console.error('Error toggling favorite:', error);
            showDangerToast('Ошибка', 'Произошла ошибка при выполнении запроса');
        }
    });
}

export function initializeCollectionFavorites(root = document) {
    root.querySelectorAll('.favorite-star').forEach(bindFavoriteButton);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => initializeCollectionFavorites());
} else {
    initializeCollectionFavorites();
}

document.addEventListener('visited-city-list-refreshed', (event) => {
    initializeCollectionFavorites(event.detail?.root);
});
