# Переносимая UI-библиотека (без Django)

Эта папка содержит переносимый слой интеграции для UI-компонентов на Data-API.

## Именование

- **`data-component`** — всегда с префиксом `mg-`: `mg-combobox-static`, `mg-combobox-remote`, `mg-select-search`.
- **Настройки** — `data-mg-<тот же slug, что и в имени компонента>-<параметр>`: `data-mg-combobox-min-chars`, `data-mg-combobox-source-url`, `data-mg-select-search-placeholder`, `data-mg-select-search-filter-placeholder` (плейсхолдер поля фильтра в выпадашке).
- **Внутренние узлы** — `data-mg-part="..."` (`input`, `listbox`, `option`, `native-select`, …), не `data-role`.
- **CSS** — классы с префиксом `mg-`; корень `mg-select-search` в проекте занят стилями Preline, у виджета библиотеки корневой класс **`mg-ui-select-search`**.

## Файлы

- `index.js` — экспортирует API ядра и хелперы регистрации компонентов.
- `auto-init.js` — регистрирует компоненты по умолчанию и запускает `initAll(document)`.
- `styles/index.css` — агрегатор: combobox, select-search, **badge** (классы `.badge*`, без JS-виджета).
- **Бейджи** — чисто CSS: `styles/badge.css`. Отдельного шаблона/JS в библиотеке нет: в разметке используйте классы `badge`, `badge-soft-*` и т.д. (см. демо в проекте).

## Быстрый старт (любой frontend-проект)

1. Скопируйте в проект только папку `frontend/ui-lib/`.
2. Подключите агрегирующий файл стилей `ui-lib/styles/index.css` в вашу CSS-сборку.
3. Импортируйте `auto-init.js` один раз в entrypoint приложения.

```js
import './ui-lib/auto-init.js';
```

```css
/* Пример подключения в глобальный файл стилей */
@import './ui-lib/styles/index.css';
```

### Tailwind-стили в `ui-lib/styles/*.css`

```css
@layer components {
  .mg-combobox {
    @apply w-full;
  }

  .mg-combobox-dropdown {
    @apply absolute z-30 mt-1 max-h-64 w-full overflow-auto rounded-lg border border-gray-200 bg-white p-1 shadow-lg dark:border-neutral-700 dark:bg-neutral-900;
  }

  .mg-combobox-option {
    @apply cursor-pointer rounded-md px-3 py-2 text-sm text-gray-800 transition hover:bg-gray-100 dark:text-neutral-200 dark:hover:bg-neutral-800;
  }

  .mg-combobox-option-title {
    @apply block truncate;
  }

  .mg-combobox-option.has-meta .mg-combobox-option-title {
    @apply font-semibold;
  }

  .mg-combobox-option-meta {
    @apply mt-0.5 block text-xs text-gray-500 dark:text-neutral-400;
  }

  /* .mg-combobox-option.is-active — см. styles/combobox.css */

  .mg-combobox-empty {
    @apply px-3 py-2 text-sm text-gray-500 dark:text-neutral-400;
  }
}
```

## Static combobox (предзагруженные данные)

Используйте обычный HTML с `data-*` атрибутами:

```html
<div
  id="city-combobox"
  data-component="mg-combobox-static"
  data-mg-combobox-min-chars="1"
  data-mg-combobox-max-items="20"
  data-mg-combobox-open-on-focus="true"
  data-mg-combobox-autoselect-first="true"
>
  <div style="position: relative;">
    <input data-mg-part="input" type="text" placeholder="Начните вводить город..." />
    <input data-mg-part="hidden-input" name="city_id" type="hidden" />
    <ul data-mg-part="listbox" class="mg-combobox-dropdown hidden">
      <li data-mg-part="option" data-value="1" data-label="Москва" class="mg-combobox-option">
        <span class="mg-combobox-option-title">Москва</span>
      </li>
      <li data-mg-part="option" data-value="2" data-label="Казань" class="mg-combobox-option">
        <span class="mg-combobox-option-title">Казань</span>
      </li>
    </ul>
  </div>
</div>
```

## Remote combobox (загрузка из API)

Чтобы загружать варианты с API:

```html
<div
  data-component="mg-combobox-remote"
  data-mg-combobox-source-url="/api/city/search"
  data-mg-combobox-query-param="query"
  data-mg-combobox-country-url-param="country"
  data-mg-combobox-value-key="id"
  data-mg-combobox-label-key="title"
  data-mg-combobox-meta-keys="region,country"
  data-mg-combobox-debounce="300"
></div>
```

## Select search (поиск по select options)

`mg-select-search` — самостоятельный компонент ui-lib для фильтрации `option` в нативном `select`.
Компонент использует нативный `select` как источник данных и синхронизирует выбор обратно в него.

```html
<div
  class="mg-ui-select-search"
  data-component="mg-select-search"
  data-mg-select-search-placeholder="Выберите страну"
  data-mg-select-search-filter-placeholder="Поиск..."
>
  <select id="id_country" data-mg-part="native-select" class="hidden">
    <option value="">Выберите страну</option>
    <option value="RU">Россия</option>
    <option value="KZ">Казахстан</option>
  </select>
</div>
```

## События

Подписка на события корневого узла combobox:

```js
const node = document.getElementById('city-combobox');
node.addEventListener('mg:combobox:select', (event) => {
  const { value, label, source } = event.detail;
  console.log(value, label, source);
});
```

## Динамический DOM

Если HTML добавляется позже (AJAX/модалка), вызывайте:

```js
window.MGUi.initAll(containerElement);
window.MGUi.destroyAll(containerElement);
```
