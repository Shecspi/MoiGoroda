/**
 * Минимальная разметка, совместимая с контроллерами ui-lib (как в Django include).
 */

/**
 * @param {object} [opts]
 * @param {string} [opts.minChars] data-mg-combobox-min-chars
 * @param {string} [opts.debounce] data-mg-combobox-debounce
 * @param {string} [opts.sourceUrl] data-mg-combobox-source-url
 * @param {string} [opts.openOnFocus] "true" | "false"
 */
export function buildStaticComboboxMarkup({
  id = 'cb-root',
  options = [
    { value: '1', label: 'Москва' },
    { value: '2', label: 'Тверь' },
    { value: '3', label: 'Смоленск' },
  ],
} = {}) {
  const li = (o) =>
    `<li data-mg-part="option" data-value="${o.value}" data-label="${o.label}"><span class="title">${o.label}</span></li>`;
  return `
    <div id="${id}" data-component="mg-combobox-static">
      <input type="text" data-mg-part="input" />
      <input type="hidden" data-mg-part="hidden-input" value="" />
      <ul data-mg-part="listbox" class="hidden" role="listbox">
        ${options.map(li).join('')}
      </ul>
    </div>
  `;
}

/**
 * @param {object} [opts] — см. buildStaticComboboxMarkup + URL для remote
 */
export function buildRemoteComboboxMarkup({
  id = 'cb-remote',
  sourceUrl = '/api/search',
  minChars = '0',
  debounce = '0',
  countryParam = '',
} = {}) {
  return `
    <div
      id="${id}"
      data-component="mg-combobox-remote"
      data-mg-combobox-source-url="${sourceUrl}"
      data-mg-combobox-query-param="query"
      data-mg-combobox-min-chars="${minChars}"
      data-mg-combobox-debounce="${debounce}"
      data-mg-combobox-value-key="value"
      data-mg-combobox-label-key="label"
      data-mg-combobox-loading-text="Загрузка..."
      data-mg-combobox-empty-text="Пусто"
      data-mg-combobox-country-url-param="${countryParam}"
    >
      <input type="text" data-mg-part="input" />
      <input type="hidden" data-mg-part="hidden-input" value="" />
      <ul data-mg-part="listbox" class="hidden" role="listbox"></ul>
    </div>
  `;
}

/**
 * @param {object} [opts]
 * @param {Array<{ value: string, label: string, selected?: boolean, disabled?: boolean }>} [opts.options]
 * @param {boolean} [opts.searchable] mg-select vs mg-select-searchable
 */
export function buildSelectMarkup({
  id = 'sel-root',
  selectId = 'id_test_select',
  searchable = false,
  options = [
    { value: 'a', label: 'Альфа' },
    { value: 'b', label: 'Бета', selected: true },
    { value: 'c', label: 'Гамма' },
  ],
} = {}) {
  const opts = options
    .map(
      (o) =>
        `<option value="${o.value}"${o.disabled ? ' disabled' : ''}${o.selected ? ' selected' : ''}>${o.label}</option>`,
    )
    .join('');
  const comp = searchable ? 'mg-select-searchable' : 'mg-select';
  const searchField = searchable
    ? `<div class="wrap">
        <input type="text" data-mg-part="search-input" class="w" autocomplete="off" />
      </div>`
    : '';
  return `
    <div id="${id}" data-component="${comp}" data-mg-select-placeholder="Выберите" data-mg-select-empty-text="Нет">
      <select id="${selectId}" data-mg-part="native-select">
        ${opts}
      </select>
      <div class="relative">
        <button type="button" data-mg-part="toggle">
          <span data-mg-part="toggle-label">Label</span>
        </button>
        <div data-mg-part="dropdown" class="hidden">
          ${searchField}
          <ul data-mg-part="options-list" role="listbox"></ul>
        </div>
      </div>
    </div>
  `;
}
