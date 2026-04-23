import { registerComponent } from './core/registry';
import { initAll, destroyAll } from './core/init';
import { ComboboxController, StaticComboboxController, RemoteComboboxController } from './components/combobox';
import { SelectSearchController } from './components/select-search';

export function registerDefaultComponents() {
  registerComponent('combobox', ComboboxController);
  registerComponent('combobox-static', StaticComboboxController);
  registerComponent('combobox-remote', RemoteComboboxController);
  registerComponent('select-search', SelectSearchController);
}

export {
  registerComponent,
  initAll,
  destroyAll,
  ComboboxController,
  StaticComboboxController,
  RemoteComboboxController,
  SelectSearchController,
};
