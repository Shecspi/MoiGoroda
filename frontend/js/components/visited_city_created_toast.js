// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import {showDaisyToast} from './daisyui_toast.js';

const createLink = (title, url) => {
    const link = document.createElement('a');
    link.className = 'dui-link dui-link-hover font-medium';
    link.href = url;
    link.textContent = title;
    return link;
};

const collectionNoun = (count) => (
    count % 10 === 1 && count % 100 !== 11 ? 'коллекции' : 'коллекциях'
);

export const showVisitedCityCreatedToast = (collectionContext) => {
    const content = document.createDocumentFragment();
    const wrapper = document.createElement('div');
    wrapper.className = 'flex min-w-0 flex-col gap-1';

    const cityLine = document.createElement('p');
    cityLine.append('Добавлено посещение: ');
    cityLine.append(createLink(collectionContext.city.title, collectionContext.city.url));
    wrapper.append(cityLine);

    const collections = collectionContext.common_collections;
    if (collections.count === 1) {
        const collectionLine = document.createElement('p');
        collectionLine.className = 'line-clamp-2';
        collectionLine.append('Город входит в коллекцию «');
        const collectionLink = createLink(collections.single.title, collections.single.url);
        collectionLink.title = collections.single.title;
        collectionLine.append(collectionLink, '».');
        wrapper.append(collectionLine);
    } else if (collections.count >= 2) {
        const collectionLine = document.createElement('p');
        collectionLine.append(
            `Город состоит в ${collections.count} ${collectionNoun(collections.count)}. `,
        );
        collectionLine.append(createLink('Посмотреть коллекции', collections.catalog_url));
        wrapper.append(collectionLine);
    }

    content.append(wrapper);
    showDaisyToast({
        type: 'success',
        content,
        duration: 5000,
        dismissible: true,
        pauseOnInteraction: true,
    });
};
