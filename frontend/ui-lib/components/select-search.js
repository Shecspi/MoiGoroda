import { isEventOutside } from '../utils/dom';

const HIDDEN_CLASS = 'hidden';

function dispatchSelectEvent(root, name, detail = {}) {
  root.dispatchEvent(
    new CustomEvent(name, {
      detail,
      bubbles: true,
    }),
  );
}

function normalizeText(value) {
  return String(value || '').trim().toLowerCase();
}

export class SelectController {
  constructor(root) {
    this.root = root;
    this.nativeSelect = root.querySelector('[data-mg-part="native-select"]');
    this.toggle = root.querySelector('[data-mg-part="toggle"]');
    this.toggleLabel = root.querySelector('[data-mg-part="toggle-label"]');
    this.dropdown = root.querySelector('[data-mg-part="dropdown"]');
    this.searchInput = root.querySelector('[data-mg-part="search-input"]');
    this.optionsList = root.querySelector('[data-mg-part="options-list"]');

    this.config = {
      placeholder: root.dataset.mgSelectPlaceholder || 'Выберите значение',
      emptyText: root.dataset.mgSelectEmptyText || 'Ничего не найдено',
    };

    this.state = {
      isOpen: false,
      options: [],
      /** Позиция в списке из getRenderableOptions() (подсветка клавиатуры), -1 когда список закрыт */
      keyboardListPos: -1,
    };

    this.observer = null;

    this.handleToggleClick = this.handleToggleClick.bind(this);
    this.handleOptionsClick = this.handleOptionsClick.bind(this);
    this.handleNativeChange = this.handleNativeChange.bind(this);
    this.handleDocumentPointerDown = this.handleDocumentPointerDown.bind(this);
    this.handleKeydown = this.handleKeydown.bind(this);
  }

  init() {
    if (
      !this.nativeSelect ||
      !this.toggle ||
      !this.toggleLabel ||
      !this.dropdown ||
      !this.optionsList
    ) {
      return;
    }

    this.toggle.addEventListener('click', this.handleToggleClick);
    this.optionsList.addEventListener('click', this.handleOptionsClick);
    this.nativeSelect.addEventListener('change', this.handleNativeChange);
    this.toggle.addEventListener('keydown', this.handleKeydown);
    document.addEventListener('pointerdown', this.handleDocumentPointerDown);

    this.observer = new MutationObserver(() => {
      this.syncFromNativeSelect();
    });
    this.observer.observe(this.nativeSelect, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['disabled', 'selected', 'label'],
    });

    this.syncFromNativeSelect();
    this.close();
    this.initSearch();
  }

  destroy() {
    if (!this.nativeSelect) {
      return;
    }

    this.toggle?.removeEventListener('click', this.handleToggleClick);
    this.optionsList?.removeEventListener('click', this.handleOptionsClick);
    this.nativeSelect.removeEventListener('change', this.handleNativeChange);
    this.toggle?.removeEventListener('keydown', this.handleKeydown);
    document.removeEventListener('pointerdown', this.handleDocumentPointerDown);
    this.destroySearch();

    if (this.observer) {
      this.observer.disconnect();
      this.observer = null;
    }
  }

  syncFromNativeSelect() {
    const options = Array.from(this.nativeSelect.options).map((option, index) => ({
      index,
      value: option.value,
      label: option.textContent || '',
      disabled: option.disabled,
      selected: option.selected,
    }));

    this.state.options = options;
    this.renderOptions();
    this.syncDisabledState();
    this.updateToggleLabel();
  }

  syncDisabledState() {
    const isDisabled = this.nativeSelect.disabled;
    this.toggle.disabled = isDisabled;
    this.syncSearchDisabledState(isDisabled);

    if (isDisabled) {
      this.close();
    }
  }

  renderOptions() {
    const options = this.getRenderableOptions();
    if (this.state.isOpen) {
      this.clampKeyboardIndex();
    }
    this.optionsList.innerHTML = '';

    if (options.length === 0) {
      const emptyNode = document.createElement('li');
      emptyNode.className = 'mg-combobox-empty';
      emptyNode.textContent = this.config.emptyText;
      this.optionsList.appendChild(emptyNode);
      return;
    }

    options.forEach((option, i) => {
      const optionNode = document.createElement('li');
      optionNode.setAttribute('data-mg-part', 'option');
      optionNode.dataset.index = String(option.index);
      optionNode.setAttribute('role', 'option');
      optionNode.className = 'mg-combobox-option';
      if (option.selected) {
        optionNode.classList.add('is-selected');
        optionNode.setAttribute('aria-selected', 'true');
      } else {
        optionNode.setAttribute('aria-selected', 'false');
      }
      if (this.state.isOpen && this.state.keyboardListPos === i) {
        optionNode.classList.add('is-active');
      }
      if (option.disabled) {
        optionNode.classList.add('is-disabled');
      }

      const labelNode = document.createElement('span');
      labelNode.className = 'mg-combobox-option-title';
      labelNode.textContent = option.label;
      optionNode.appendChild(labelNode);

      this.optionsList.appendChild(optionNode);
    });
  }

  updateToggleLabel() {
    const selectedOption = this.state.options.find((option) => option.selected && !option.disabled);
    if (selectedOption) {
      this.toggleLabel.textContent = selectedOption.label;
      this.toggleLabel.classList.remove('text-gray-500', 'dark:text-neutral-400');
      this.toggleLabel.classList.add('text-gray-900', 'dark:text-neutral-100');
      return;
    }

    this.toggleLabel.textContent = this.config.placeholder;
    this.toggleLabel.classList.add('text-gray-500', 'dark:text-neutral-400');
    this.toggleLabel.classList.remove('text-gray-900', 'dark:text-neutral-100');
  }

  open({ keyboardFromEnd = false } = {}) {
    if (this.state.isOpen || this.nativeSelect.disabled) {
      return;
    }
    this.state.isOpen = true;
    this.dropdown.classList.remove(HIDDEN_CLASS);
    this.toggle.setAttribute('aria-expanded', 'true');
    this.initKeyboardPosition({ fromEnd: keyboardFromEnd });
    this.renderOptions();
    this.focusOpenTarget();
    this.scrollKeyboardItemIntoView();
    dispatchSelectEvent(this.root, 'mg:select:open');
  }

  close() {
    if (!this.state.isOpen && this.dropdown.classList.contains(HIDDEN_CLASS)) {
      return;
    }
    this.state.isOpen = false;
    this.state.keyboardListPos = -1;
    this.dropdown.classList.add(HIDDEN_CLASS);
    this.toggle.setAttribute('aria-expanded', 'false');
    this.onClose();
    dispatchSelectEvent(this.root, 'mg:select:close');
  }

  selectOption(optionIndex) {
    const targetOption = this.nativeSelect.options[optionIndex];
    if (!targetOption || targetOption.disabled) {
      return;
    }

    this.nativeSelect.selectedIndex = optionIndex;
    this.nativeSelect.dispatchEvent(new Event('change', { bubbles: true }));
    this.syncFromNativeSelect();
    this.close();

    dispatchSelectEvent(this.root, 'mg:select:select', {
      value: targetOption.value,
      label: targetOption.textContent || '',
    });
  }

  handleToggleClick() {
    if (this.state.isOpen) {
      this.close();
      return;
    }
    this.open();
  }

  handleOptionsClick(event) {
    const optionNode = event.target.closest('[data-mg-part="option"]');
    if (!optionNode || !this.optionsList.contains(optionNode)) {
      return;
    }

    this.selectOption(Number.parseInt(optionNode.dataset.index || '', 10));
  }

  handleNativeChange() {
    this.syncFromNativeSelect();
  }

  handleDocumentPointerDown(event) {
    if (isEventOutside(event, this.root)) {
      this.close();
    }
  }

  handleKeydown(event) {
    const { key, code, target } = event;
    const isArrowDown = key === 'ArrowDown' || code === 'ArrowDown';
    const isArrowUp = key === 'ArrowUp' || code === 'ArrowUp';
    const fromSearch = this.searchInput && target === this.searchInput;

    if (key === 'Escape') {
      event.preventDefault();
      this.close();
      this.toggle?.focus();
      return;
    }

    if (key === 'Tab' && this.state.isOpen) {
      this.close();
      return;
    }

    if (!this.state.isOpen) {
      if (fromSearch) {
        return;
      }
      if (isArrowDown || isArrowUp || key === 'Enter' || key === ' ' || code === 'Space') {
        event.preventDefault();
        this.open({ keyboardFromEnd: isArrowUp });
      }
      return;
    }

    if (isArrowDown) {
      event.preventDefault();
      this.moveKeyboardActive(1);
      return;
    }
    if (isArrowUp) {
      event.preventDefault();
      this.moveKeyboardActive(-1);
      return;
    }
    if (key === 'Home' || code === 'Home') {
      event.preventDefault();
      this.moveKeyboardToEdge('start');
      return;
    }
    if (key === 'End' || code === 'End') {
      event.preventDefault();
      this.moveKeyboardToEdge('end');
      return;
    }
    if (key === 'Enter' || code === 'Enter' || code === 'NumpadEnter') {
      if (this.state.keyboardListPos < 0) {
        return;
      }
      event.preventDefault();
      this.selectKeyboardActive();
      return;
    }
  }

  initKeyboardPosition({ fromEnd = false } = {}) {
    if (fromEnd) {
      const all = this.getRenderableOptions();
      const enabledIdx = all.map((o, i) => (o.disabled ? -1 : i)).filter((j) => j >= 0);
      this.state.keyboardListPos = enabledIdx.length ? enabledIdx[enabledIdx.length - 1] : -1;
      return;
    }
    this.state.keyboardListPos = this.findInitialKeyboardIndex();
  }

  findInitialKeyboardIndex() {
    const all = this.getRenderableOptions();
    if (all.length === 0) {
      return -1;
    }
    const selectedIdx = all.findIndex((o) => o.selected && !o.disabled);
    if (selectedIdx >= 0) {
      return selectedIdx;
    }
    const firstEnabled = all.findIndex((o) => !o.disabled);
    return firstEnabled >= 0 ? firstEnabled : 0;
  }

  clampKeyboardIndex() {
    const options = this.getRenderableOptions();
    if (options.length === 0) {
      this.state.keyboardListPos = -1;
      return;
    }
    if (this.state.keyboardListPos < 0 || this.state.keyboardListPos >= options.length) {
      this.state.keyboardListPos = this.findInitialKeyboardIndex();
      return;
    }
    if (options[this.state.keyboardListPos].disabled) {
      this.state.keyboardListPos = this.findInitialKeyboardIndex();
    }
  }

  moveKeyboardActive(delta) {
    const all = this.getRenderableOptions();
    const enabledIdx = all.map((o, i) => (o.disabled ? -1 : i)).filter((i) => i >= 0);
    if (enabledIdx.length === 0) {
      return;
    }
    let pos = this.state.keyboardListPos;
    if (pos < 0 || all[pos].disabled) {
      pos = enabledIdx[0];
    } else {
      const inList = enabledIdx.indexOf(pos);
      if (inList < 0) {
        pos = enabledIdx[0];
      } else {
        const next = (inList + delta + enabledIdx.length) % enabledIdx.length;
        pos = enabledIdx[next];
      }
    }
    this.state.keyboardListPos = pos;
    this.renderOptions();
    this.scrollKeyboardItemIntoView();
  }

  moveKeyboardToEdge(edge) {
    const all = this.getRenderableOptions();
    const enabledIdx = all.map((o, i) => (o.disabled ? -1 : i)).filter((i) => i >= 0);
    if (enabledIdx.length === 0) {
      return;
    }
    this.state.keyboardListPos = edge === 'start' ? enabledIdx[0] : enabledIdx[enabledIdx.length - 1];
    this.renderOptions();
    this.scrollKeyboardItemIntoView();
  }

  selectKeyboardActive() {
    const options = this.getRenderableOptions();
    if (this.state.keyboardListPos < 0) {
      return;
    }
    const opt = options[this.state.keyboardListPos];
    if (!opt || opt.disabled) {
      return;
    }
    this.selectOption(opt.index);
  }

  scrollKeyboardItemIntoView() {
    if (this.state.keyboardListPos < 0 || !this.optionsList) {
      return;
    }
    const optionElements = this.optionsList.querySelectorAll('[data-mg-part="option"]');
    const li = optionElements[this.state.keyboardListPos];
    if (li) {
      li.scrollIntoView({ block: 'nearest' });
    }
  }

  getRenderableOptions() {
    return this.state.options;
  }

  initSearch() {}

  destroySearch() {}

  syncSearchDisabledState() {}

  focusOpenTarget() {}

  onClose() {}
}

export class SelectSearchableController extends SelectController {
  constructor(root) {
    super(root);
    this.config.searchPlaceholder = root.dataset.mgSelectSearchableFilterPlaceholder || 'Поиск...';
    this.state.query = '';
    this.state.filteredOptions = [];
    this.handleSearchInput = this.handleSearchInput.bind(this);
  }

  initSearch() {
    if (!this.searchInput) {
      return;
    }

    this.searchInput.placeholder = this.config.searchPlaceholder;
    this.searchInput.addEventListener('input', this.handleSearchInput);
    this.searchInput.addEventListener('keydown', this.handleKeydown);
    this.applyFilter('');
  }

  destroySearch() {
    this.searchInput?.removeEventListener('input', this.handleSearchInput);
    this.searchInput?.removeEventListener('keydown', this.handleKeydown);
  }

  syncSearchDisabledState(isDisabled) {
    if (this.searchInput) {
      this.searchInput.disabled = isDisabled;
    }
  }

  focusOpenTarget() {
    if (this.searchInput) {
      this.searchInput.focus();
    }
  }

  onClose() {
    if (this.searchInput) {
      this.searchInput.value = '';
    }
    this.applyFilter('');
  }

  handleSearchInput(event) {
    this.applyFilter(event.target.value || '');
  }

  applyFilter(query) {
    this.state.query = query;
    const normalizedQuery = normalizeText(query);
    this.state.filteredOptions = this.state.options.filter((option) => {
      if (!normalizedQuery) {
        return true;
      }
      return normalizeText(option.label).includes(normalizedQuery);
    });
    this.renderOptions();
  }

  getRenderableOptions() {
    return this.state.filteredOptions;
  }

  syncFromNativeSelect() {
    super.syncFromNativeSelect();
    this.applyFilter(this.state.query);
  }
}
