const registry = new Map();

export function registerComponent(name, ControllerClass) {
  if (!name || typeof name !== 'string') {
    throw new Error('UI registry: component name must be a non-empty string');
  }

  if (typeof ControllerClass !== 'function') {
    throw new Error(`UI registry: "${name}" controller must be a class/function`);
  }

  registry.set(name, ControllerClass);
}

export function getComponent(name) {
  return registry.get(name) || null;
}
