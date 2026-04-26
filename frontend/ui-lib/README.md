# Переносимая UI-библиотека (без Django)

Эта папка содержит переносимый слой интеграции для UI-компонентов на Data-API.

## Именование

- **`data-component`** — всегда с префиксом `mg-`: `mg-combobox-static`, `mg-combobox-remote`, `mg-select`, `mg-select-searchable`.
- **Настройки** — `data-mg-<тот же slug, что и в имени компонента>-<параметр>`: `data-mg-combobox-min-chars`, `data-mg-combobox-source-url`, `data-mg-select-placeholder`, `data-mg-select-searchable-filter-placeholder`.
- **Внутренние узлы** — `data-mg-part="..."` (`input`, `listbox`, `option`, `native-select`, …), не `data-role`.
- **CSS** — классы с префиксом `mg-`; корень `mg-select-search` в проекте занят стилями Preline, у виджета библиотеки корневой класс **`mg-ui-select-search`**.

## Файлы

- `index.js` — экспортирует API ядра и хелперы регистрации компонентов.
- `auto-init.js` — регистрирует компоненты по умолчанию и запускает `initAll(document)`.
- `styles/index.css` — агрегатор: combobox, select-search, **badge** (классы `.badge*`, без JS-виджета).
- **Бейджи** — чисто CSS: `styles/badge.css`. Отдельного шаблона/JS в библиотеке нет: в разметке используйте классы `badge`, `badge-soft-*` и т.д. (см. демо в проекте).

## Тесты (в каталоге `frontend/`)

Автотесты [Vitest](https://vitest.dev/) + [happy-dom](https://github.com/capricorn86/happy-dom) лежат в `ui-lib/**/*.test.js`; разметка-фикстуры — `ui-lib/test/fixtures.js`. Запуск из папки `frontend`:

```bash
npm test
# или непрерывно при разработке
npm run test:watch
```

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

## Select и Select searchable

`mg-select` — select без поля поиска.  
`mg-select-searchable` — select с полем поиска по `option`.  
Оба компонента используют нативный `select` как источник данных и синхронизируют выбор обратно в него.

### Когда использовать

- Используйте `mg-select`, когда список короткий и искать по нему не нужно (например, выбор года).
- Используйте `mg-select-searchable`, когда список длинный и пользователю нужна фильтрация.

### Через Django include

`mg-select` (без поиска):

```django
{% include "components/ui/select.html" with
  select_id="id_year"
  select_name="year"
  disabled=False
  placeholder="Выберите год"
  options=year_options
%}
```

`mg-select-searchable` (с поиском):

```django
{% include "components/ui/select_search.html" with
  select_id="id_country"
  select_name="country"
  disabled=False
  placeholder="Выберите страну"
  search_placeholder="Поиск..."
  options=country_options
%}
```

### Через Data API (чистый HTML)

`mg-select`:

```html
<div class="mg-ui-select-search" data-component="mg-select" data-mg-select-placeholder="Выберите год">
  <select id="id_year" data-mg-part="native-select" class="hidden">
    <option value="">Выберите год</option>
    <option value="2024">2024</option>
    <option value="2025">2025</option>
  </select>
  <!-- остальная разметка с data-mg-part совпадает с include components/ui/select.html -->
</div>
```

`mg-select-searchable`:

```html
<div
  class="mg-ui-select-search"
  data-component="mg-select-searchable"
  data-mg-select-placeholder="Выберите страну"
  data-mg-select-searchable-filter-placeholder="Поиск..."
>
  <select id="id_country" data-mg-part="native-select" class="hidden">
    <option value="">Выберите страну</option>
    <option value="RU">Россия</option>
    <option value="KZ">Казахстан</option>
  </select>
</div>
```

```html
<div
  class="mg-ui-select-search"
  data-component="mg-select-searchable"
  data-mg-select-placeholder="Выберите страну"
  data-mg-select-searchable-filter-placeholder="Поиск..."
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
