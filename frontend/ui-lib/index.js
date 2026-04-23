import { registerComponent } from './core/registry';
import { initAll, destroyAll } from './core/init';
import { ComboboxController, StaticComboboxController, RemoteComboboxController } from './components/combobox';

export function registerDefaultComponents() {
  registerComponent('combobox', ComboboxController);
  registerComponent('combobox-static', StaticComboboxController);
  registerComponent('combobox-remote', RemoteComboboxController);
}

export {
  registerComponent,
  initAll,
  destroyAll,
  ComboboxController,
  StaticComboboxController,
  RemoteComboboxController,
};
