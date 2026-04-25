import { isEventOutside, parseBooleanAttr, parseNumberAttr } from '../utils/dom';

const HIDDEN_CLASS = 'hidden';

function dispatchComboboxEvent(root, name, detail = {}) {
  root.dispatchEvent(
    new CustomEvent(name, {
      detail,
      bubbles: true,
    }),
  );
}

class ComboboxBaseController {
  constructor(root) {
    this.root = root;
    this.input = root.querySelector('[data-mg-part="input"]');
    this.listbox = root.querySelector('[data-mg-part="listbox"]');
    this.hiddenInput = root.querySelector('[data-mg-part="hidden-input"]');
    this.optionNodes = Array.from(root.querySelectorAll('[data-mg-part="option"]'));

    this.state = {
      isOpen: false,
      query: '',
      activeIndex: -1,
      visibleOptions: this.optionNodes,
    };

    this.config = {
      openOnFocus: parseBooleanAttr(root.dataset.mgComboboxOpenOnFocus, true),
      minChars: Math.max(0, parseNumberAttr(root.dataset.mgComboboxMinChars, 0)),
      maxItems: Math.max(1, parseNumberAttr(root.dataset.mgComboboxMaxItems, 20)),
      autoSelectFirst: parseBooleanAttr(root.dataset.mgComboboxAutoselectFirst, true),
    };

    this.handleInput = this.handleInput.bind(this);
    this.handleFocus = this.handleFocus.bind(this);
    this.handleKeydown = this.handleKeydown.bind(this);
    this.handleDocumentPointerDown = this.handleDocumentPointerDown.bind(this);
    this.handleOptionClick = this.handleOptionClick.bind(this);
  }

  init() {
    if (!this.input || !this.listbox) {
      return;
    }

    this.ensureA11yAttributes();
    this.input.addEventListener('input', this.handleInput);
    this.input.addEventListener('focus', this.handleFocus);
    this.input.addEventListener('keydown', this.handleKeydown);
    this.listbox.addEventListener('click', this.handleOptionClick);
    document.addEventListener('pointerdown', this.handleDocumentPointerDown);
    this.onInit();
  }

  destroy() {
    if (!this.input || !this.listbox) {
      return;
    }

    this.input.removeEventListener('input', this.handleInput);
    this.input.removeEventListener('focus', this.handleFocus);
    this.input.removeEventListener('keydown', this.handleKeydown);
    this.listbox.removeEventListener('click', this.handleOptionClick);
    document.removeEventListener('pointerdown', this.handleDocumentPointerDown);
    this.onDestroy();
  }

  onInit() {
    this.filterOptions(this.input.value || '');
    this.close();
  }

  // For subclasses with custom cleanup (timers, inflight fetches).
  onDestroy() {}

  onQueryChange(query) {
    this.filterOptions(query);
    if (this.state.visibleOptions.length > 0) {
      this.open();
      if (this.config.autoSelectFirst) {
        this.setActiveIndex(0);
      }
    } else {
      this.close();
    }
  }

  onFocusOpen() {
    this.filterOptions(this.input.value || '');
    if (this.state.visibleOptions.length > 0) {
      this.open();
      if (this.config.autoSelectFirst) {
        this.setActiveIndex(0);
      }
    }
  }

  onBelowMinChars() {
    this.close();
    this.filterOptions('');
  }

  ensureA11yAttributes() {
    if (!this.listbox.id) {
      this.listbox.id = `mg-combobox-listbox-${Math.random().toString(36).slice(2, 10)}`;
    }

    this.input.setAttribute('role', 'combobox');
    this.input.setAttribute('aria-autocomplete', 'list');
    this.input.setAttribute('aria-expanded', 'false');
    this.input.setAttribute('aria-controls', this.listbox.id);
    this.listbox.setAttribute('role', 'listbox');

    this.optionNodes.forEach((option, index) => {
      option.setAttribute('role', 'option');
      if (!option.id) {
        option.id = `${this.listbox.id}-option-${index}`;
      }
      option.setAttribute('aria-selected', 'false');
    });
  }

  handleInput(event) {
    const query = event.target.value || '';
    this.state.query = query;

    if (query.length < this.config.minChars) {
      this.onBelowMinChars();
      return;
    }

    this.onQueryChange(query);
  }

  handleFocus() {
    if (!this.config.openOnFocus) {
      return;
    }

    this.onFocusOpen();
  }

  handleKeydown(event) {
    const { key } = event;

    if (key === 'ArrowDown') {
      event.preventDefault();
      if (!this.state.isOpen) {
        this.open();
        if (this.state.activeIndex < 0 && this.state.visibleOptions.length > 0) {
          this.setActiveIndex(0);
        }
        return;
      }
      this.moveActive(1);
      return;
    }

    if (key === 'ArrowUp') {
      event.preventDefault();
      if (!this.state.isOpen) {
        this.open();
        if (this.state.activeIndex < 0 && this.state.visibleOptions.length > 0) {
          this.setActiveIndex(this.state.visibleOptions.length - 1);
        }
        return;
      }
      this.moveActive(-1);
      return;
    }

    if (key === 'Enter') {
      if (this.state.isOpen && this.state.activeIndex >= 0) {
        event.preventDefault();
        const option = this.state.visibleOptions[this.state.activeIndex];
        this.selectOption(option, 'keyboard');
      }
      return;
    }

    if (key === 'Escape') {
      this.close();
      return;
    }

    if (key === 'Tab') {
      this.close();
    }
  }

  handleDocumentPointerDown(event) {
    if (isEventOutside(event, this.root)) {
      this.close();
    }
  }

  handleOptionClick(event) {
    const option = event.target.closest('[data-mg-part="option"]');
    if (!option || !this.listbox.contains(option)) {
      return;
    }

    this.selectOption(option, 'pointer');
  }

  moveActive(delta) {
    const options = this.state.visibleOptions;
    if (options.length === 0) {
      this.setActiveIndex(-1);
      return;
    }

    const currentIndex = this.state.activeIndex;
    const nextIndex = currentIndex < 0 ? 0 : (currentIndex + delta + options.length) % options.length;
    this.setActiveIndex(nextIndex);
  }

  setActiveIndex(index) {
    this.state.activeIndex = index;

    this.optionNodes.forEach((node) => {
      node.classList.remove('is-active');
      node.setAttribute('aria-selected', 'false');
    });

    if (index < 0 || index >= this.state.visibleOptions.length) {
      this.input.removeAttribute('aria-activedescendant');
      return;
    }

    const activeOption = this.state.visibleOptions[index];
    activeOption.classList.add('is-active');
    activeOption.setAttribute('aria-selected', 'true');
    this.input.setAttribute('aria-activedescendant', activeOption.id);
    this.scrollActiveOptionIntoView(activeOption);

    dispatchComboboxEvent(this.root, 'mg:combobox:highlight', {
      value: activeOption.dataset.value || '',
      label: activeOption.dataset.label || activeOption.textContent?.trim() || '',
    });
  }

  scrollActiveOptionIntoView(activeOption) {
    if (!activeOption || !this.listbox) {
      return;
    }

    const optionTop = activeOption.offsetTop;
    const optionBottom = optionTop + activeOption.offsetHeight;
    const visibleTop = this.listbox.scrollTop;
    const visibleBottom = visibleTop + this.listbox.clientHeight;

    if (optionTop < visibleTop) {
      this.listbox.scrollTop = optionTop;
      return;
    }

    if (optionBottom > visibleBottom) {
      this.listbox.scrollTop = optionBottom - this.listbox.clientHeight;
    }
  }

  filterOptions(query) {
    const normalizedQuery = query.trim().toLowerCase();
    const visible = [];

    this.optionNodes.forEach((option) => {
      const label = (option.dataset.label || option.textContent || '').trim();
      const shouldShow = normalizedQuery === '' || label.toLowerCase().includes(normalizedQuery);

      option.classList.toggle(HIDDEN_CLASS, !shouldShow);
      if (shouldShow) {
        visible.push(option);
      }
    });

    this.state.visibleOptions = visible.slice(0, this.config.maxItems);

    visible.forEach((option, index) => {
      const inRange = index < this.config.maxItems;
      option.classList.toggle(HIDDEN_CLASS, !inRange);
    });

    this.setActiveIndex(-1);
  }

  renderStatusOption(text) {
    this.listbox.innerHTML = '';
    const item = document.createElement('li');
    item.className = 'mg-combobox-empty';
    item.textContent = text;
    this.listbox.appendChild(item);
    this.optionNodes = [];
    this.state.visibleOptions = [];
    this.setActiveIndex(-1);
  }

  renderOptions(items, extraMetaKeys = []) {
    this.listbox.innerHTML = '';

    const optionElements = [];
    items.forEach((item) => {
      if (!item || typeof item !== 'object') {
        return;
      }

      const value = item[this.config.valueKey];
      const label = item[this.config.labelKey];
      if (value === undefined || value === null || !label) {
        return;
      }

      const option = document.createElement('li');
      option.setAttribute('data-mg-part', 'option');
      option.className = 'mg-combobox-option';
      option.dataset.value = String(value);
      option.dataset.label = String(label);
      option.setAttribute('role', 'option');

      const titleNode = document.createElement('span');
      titleNode.className = 'mg-combobox-option-title';
      titleNode.textContent = String(label);
      option.appendChild(titleNode);

      const meta = extraMetaKeys
        .map((key) => item[key])
        .filter(Boolean)
        .map((part) => String(part));
      if (meta.length > 0) {
        option.classList.add('has-meta');
        const metaNode = document.createElement('span');
        metaNode.className = 'mg-combobox-option-meta';
        metaNode.textContent = meta.join(', ');
        option.appendChild(metaNode);
      }

      this.listbox.appendChild(option);
      optionElements.push(option);
    });

    this.setOptionNodes(optionElements);
  }

  setOptionNodes(nodes) {
    this.optionNodes = nodes;
    this.optionNodes.forEach((option, index) => {
      if (!option.id) {
        option.id = `${this.listbox.id}-option-${index}`;
      }
      option.setAttribute('aria-selected', 'false');
    });
  }

  selectOption(option, source = 'api') {
    if (!option) {
      return;
    }

    const value = option.dataset.value || '';
    const label = option.dataset.label || option.textContent?.trim() || '';

    this.input.value = label;
    this.state.query = label;

    if (this.hiddenInput) {
      this.hiddenInput.value = value;
      this.hiddenInput.dispatchEvent(new Event('change', { bubbles: true }));
    }

    dispatchComboboxEvent(this.root, 'mg:combobox:select', { value, label, source });
    this.close();
  }

  open() {
    if (this.state.isOpen) {
      return;
    }

    this.state.isOpen = true;
    this.listbox.classList.remove(HIDDEN_CLASS);
    this.input.setAttribute('aria-expanded', 'true');
    if (
      this.config.autoSelectFirst &&
      this.state.activeIndex < 0 &&
      this.state.visibleOptions.length > 0
    ) {
      this.setActiveIndex(0);
    }
    dispatchComboboxEvent(this.root, 'mg:combobox:open');
  }

  close() {
    if (!this.state.isOpen && this.listbox.classList.contains(HIDDEN_CLASS)) {
      return;
    }

    this.state.isOpen = false;
    this.listbox.classList.add(HIDDEN_CLASS);
    this.input.setAttribute('aria-expanded', 'false');
    this.setActiveIndex(-1);
    dispatchComboboxEvent(this.root, 'mg:combobox:close');
  }
}

export class StaticComboboxController extends ComboboxBaseController {}

export class RemoteComboboxController extends ComboboxBaseController {
  constructor(root) {
    super(root);
    this.config = {
      ...this.config,
      remoteUrl: root.dataset.mgComboboxSourceUrl || '',
      queryParam: root.dataset.mgComboboxQueryParam || 'query',
      countryParamFromUrl: root.dataset.mgComboboxCountryUrlParam || '',
      valueKey: root.dataset.mgComboboxValueKey || 'value',
      labelKey: root.dataset.mgComboboxLabelKey || 'label',
      metaKeys: (root.dataset.mgComboboxMetaKeys || '')
        .split(',')
        .map((key) => key.trim())
        .filter(Boolean),
      loadingText: root.dataset.mgComboboxLoadingText || 'Загрузка...',
      emptyText: root.dataset.mgComboboxEmptyText || 'Ничего не найдено',
      debounceMs: Math.max(0, parseNumberAttr(root.dataset.mgComboboxDebounce, 250)),
    };
    this.fetchDebounceTimer = null;
    this.currentAbortController = null;
    this.lastRequestToken = 0;
  }

  onInit() {
    this.close();
  }

  onDestroy() {
    this.cancelPendingRequests();
  }

  onBelowMinChars() {
    this.cancelPendingRequests();
    this.close();
  }

  onQueryChange(query) {
    if (!this.config.remoteUrl) {
      return;
    }
    this.scheduleRemoteSearch(query);
  }

  onFocusOpen() {
    const query = this.input.value.trim();
    if (query.length < this.config.minChars) {
      return;
    }

    if (this.state.visibleOptions.length > 0) {
      this.open();
      if (this.config.autoSelectFirst) {
        this.setActiveIndex(0);
      }
    }
  }

  scheduleRemoteSearch(query) {
    if (this.fetchDebounceTimer) {
      window.clearTimeout(this.fetchDebounceTimer);
    }

    this.fetchDebounceTimer = window.setTimeout(() => {
      this.loadRemoteOptions(query);
    }, this.config.debounceMs);
  }

  async loadRemoteOptions(query) {
    if (query.trim().length < this.config.minChars) {
      return;
    }

    if (this.currentAbortController) {
      this.currentAbortController.abort();
    }

    const requestToken = ++this.lastRequestToken;
    const controller = new AbortController();
    this.currentAbortController = controller;

    this.renderStatusOption(this.config.loadingText);
    this.open();

    const requestUrl = new URL(this.config.remoteUrl, window.location.origin);
    requestUrl.searchParams.set(this.config.queryParam, query);

    if (this.config.countryParamFromUrl) {
      const currentUrlParams = new URLSearchParams(window.location.search);
      const countryValue = currentUrlParams.get(this.config.countryParamFromUrl);
      if (countryValue) {
        requestUrl.searchParams.set(this.config.countryParamFromUrl, countryValue);
      }
    }

    try {
      const response = await fetch(requestUrl.toString(), { signal: controller.signal });
      if (!response.ok) {
        throw new Error(`Combobox remote search failed: ${response.status}`);
      }

      const payload = await response.json();
      if (requestToken !== this.lastRequestToken) {
        return;
      }

      const items = Array.isArray(payload) ? payload : [];
      this.renderOptions(items, this.config.metaKeys);
      this.filterOptions('');

      if (this.state.visibleOptions.length > 0) {
        this.open();
        if (this.config.autoSelectFirst) {
          this.setActiveIndex(0);
        }
      } else {
        this.renderStatusOption(this.config.emptyText);
        this.open();
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        return;
      }
      console.error('Combobox remote search error:', error);
      this.renderStatusOption(this.config.emptyText);
      this.open();
    }
  }

  cancelPendingRequests() {
    if (this.fetchDebounceTimer) {
      window.clearTimeout(this.fetchDebounceTimer);
      this.fetchDebounceTimer = null;
    }
    if (this.currentAbortController) {
      this.currentAbortController.abort();
      this.currentAbortController = null;
    }
  }
}

export class ComboboxController extends StaticComboboxController {}
