import { getComponent } from './registry';

const COMPONENT_SELECTOR = '[data-component]';
const BOUND_ATTR = 'uiBound';
const instances = new WeakMap();

function initNode(node) {
  if (!node || node.dataset[BOUND_ATTR] === '1') {
    return null;
  }

  const componentName = node.dataset.component;
  const ControllerClass = getComponent(componentName);
  if (!ControllerClass) {
    return null;
  }

  const instance = new ControllerClass(node);
  if (typeof instance.init === 'function') {
    instance.init();
  }

  node.dataset[BOUND_ATTR] = '1';
  instances.set(node, instance);
  return instance;
}

function destroyNode(node) {
  const instance = instances.get(node);
  if (!instance) {
    delete node.dataset[BOUND_ATTR];
    return;
  }

  if (typeof instance.destroy === 'function') {
    instance.destroy();
  }

  instances.delete(node);
  delete node.dataset[BOUND_ATTR];
}

function getScopeNodes(root = document) {
  if (!root) {
    return [];
  }

  const nodes = Array.from(root.querySelectorAll(COMPONENT_SELECTOR));
  if (root.matches && root.matches(COMPONENT_SELECTOR)) {
    nodes.unshift(root);
  }
  return nodes;
}

export function initAll(root = document) {
  const nodes = getScopeNodes(root);
  nodes.forEach((node) => initNode(node));
}

export function destroyAll(root = document) {
  const nodes = getScopeNodes(root);
  nodes.forEach((node) => destroyNode(node));
}
