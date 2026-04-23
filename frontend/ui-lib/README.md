# Переносимая UI-библиотека (без Django)

Эта папка содержит переносимый слой интеграции для UI-компонентов на Data-API.

## Файлы

- `index.js` — экспортирует API ядра и хелперы регистрации компонентов.
- `auto-init.js` — регистрирует компоненты по умолчанию и запускает `initAll(document)`.

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

  .mg-combobox-option.is-active {
    @apply bg-blue-50 text-blue-700 dark:bg-blue-500/20 dark:text-blue-200;
  }

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
  data-component="combobox-static"
  data-combobox-min-chars="1"
  data-combobox-max-items="20"
  data-combobox-open-on-focus="true"
  data-combobox-autoselect-first="true"
>
  <div style="position: relative;">
    <input data-role="input" type="text" placeholder="Начните вводить город..." />
    <input data-role="hidden-input" name="city_id" type="hidden" />
    <ul data-role="listbox" class="mg-combobox-dropdown hidden">
      <li data-role="option" data-value="1" data-label="Москва" class="mg-combobox-option">
        <span class="mg-combobox-option-title">Москва</span>
      </li>
      <li data-role="option" data-value="2" data-label="Казань" class="mg-combobox-option">
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
  data-component="combobox-remote"
  data-combobox-source-url="/api/city/search"
  data-combobox-query-param="query"
  data-combobox-country-url-param="country"
  data-combobox-value-key="id"
  data-combobox-label-key="title"
  data-combobox-meta-keys="region,country"
  data-combobox-debounce="300"
></div>
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
