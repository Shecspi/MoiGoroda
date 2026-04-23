import { isEventOutside } from '../utils/dom';

const HIDDEN_CLASS = 'hidden';

function dispatchSelectSearchEvent(root, name, detail = {}) {
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

export class SelectSearchController {
  constructor(root) {
    this.root = root;
    this.nativeSelect = root.querySelector('[data-mg-part="native-select"]');
    this.toggle = root.querySelector('[data-mg-part="toggle"]');
    this.toggleLabel = root.querySelector('[data-mg-part="toggle-label"]');
    this.dropdown = root.querySelector('[data-mg-part="dropdown"]');
    this.searchInput = root.querySelector('[data-mg-part="search-input"]');
    this.optionsList = root.querySelector('[data-mg-part="options-list"]');

    this.config = {
      placeholder: root.dataset.mgSelectSearchPlaceholder || 'Выберите значение',
      searchPlaceholder: root.dataset.mgSelectSearchFilterPlaceholder || 'Поиск...',
      emptyText: root.dataset.mgSelectSearchEmptyText || 'Ничего не найдено',
    };

    this.state = {
      isOpen: false,
      query: '',
      options: [],
      filteredOptions: [],
    };

    this.observer = null;

    this.handleToggleClick = this.handleToggleClick.bind(this);
    this.handleSearchInput = this.handleSearchInput.bind(this);
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
      !this.searchInput ||
      !this.optionsList
    ) {
      return;
    }

    this.searchInput.placeholder = this.config.searchPlaceholder;

    this.toggle.addEventListener('click', this.handleToggleClick);
    this.searchInput.addEventListener('input', this.handleSearchInput);
    this.optionsList.addEventListener('click', this.handleOptionsClick);
    this.nativeSelect.addEventListener('change', this.handleNativeChange);
    this.toggle.addEventListener('keydown', this.handleKeydown);
    this.searchInput.addEventListener('keydown', this.handleKeydown);
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
  }

  destroy() {
    if (!this.nativeSelect) {
      return;
    }

    this.toggle?.removeEventListener('click', this.handleToggleClick);
    this.searchInput?.removeEventListener('input', this.handleSearchInput);
    this.optionsList?.removeEventListener('click', this.handleOptionsClick);
    this.nativeSelect.removeEventListener('change', this.handleNativeChange);
    this.toggle?.removeEventListener('keydown', this.handleKeydown);
    this.searchInput?.removeEventListener('keydown', this.handleKeydown);
    document.removeEventListener('pointerdown', this.handleDocumentPointerDown);

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
    this.applyFilter(this.state.query);
    this.syncDisabledState();
    this.updateToggleLabel();
  }

  syncDisabledState() {
    const isDisabled = this.nativeSelect.disabled;
    this.toggle.disabled = isDisabled;
    this.searchInput.disabled = isDisabled;

    if (isDisabled) {
      this.close();
    }
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

  renderOptions() {
    this.optionsList.innerHTML = '';

    if (this.state.filteredOptions.length === 0) {
      const emptyNode = document.createElement('li');
      emptyNode.className = 'mg-combobox-empty';
      emptyNode.textContent = this.config.emptyText;
      this.optionsList.appendChild(emptyNode);
      return;
    }

    this.state.filteredOptions.forEach((option) => {
      const optionNode = document.createElement('li');
      optionNode.setAttribute('data-mg-part', 'option');
      optionNode.dataset.index = String(option.index);
      optionNode.setAttribute('role', 'option');
      optionNode.className = 'mg-combobox-option';
      if (option.selected) {
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

  open() {
    if (this.state.isOpen || this.nativeSelect.disabled) {
      return;
    }
    this.state.isOpen = true;
    this.dropdown.classList.remove(HIDDEN_CLASS);
    this.toggle.setAttribute('aria-expanded', 'true');
    this.searchInput.focus();
    dispatchSelectSearchEvent(this.root, 'mg:select-search:open');
  }

  close() {
    if (!this.state.isOpen && this.dropdown.classList.contains(HIDDEN_CLASS)) {
      return;
    }
    this.state.isOpen = false;
    this.dropdown.classList.add(HIDDEN_CLASS);
    this.toggle.setAttribute('aria-expanded', 'false');
    this.searchInput.value = '';
    this.applyFilter('');
    dispatchSelectSearchEvent(this.root, 'mg:select-search:close');
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

    dispatchSelectSearchEvent(this.root, 'mg:select-search:select', {
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

  handleSearchInput(event) {
    this.applyFilter(event.target.value || '');
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
    if (event.key === 'Escape') {
      this.close();
      this.toggle.focus();
    }
  }
}
