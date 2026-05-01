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
- `styles/index.css` — агрегатор: combobox, select-search, **badge**, **progress** (классы `.badge*`, `.progress*`, без JS-виджетов).
- **Бейджи** — чисто CSS: `styles/badge.css`. Отдельного шаблона/JS в библиотеке нет: в разметке используйте классы `badge`, `badge-soft-*` и т.д. (см. демо в проекте).
- **Прогресс-бары** — чисто CSS: `styles/progress.css`. Отдельного шаблона/JS в библиотеке нет: в разметке используйте классы `progress`, `progress-bar-*`, `progress-circular`, `progress-gauge` и т.д. (см. демо в проекте).

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

## Progress bars (прогресс-бары)

Чисто CSS-примитив без JavaScript-логики. Использует только классы Tailwind.

### Базовый прогресс-бар (горизонтальный)

```html
<!-- Базовый прогресс-бар -->
<div class="progress progress-md" role="progressbar" aria-valuenow="75" aria-valuemin="0" aria-valuemax="100">
  <div class="progress-bar progress-bar-primary" style="width: 75%">
    <span class="sr-only">75% завершено</span>
  </div>
</div>

<!-- С текстом внутри -->
<div class="progress progress-md" role="progressbar" aria-valuenow="50" aria-valuemin="0" aria-valuemax="100">
  <div class="progress-bar progress-bar-primary" style="width: 50%">50%</div>
</div>

<!-- С лейблом справа -->
<div class="progress-with-label">
  <div class="progress progress-sm" role="progressbar" aria-valuenow="75" aria-valuemin="0" aria-valuemax="100">
    <div class="progress-bar progress-bar-primary" style="width: 75%">
      <span class="sr-only">75% завершено</span>
    </div>
  </div>
  <span class="progress-label">75%</span>
</div>
```

### Размеры

- `.progress-xs` — h-1.5
- `.progress-sm` — h-2 (по умолчанию)
- `.progress-md` — h-4
- `.progress-lg` — h-6

### Цвета

- `.progress-bar-primary` — основной цвет
- `.progress-bar-secondary` — вторичный
- `.progress-bar-success` — зелёный (teal-500)
- `.progress-bar-danger` — красный
- `.progress-bar-warning` — жёлтый
- `.progress-bar-info` — серый (surface-4)
- `.progress-bar-plain` — нейтральный

### Вертикальный прогресс-бар

```html
<div class="progress progress-vertical progress-vertical-sm h-32" role="progressbar" aria-valuenow="75" aria-valuemin="0" aria-valuemax="100">
  <div class="progress-bar progress-bar-primary" style="height: 75%">
    <span class="sr-only">75% завершено</span>
  </div>
</div>
```

### Сегментированный

```html
<div class="progress-segmented" role="progressbar" aria-valuenow="50" aria-valuemin="0" aria-valuemax="100">
  <div class="progress-segment progress-segment-active"></div>
  <div class="progress-segment progress-segment-active"></div>
  <div class="progress-segment progress-segment-inactive"></div>
  <div class="progress-segment progress-segment-inactive"></div>
</div>
```

### Круглый (circular)

```html
<div class="progress-circular progress-circular-lg" role="progressbar" aria-valuenow="75" aria-valuemin="0" aria-valuemax="100">
  <svg viewBox="0 0 36 36" xmlns="http://www.w3.org/2000/svg">
    <circle cx="18" cy="18" r="16" fill="none" class="progress-circular-bg" stroke-width="2"></circle>
    <circle cx="18" cy="18" r="16" fill="none" class="progress-circular-bar" stroke-width="2" stroke-dasharray="100" stroke-dashoffset="25" stroke-linecap="round"></circle>
  </svg>
  <div class="progress-circular-text">75%</div>
</div>
```

### Gauge (неполный круг)

```html
<div class="progress-gauge progress-gauge-lg progress-gauge-rotate-135" role="progressbar" aria-valuenow="75" aria-valuemin="0" aria-valuemax="100">
  <svg viewBox="0 0 36 36" xmlns="http://www.w3.org/2000/svg">
    <circle cx="18" cy="18" r="16" fill="none" class="progress-gauge-bg" stroke-width="1" stroke-dasharray="75 100" stroke-linecap="round"></circle>
    <circle cx="18" cy="18" r="16" fill="none" class="progress-gauge-bar" stroke-width="2" stroke-dasharray="56.25 100" stroke-linecap="round"></circle>
  </svg>
  <div class="progress-gauge-text">
    <span class="progress-gauge-value">75</span>
    <span class="progress-gauge-label">Score</span>
  </div>
</div>
```

Цветовые варианты gauge: `.progress-gauge-purple`, `.progress-gauge-green`, `.progress-gauge-orange`.

Подробнее см. демо-страницу `/ui-demo/progress/`
