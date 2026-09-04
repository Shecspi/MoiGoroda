// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

// THROWAWAY PROTOTYPE: no persistence, real analytics, billing, or export.

const root = document.getElementById('travel-results-prototype');

if (root) {
    const variants = [
        { key: 'A', name: 'История по главам' },
        { key: 'B', name: 'Журнальный разворот' },
        { key: 'C', name: 'Панель исследователя' },
    ];

    const scenarios = {
        rich: {
            short: 'Насыщенный год', mode: 'summary', period: '2025', access: 'Расширенный тариф',
            kicker: 'Ваш 2025 год', title: 'Год, в котором дороги вели дальше обычного',
            intro: 'Вы открыли девять новых городов и всё равно находили причины возвращаться в знакомые места.',
            visits: 14, cities: 9, repeats: 5, countries: 3, distance: '8 460 км', days: 34,
            record: 'Личный рекорд: больше всего новых городов за полный год',
            insight: 'Особенно насыщенной получилась осень: на неё пришлось 6 из 14 посещений.',
            route: ['Псков', 'Выборг', 'Казань', 'Тобольск', 'Калининград'],
            note: 'Снимок 2025 года сохранён при первом открытии.', publication: 'Не настроена',
        },
        quiet: {
            short: 'Редкий год', mode: 'summary', period: '2024', access: 'Расширенный тариф',
            kicker: 'Ваш 2024 год', title: 'Два посещения, которые сохранили этот год',
            intro: 'В этом году городов было немного, зато оба посещения получили точные даты и остались в вашей истории.',
            visits: 2, cities: 1, repeats: 1, countries: 1, distance: '620 км', days: 5,
            record: '', insight: 'Вы вернулись в Ярославль спустя 3 года. Иногда знакомый город и есть главное открытие года.',
            route: ['Суздаль', 'Ярославль'],
            note: 'Разделы без содержательных данных пропущены: нет сезонного пика и рекорда.', publication: 'Не настроена',
        },
        lifetime: {
            short: 'Вся история', mode: 'summary', period: 'Вся история', access: 'Расширенный тариф',
            kicker: 'Ваша история путешествий', title: '28 городов уже стали частью вашей карты',
            intro: 'От первой отметки до последнего возвращения: вся накопленная история в одном маршруте.',
            visits: 43, cities: 28, repeats: 15, countries: 6, distance: '31 200 км', days: 126,
            record: 'Чаще всего вы возвращались в Санкт-Петербург — 6 посещений',
            insight: 'У семи посещений нет даты. Они учтены здесь, но не попадут в итоги отдельных лет.',
            route: ['Москва', 'Тула', 'Казань', 'Пермь', 'Томск', 'Владивосток'],
            note: 'Страны объединяют ручные отметки и страны посещённых городов.', publication: 'Не настроена',
        },
        compare: {
            short: 'Сравнение', mode: 'compare', period: '2025 и 2023', access: 'Расширенный тариф',
            kicker: 'Сравнение периодов', title: 'Два года с разным ритмом',
            intro: 'Сравнение показывает изменение каждого показателя без общей оценки года.',
            visits: 14, cities: 7, repeats: 4, countries: 3, distance: '8 460 км', days: 34,
            previousVisits: 9, previousCities: 0, previousRepeats: 4, previousCountries: 3,
            record: '', insight: 'Новые города: 7 против 0. Страны: 3 против 3 — результат не изменился.',
            route: ['2023', '2025'], note: 'Нулевая база показана числом, без некорректного процента роста.', publication: 'Не настроена',
        },
        teaser: {
            short: 'Тизер тарифа', mode: 'teaser', period: '2025', access: 'Бесплатный тариф',
            kicker: 'Ваши итоги готовы', title: 'В вашей истории нашлось 5 личных наблюдений',
            intro: 'Показываем достаточно персонального контекста, чтобы ценность была понятна до оплаты.',
            visits: 14, cities: 9, repeats: 5, countries: 3, distance: '8 460 км', days: 34,
            record: 'Один личный рекорд найден', insight: 'Самый активный сезон уже определён.',
            route: ['Открытие', 'Рекорд', 'Карта'], note: 'Существующая личная статистика остаётся доступной бесплатно.', publication: 'Закрыта',
        },
        expired: {
            short: 'Архив без доступа', mode: 'archive', period: 'Архив', access: 'Подписка закончилась',
            kicker: 'Сохранённые итоги', title: 'Ваши снимки никуда не исчезли',
            intro: 'Производные материалы скрыты до новой оплаты, исходные посещения и фотографии по-прежнему доступны.',
            visits: 43, cities: 28, repeats: 15, countries: 6, distance: '31 200 км', days: 126,
            record: '', insight: '', route: [], note: 'Закрытый снимок можно удалить без возобновления подписки.', publication: 'Скрыта',
        },
        studio: {
            short: 'Публикация', mode: 'studio', period: '2025', access: 'Расширенный тариф',
            kicker: 'Материалы для публикации', title: 'Соберите итог в своём стиле',
            intro: 'Готовые направления вместо полного редактора: меняются формат, тема, акцент и набор блоков.',
            visits: 14, cities: 9, repeats: 5, countries: 3, distance: '8 460 км', days: 34,
            record: 'Личный рекорд года', insight: 'Осень стала самым насыщенным сезоном.',
            route: ['Псков', 'Выборг', 'Казань'], note: 'Фотографии появятся только после явного выбора.', publication: '1:1 · карта · светлая',
        },
    };

    const url = new URL(window.location.href);
    const state = {
        variant: variants.some((item) => item.key === url.searchParams.get('variant')) ? url.searchParams.get('variant') : 'B',
        scenario: scenarios[url.searchParams.get('scenario')] ? url.searchParams.get('scenario') : 'rich',
        storyStep: 0,
        template: 'map',
        format: '1:1',
        theme: 'light',
        accent: 'Кобальт',
        output: 'summary',
        watermark: true,
        blocks: new Set(['Карта', 'Показатели', 'Наблюдение']),
        selectedPhotos: new Set(),
        archiveDeleted: false,
    };

    const mapArtwork = (compact = false) => `
        <div class="relative overflow-hidden rounded-box bg-[#dfe9dc] ${compact ? 'h-48' : 'h-64 sm:h-80'}">
            <div class="absolute -left-8 top-8 h-32 w-72 rotate-[-12deg] rounded-[50%] border-[18px] border-[#b8d4e7]"></div>
            <div class="absolute right-4 top-6 h-36 w-44 rotate-12 rounded-[42%_58%_45%_55%] bg-[#f7f1d2] shadow-inner"></div>
            <div class="absolute bottom-8 left-[22%] h-28 w-48 -rotate-6 rounded-[55%_45%_62%_38%] bg-[#c5d6ad]"></div>
            ${['18%:40%', '38%:68%', '59%:30%', '74%:58%', '86%:24%'].map((position) => {
                const [left, top] = position.split(':');
                return `<span class="absolute size-3 rounded-full bg-primary shadow-[0_0_0_5px_rgba(255,255,255,.75)]" style="left:${left};top:${top}"></span>`;
            }).join('')}
            <span class="absolute bottom-3 right-3 rounded-full bg-white/85 px-3 py-1 text-[10px] font-bold text-slate-700">Схема маршрута · фиктивные данные</span>
        </div>`;

    const metric = (value, label, detail = '') => `
        <div class="dui-stat min-w-0 p-0">
            <p class="dui-stat-value text-2xl font-black tabular-nums sm:text-3xl">${value}</p>
            <p class="dui-stat-title text-xs">${label}</p>
            ${detail ? `<p class="dui-stat-desc mt-1 text-xs font-semibold text-primary">${detail}</p>` : ''}
        </div>`;

    const comparisonRows = (data) => [
        ['Посещения', data.previousVisits, data.visits, `+${data.visits - data.previousVisits}`],
        ['Новые города', data.previousCities, data.cities, `+${data.cities}`],
        ['Повторные посещения', data.previousRepeats, data.repeats, 'без изменений'],
        ['Страны', data.previousCountries, data.countries, 'без изменений'],
    ].map(([label, before, after, change]) => `
        <div class="dui-list-row grid-cols-[1fr_auto_auto] items-center gap-4 border-b border-base-300 px-0 py-4 last:border-0">
            <div><p class="font-semibold">${label}</p><p class="text-xs text-base-content/55">${change}</p></div>
            <div class="text-right"><p class="text-xs text-base-content/45">2023</p><strong class="text-xl tabular-nums">${before}</strong></div>
            <div class="min-w-16 rounded-box bg-primary/10 p-2 text-right text-primary"><p class="text-xs">2025</p><strong class="text-xl tabular-nums">${after}</strong></div>
        </div>`).join('');

    function specialContent(data, visual) {
        if (data.mode === 'compare') {
            return `<div class="grid gap-5 lg:grid-cols-[1.1fr_.9fr]">
                <section class="dui-card bg-base-100 shadow-sm ring-1 ring-base-300"><div class="dui-card-body">
                    <span class="dui-badge dui-badge-outline">Сопоставимые полные годы</span>
                    <h2 class="dui-card-title mt-2 text-2xl">${data.title}</h2><div class="dui-list">${comparisonRows(data)}</div>
                </div></section>
                <aside class="space-y-4">${mapArtwork(true)}
                    <div class="dui-alert dui-alert-info dui-alert-soft"><span>${data.note}</span></div>
                    <div class="dui-card border border-base-300 bg-base-100"><div class="dui-card-body p-5"><p class="text-xs uppercase tracking-widest text-base-content/50">Автоматический вывод</p><p class="mt-2 text-lg font-semibold">${data.insight}</p></div></div>
                </aside></div>`;
        }
        if (data.mode === 'teaser') {
            return `<div class="dui-card mx-auto max-w-5xl overflow-hidden bg-neutral text-neutral-content shadow-xl">
                <div class="grid lg:grid-cols-2">
                    <div class="p-7 sm:p-10"><span class="dui-badge dui-badge-warning">Персональный тизер</span><p class="mt-8 text-sm opacity-60">${data.kicker}</p>
                        <h2 class="mt-2 text-3xl font-black sm:text-5xl">${data.title}</h2><p class="mt-5 max-w-lg opacity-75">${data.intro}</p>
                        <div class="dui-stats dui-stats-horizontal mt-8 bg-transparent text-neutral-content shadow-none">${metric(data.visits, 'посещений')}${metric(data.cities, 'новых городов')}${metric(data.countries, 'страны')}</div>
                        <button type="button" class="dui-btn dui-btn-primary mt-9" data-upgrade-preview>Посмотреть с расширенным тарифом</button>
                        <p class="mt-3 text-xs opacity-55">Без списания. В прототипе откроется полный сценарий.</p>
                    </div>
                    <div class="relative min-h-96 bg-base-100/10 p-7 sm:p-10"><div class="space-y-4 blur-[7px]" aria-hidden="true">${mapArtwork(true)}<div class="grid grid-cols-2 gap-3"><div class="h-24 rounded-box bg-white/20"></div><div class="h-24 rounded-box bg-white/20"></div></div></div>
                        <div class="absolute inset-0 flex items-center justify-center bg-neutral/25 p-8 text-center"><div><div class="mx-auto flex size-14 items-center justify-center rounded-full bg-white/15 text-2xl">↗</div><p class="mt-4 text-xl font-bold">Ещё 4 наблюдения, карта и готовые карточки</p></div></div>
                    </div>
                </div></div>`;
        }
        if (data.mode === 'archive') {
            if (state.archiveDeleted) return `<div class="dui-alert mx-auto max-w-3xl"><span>Снимок удалён из памяти прототипа. Исходные посещения не изменились.</span><button class="dui-btn dui-btn-sm" data-restore-archive>Вернуть для демо</button></div>`;
            return `<div class="mx-auto max-w-5xl"><div class="dui-alert dui-alert-warning dui-alert-soft mb-5"><div><strong>Расширенный тариф закончился</strong><p class="text-sm">Снимки хранятся, но их содержимое и публикации временно скрыты.</p></div><button class="dui-btn dui-btn-sm" data-upgrade-preview>Возобновить</button></div>
                <article class="dui-card bg-base-100 shadow-sm ring-1 ring-base-300"><div class="dui-card-body gap-5 sm:flex-row sm:items-center">
                    <div class="flex size-24 shrink-0 items-center justify-center rounded-box bg-base-200 text-3xl">🔒</div><div class="min-w-0 flex-1"><div class="flex flex-wrap items-center gap-2"><h2 class="dui-card-title">Итоги 2025 года</h2><span class="dui-badge dui-badge-outline">снимок</span></div><p class="mt-2 text-sm text-base-content/60">Сохранён 8 января 2026 · 14 посещений · 9 новых городов</p><p class="mt-2 text-sm">Исходные посещения и фотографии доступны в обычных разделах.</p></div>
                    <div class="flex shrink-0 flex-col gap-2"><button class="dui-btn dui-btn-primary dui-btn-sm" data-upgrade-preview>Открыть снова</button><button class="dui-btn dui-btn-error dui-btn-outline dui-btn-sm" data-delete-archive>Удалить снимок</button></div>
                </div></article></div>`;
        }
        if (data.mode === 'studio') return studioContent(visual);
        return '';
    }

    function studioContent(visual) {
        const templates = [
            ['map', 'Картографический', 'линии маршрута'], ['magazine', 'Журнальный', 'крупная типографика'],
            ['stats', 'Статистический', 'числа без декора'], ['celebration', 'Праздничный', 'итог года'],
            ['photos', 'Фотодневник', 'выбранные кадры'],
        ];
        const previewClass = state.theme === 'dark' ? 'bg-slate-950 text-white' : 'bg-[#f6f1e7] text-slate-900';
        const accent = { 'Кобальт': 'bg-blue-600', 'Мандарин': 'bg-orange-500', 'Хвоя': 'bg-emerald-700' }[state.accent];
        const ratio = { '1:1': 'aspect-square', '9:16': 'aspect-[9/16] max-h-[640px]', '16:9': 'aspect-video' }[state.format];
        const cards = {
            map: `<p class="text-xs font-bold uppercase tracking-[.25em] opacity-55">Итоги путешествий · 2025</p><h3 class="mt-5 max-w-lg text-3xl font-black sm:text-5xl">9 новых городов на личной карте</h3>${state.blocks.has('Карта') ? `<div class="mt-7">${mapArtwork(true)}</div>` : ''}`,
            magazine: `<div class="grid h-full content-between gap-6 sm:grid-cols-[.8fr_1.2fr]"><div><p class="font-serif text-7xl italic sm:text-9xl">2025</p><p class="mt-3 text-xs font-bold uppercase tracking-[.25em] opacity-55">Личный ежегодник</p></div><div class="border-l border-current/25 pl-5"><h3 class="font-serif text-3xl font-black sm:text-5xl">Год, в котором дороги вели дальше</h3>${state.blocks.has('Карта') ? `<div class="mt-6">${mapArtwork(true)}</div>` : ''}</div></div>`,
            stats: `<p class="text-xs font-bold uppercase tracking-[.3em] opacity-55">Итоги · только главное</p><div class="mt-8 flex items-end gap-4"><strong class="text-8xl font-black tabular-nums sm:text-9xl">09</strong><span class="mb-4 max-w-28 text-sm font-bold uppercase">новых городов</span></div><div class="mt-8 h-px bg-current/25"></div><p class="mt-6 text-2xl font-semibold">14 посещений · 3 страны · 5 возвращений</p>`,
            celebration: `<div class="text-center"><p class="text-5xl">✦</p><p class="mt-5 text-xs font-bold uppercase tracking-[.3em] opacity-55">Ваш 2025 год</p><h3 class="mx-auto mt-5 max-w-lg text-4xl font-black sm:text-6xl">Девять новых поводов праздновать</h3><div class="mx-auto mt-8 flex max-w-md justify-around text-2xl"><span>✦</span><span>9</span><span>✦</span><span>14</span><span>✦</span></div></div>`,
            photos: `<p class="text-xs font-bold uppercase tracking-[.25em] opacity-55">Фотодневник · 2025</p><h3 class="mt-5 text-3xl font-black sm:text-5xl">Места, которые остались с вами</h3>${photoStrip()}`,
        };
        return `<div class="grid gap-5 xl:grid-cols-[18rem_minmax(0,1fr)_20rem]">
            <aside class="space-y-3"><h2 class="text-sm font-bold uppercase tracking-widest text-base-content/50">1. Направление</h2>${templates.map(([key, name, note]) => `<button type="button" data-template="${key}" class="dui-btn h-auto w-full justify-start py-4 text-left ${state.template === key ? 'dui-btn-primary' : 'dui-btn-outline bg-base-100'}"><span><strong class="block">${name}</strong><span class="mt-1 block text-xs font-normal opacity-60">${note}</span></span></button>`).join('')}</aside>
            <section class="min-w-0"><div class="mb-3 flex items-center justify-between"><h2 class="text-sm font-bold uppercase tracking-widest text-base-content/50">2. Preview</h2><span class="dui-badge">${state.output === 'summary' ? 'Сводная карточка' : 'Серия · 4 карточки'}</span></div>
                <div class="relative mx-auto w-full max-w-2xl ${state.output === 'series' ? 'after:absolute after:inset-3 after:-z-10 after:translate-x-3 after:translate-y-3 after:rounded-[1.75rem] after:bg-base-300' : ''}"><div class="${ratio} ${previewClass} relative w-full overflow-hidden rounded-[1.75rem] p-7 shadow-2xl sm:p-10">
                    <div class="absolute inset-x-0 top-0 h-2 ${accent}"></div>${cards[state.template]}
                    ${state.blocks.has('Показатели') ? `<div class="dui-stats dui-stats-horizontal mt-7 bg-transparent text-inherit shadow-none">${metric(14, 'посещений')}${metric(3, 'страны')}${metric(5, 'возвращений')}</div>` : ''}
                    ${state.blocks.has('Наблюдение') ? '<p class="mt-7 border-l-4 border-current pl-4 text-sm font-semibold opacity-75">Осень стала самым насыщенным сезоном.</p>' : ''}
                    ${state.watermark ? '<p class="absolute bottom-4 right-5 text-[10px] font-bold opacity-45">moi-goroda.ru</p>' : ''}
                </div></div>
            </section>
            <aside class="dui-card h-fit bg-base-100 shadow-sm ring-1 ring-base-300"><div class="dui-card-body gap-5"><h2 class="dui-card-title text-base">Настройки без редактора</h2>
                ${controlGroup('Формат', ['1:1', '9:16', '16:9'], state.format, 'format')}${controlGroup('Тема', ['light', 'dark'], state.theme, 'theme')}${controlGroup('Акцент', ['Кобальт', 'Мандарин', 'Хвоя'], state.accent, 'accent')}${controlGroup('Вывод', ['summary', 'series'], state.output, 'output')}
                <fieldset><legend class="mb-2 text-xs font-bold uppercase tracking-wide text-base-content/55">Блоки</legend>${['Карта', 'Показатели', 'Наблюдение'].map((block) => `<label class="dui-label cursor-pointer justify-start gap-3"><input type="checkbox" class="dui-checkbox dui-checkbox-sm" data-block="${block}" ${state.blocks.has(block) ? 'checked' : ''}><span>${block}</span></label>`).join('')}</fieldset>
                <label class="dui-label cursor-pointer justify-start gap-3"><input type="checkbox" class="dui-toggle dui-toggle-sm" data-watermark ${state.watermark ? 'checked' : ''}><span>Маркировка сервиса</span></label>
                ${state.template === 'photos' ? '<button class="dui-btn dui-btn-outline dui-btn-sm" data-photo-demo>Выбрать фотографии</button><button class="dui-btn dui-btn-ghost dui-btn-sm" data-clear-photos>Проверить без фотографий</button>' : ''}
                <button class="dui-btn dui-btn-primary">Скачать PNG</button><p class="text-center text-xs text-base-content/45">В прототипе файл не создаётся</p>
            </div></aside></div>`;
    }

    function controlGroup(label, options, current, action) {
        return `<fieldset><legend class="mb-2 text-xs font-bold uppercase tracking-wide text-base-content/55">${label}</legend><div class="flex flex-wrap gap-2">${options.map((option) => `<button type="button" data-setting="${action}" data-value="${option}" class="dui-btn dui-btn-xs ${current === option ? 'dui-btn-neutral' : 'dui-btn-outline'}">${option === 'summary' ? 'Одна' : option === 'series' ? 'Серия' : option === 'light' ? 'Светлая' : option === 'dark' ? 'Тёмная' : option}</button>`).join('')}</div></fieldset>`;
    }

    function photoStrip() {
        if (!state.selectedPhotos.size) return '<div class="dui-alert mt-6 bg-current/5 text-inherit"><span>Фотографии не выбраны. Макет остаётся полноценным и не подставляет снимки автоматически.</span></div>';
        return `<div class="mt-6 grid grid-cols-3 gap-2">${[...state.selectedPhotos].map((number) => `<div class="aspect-square rounded-box bg-gradient-to-br ${number === 1 ? 'from-amber-200 to-orange-500' : number === 2 ? 'from-cyan-200 to-blue-600' : 'from-emerald-200 to-teal-700'}"></div>`).join('')}</div>`;
    }

    function variantA(data) {
        if (data.mode !== 'summary') return `<header class="mb-7 text-center"><p class="text-xs font-bold uppercase tracking-[.25em] text-primary">Вариант A · направляемый сценарий</p><h2 class="mt-2 text-3xl font-black">${data.kicker}</h2></header>${specialContent(data, 'A')}`;
        const chapters = [
            `<div class="grid items-center gap-8 lg:grid-cols-2"><div><span class="dui-badge dui-badge-primary dui-badge-outline">Глава 1 из 4</span><p class="mt-8 text-sm font-bold uppercase tracking-[.25em] text-primary">${data.kicker}</p><h2 class="mt-3 text-4xl font-black leading-tight sm:text-6xl">${data.title}</h2><p class="mt-5 max-w-xl text-lg text-base-content/65">${data.intro}</p></div>${mapArtwork()}</div>`,
            `<div class="mx-auto max-w-5xl"><span class="dui-badge dui-badge-primary dui-badge-outline">Глава 2 из 4</span><h2 class="mt-6 text-3xl font-black sm:text-5xl">Ритм года в четырёх числах</h2><div class="dui-stats dui-stats-vertical mt-10 w-full bg-base-100 p-6 shadow-sm ring-1 ring-base-300 sm:dui-stats-horizontal sm:p-10">${metric(data.visits, 'посещений')}${metric(data.cities, 'новых городов')}${metric(data.repeats, 'возвращений')}${metric(data.countries, 'страны')}</div><p class="mt-6 text-sm text-base-content/55">${data.note}</p></div>`,
            `<div class="mx-auto grid max-w-5xl gap-7 lg:grid-cols-[.8fr_1.2fr]"><div><span class="dui-badge dui-badge-primary dui-badge-outline">Глава 3 из 4</span><h2 class="mt-6 text-3xl font-black sm:text-5xl">Маршрут запомнился не только новыми точками</h2><p class="mt-6 text-lg text-base-content/65">${data.insight}</p></div><ol class="dui-list gap-3">${data.route.map((city, index) => `<li class="dui-list-row bg-base-100 ring-1 ring-base-300"><span class="dui-badge dui-badge-primary size-9 rounded-full">${index + 1}</span><strong>${city}</strong></li>`).join('')}</ol></div>`,
            `<div class="mx-auto max-w-4xl text-center"><span class="dui-badge dui-badge-primary dui-badge-outline">Глава 4 из 4</span><p class="mt-8 text-7xl">✦</p><h2 class="mt-5 text-3xl font-black sm:text-5xl">${data.record || 'Этот год занял своё место в вашей истории'}</h2><p class="mx-auto mt-5 max-w-2xl text-lg text-base-content/60">Итог можно сохранить снимком или собрать в карточки для публикации.</p><div class="mt-8 flex flex-wrap justify-center gap-3"><button class="dui-btn dui-btn-primary" data-open-studio>Собрать карточки</button><button class="dui-btn dui-btn-outline">Сохранить снимок</button></div></div>`,
        ];
        return `<div class="dui-card bg-base-100 shadow-sm ring-1 ring-base-300 lg:min-h-[650px]"><div class="dui-card-body px-5 py-8 sm:px-10 sm:py-12 lg:px-14"><div class="dui-join mb-8 flex">${chapters.map((_, index) => `<button class="dui-btn dui-btn-xs dui-join-item flex-1 ${index <= state.storyStep ? 'dui-btn-primary' : ''}" data-story-step="${index}" aria-label="Открыть главу ${index + 1}"></button>`).join('')}</div>${chapters[state.storyStep]}<div class="dui-card-actions mt-10 justify-between"><button class="dui-btn dui-btn-ghost" data-story-prev ${state.storyStep === 0 ? 'disabled' : ''}>← Назад</button><button class="dui-btn dui-btn-neutral" data-story-next>${state.storyStep === chapters.length - 1 ? 'Сначала' : 'Дальше →'}</button></div></div></div>`;
    }

    function variantB(data) {
        if (data.mode !== 'summary') return `<div class="mb-7 border-b-4 border-neutral pb-5"><p class="text-xs font-bold uppercase tracking-[.3em]">Вариант B · личный ежегодник</p><h2 class="mt-2 font-serif text-4xl font-black sm:text-6xl">${data.kicker}</h2></div>${specialContent(data, 'B')}`;
        return `<article class="overflow-hidden rounded-sm bg-[#f4eddf] text-slate-900 shadow-xl ring-1 ring-black/10">
            <header class="grid border-b border-slate-900 lg:grid-cols-[1fr_auto]"><div class="p-6 sm:p-10"><p class="text-xs font-bold uppercase tracking-[.35em]">Личный ежегодник · ${data.period}</p><h2 class="mt-5 max-w-4xl font-serif text-5xl font-black leading-[.9] sm:text-7xl">${data.title}</h2></div><div class="flex min-w-40 items-end justify-end bg-slate-900 p-6 text-[#f4eddf] sm:p-10"><span class="font-serif text-7xl italic">${data.cities}</span><span class="mb-2 ml-2 text-xs uppercase">новых<br>городов</span></div></header>
            <div class="grid lg:grid-cols-[1.35fr_.65fr]"><div class="border-b border-slate-900 p-5 sm:p-8 lg:border-b-0 lg:border-r">${mapArtwork()}<p class="mt-5 columns-1 font-serif text-lg leading-relaxed sm:columns-2">${data.intro} ${data.insight}</p></div>
            <aside class="p-6 sm:p-8"><p class="text-xs font-black uppercase tracking-[.3em]">Год в деталях</p><div class="dui-stats dui-stats-vertical mt-7 bg-transparent text-slate-900 shadow-none">${metric(data.visits, 'посещений')}${metric(data.repeats, 'повторных посещений')}${metric(data.countries, 'посещённые страны')}${metric(data.days, 'дней с датированными посещениями')}</div>${data.record ? `<div class="mt-9 border-y border-slate-900 py-5"><p class="text-xs font-bold uppercase">Личный рекорд</p><p class="mt-2 font-serif text-xl font-bold">${data.record}</p></div>` : `<div class="mt-9 border-y border-slate-900 py-5"><p class="font-serif text-lg">Никакой гонки: этот год важен сам по себе.</p></div>`}<p class="mt-7 text-xs leading-relaxed opacity-60">${data.note}</p></aside></div>
            <footer class="flex flex-wrap items-center justify-between gap-4 bg-slate-900 px-6 py-5 text-[#f4eddf] sm:px-10"><p class="font-serif italic">${data.route.join(' · ')}</p><button class="dui-btn dui-btn-sm bg-[#f4eddf] text-slate-900" data-open-studio>Собрать выпуск</button></footer></article>`;
    }

    function variantC(data) {
        const special = data.mode !== 'summary' ? specialContent(data, 'C') : '';
        return `<div class="grid gap-4 lg:grid-cols-[15rem_minmax(0,1fr)]">
            <aside class="dui-card h-fit bg-neutral text-neutral-content lg:sticky lg:top-4"><div class="dui-card-body p-4"><p class="text-xs font-bold uppercase tracking-widest opacity-50">Вариант C</p><h2 class="text-xl font-black">Панель исследователя</h2><div class="dui-divider opacity-30"></div>
                ${['Обзор периода', 'Наблюдения', 'Сравнение', 'Личные рекорды', 'Снимки', 'Публикация'].map((label, index) => `<button type="button" class="dui-btn justify-start ${index === (data.mode === 'summary' ? 0 : data.mode === 'compare' ? 2 : data.mode === 'archive' ? 4 : data.mode === 'studio' ? 5 : 1) ? 'bg-white text-neutral' : 'dui-btn-ghost'}">${label}</button>`).join('')}
                <div class="dui-stats dui-stats-vertical mt-3 bg-white/10 text-neutral-content shadow-none"><div class="dui-stat p-3"><p class="dui-stat-title text-xs text-neutral-content/55">Текущий период</p><strong class="dui-stat-value text-sm">${data.period}</strong></div><div class="dui-stat p-3"><p class="dui-stat-title text-xs text-neutral-content/55">Доступ</p><strong class="dui-stat-value text-sm">${data.access}</strong></div></div></div></aside>
            <div class="min-w-0">${special || `<header class="dui-card mb-4 bg-base-100 ring-1 ring-base-300"><div class="dui-card-body flex-col gap-4 p-5 sm:flex-row sm:items-end sm:justify-between"><div><p class="text-xs font-bold uppercase tracking-widest text-primary">${data.kicker}</p><h2 class="mt-2 text-3xl font-black">${data.title}</h2><p class="mt-2 max-w-3xl text-sm text-base-content/60">${data.intro}</p></div><button class="dui-btn dui-btn-primary dui-btn-sm" data-open-studio>Создать публикацию</button></div></header>
                <div class="dui-stats dui-stats-vertical w-full bg-base-100 shadow-sm ring-1 ring-base-300 md:dui-stats-horizontal">${metric(data.visits, 'посещений')}${metric(data.cities, 'новых городов')}${metric(data.repeats, 'возвращений')}${metric(data.countries, 'страны')}</div>
                <div class="mt-4 grid gap-4 xl:grid-cols-[1.35fr_.65fr]"><div class="dui-card bg-base-100 ring-1 ring-base-300"><div class="dui-card-body p-4">${mapArtwork()}<div class="mt-4 flex flex-wrap gap-2">${data.route.map((city) => `<span class="dui-badge dui-badge-outline">${city}</span>`).join('')}</div></div></div><div class="space-y-4"><div class="dui-alert dui-alert-info dui-alert-soft"><span>${data.insight}</span></div>${data.record ? `<div class="dui-card border-l-4 border-primary bg-base-100 ring-1 ring-base-300"><div class="dui-card-body p-5"><p class="text-xs font-bold uppercase tracking-widest text-primary">Личный рекорд</p><p class="mt-2 font-semibold">${data.record}</p></div></div>` : ''}<div class="dui-card bg-base-100 ring-1 ring-base-300"><div class="dui-card-body p-5 text-sm">${data.note}</div></div></div></div>`}</div></div>`;
    }

    function updateUrl() {
        const next = new URL(window.location.href);
        next.searchParams.set('variant', state.variant);
        next.searchParams.set('scenario', state.scenario);
        window.history.replaceState({}, '', next);
    }

    function render() {
        const data = scenarios[state.scenario];
        root.querySelector('[data-scenario-nav]').innerHTML = Object.entries(scenarios).map(([key, scenario]) => `<button type="button" data-scenario="${key}" class="dui-btn dui-btn-sm shrink-0 ${key === state.scenario ? 'dui-btn-neutral' : 'bg-base-100'}">${scenario.short}</button>`).join('');
        root.querySelector('[data-variant="A"]').innerHTML = variantA(data);
        root.querySelector('[data-variant="B"]').innerHTML = variantB(data);
        root.querySelector('[data-variant="C"]').innerHTML = variantC(data);
        root.querySelectorAll('[data-variant]').forEach((element) => { element.hidden = element.dataset.variant !== state.variant; });
        const variant = variants.find((item) => item.key === state.variant);
        root.querySelector('[data-variant-label]').textContent = `${variant.key} · ${variant.name}`;
        const publication = data.mode === 'studio' ? `${state.output === 'summary' ? 'одна' : 'серия'} · ${state.format} · ${state.template}` : data.publication;
        const values = { variant: `${variant.key} · ${variant.name}`, scenario: data.short, period: data.period, access: data.access, mode: data.mode, publication };
        Object.entries(values).forEach(([key, value]) => { root.querySelector(`[data-state="${key}"]`).textContent = value; });
        updateUrl();
    }

    function cycleVariant(direction) {
        const current = variants.findIndex((item) => item.key === state.variant);
        state.variant = variants[(current + direction + variants.length) % variants.length].key;
        render();
    }

    root.addEventListener('click', (event) => {
        const target = event.target.closest('button');
        if (!target) return;
        if (target.matches('[data-variant-previous]')) cycleVariant(-1);
        if (target.matches('[data-variant-next]')) cycleVariant(1);
        if (target.dataset.scenario) { state.scenario = target.dataset.scenario; state.storyStep = 0; render(); }
        if (target.matches('[data-story-prev]')) { state.storyStep = Math.max(0, state.storyStep - 1); render(); }
        if (target.matches('[data-story-next]')) { state.storyStep = (state.storyStep + 1) % 4; render(); }
        if (target.dataset.storyStep) { state.storyStep = Number(target.dataset.storyStep); render(); }
        if (target.matches('[data-open-studio]')) { state.scenario = 'studio'; state.storyStep = 0; render(); }
        if (target.matches('[data-upgrade-preview]')) { state.scenario = 'rich'; render(); }
        if (target.matches('[data-delete-archive]')) { state.archiveDeleted = true; render(); }
        if (target.matches('[data-restore-archive]')) { state.archiveDeleted = false; render(); }
        if (target.dataset.template) { state.template = target.dataset.template; render(); }
        if (target.dataset.setting) { state[target.dataset.setting] = target.dataset.value; render(); }
        if (target.matches('[data-photo-demo]')) { state.selectedPhotos = new Set([1, 2, 3]); render(); }
        if (target.matches('[data-clear-photos]')) { state.selectedPhotos.clear(); render(); }
        if (target.matches('[data-toggle-state]')) {
            const panel = root.querySelector('[data-state-panel]');
            panel.classList.toggle('hidden');
            target.textContent = panel.classList.contains('hidden') ? 'Показать состояние' : 'Скрыть состояние';
        }
    });

    root.addEventListener('change', (event) => {
        if (event.target.matches('[data-block]')) {
            event.target.checked ? state.blocks.add(event.target.dataset.block) : state.blocks.delete(event.target.dataset.block);
            render();
        }
        if (event.target.matches('[data-watermark]')) { state.watermark = event.target.checked; render(); }
    });

    document.addEventListener('keydown', (event) => {
        if (!['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
        if (event.target.matches('input, textarea, select, [contenteditable]')) return;
        cycleVariant(event.key === 'ArrowLeft' ? -1 : 1);
    });

    render();
}
