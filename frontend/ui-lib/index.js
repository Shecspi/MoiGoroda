import { registerComponent } from './core/registry';
import { initAll, destroyAll } from './core/init';
import { ComboboxController, StaticComboboxController, RemoteComboboxController } from './components/combobox';
import { SelectController, SelectSearchableController } from './components/select-search';

export function registerDefaultComponents() {
  registerComponent('mg-combobox-static', StaticComboboxController);
  registerComponent('mg-combobox-remote', RemoteComboboxController);
  registerComponent('mg-select', SelectController);
  registerComponent('mg-select-searchable', SelectSearchableController);
}

export {
  registerComponent,
  initAll,
  destroyAll,
  ComboboxController,
  StaticComboboxController,
  RemoteComboboxController,
  SelectController,
  SelectSearchableController,
};
