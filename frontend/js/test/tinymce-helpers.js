import { vi } from 'vitest';

/**
 * Минимальный mock TinyMCE editor для тестов плагинов в static/tinymce/js.
 * @returns {{
 *   getBody: () => HTMLElement,
 *   dom: object,
 *   selection: object,
 *   windowManager: object,
 *   undoManager: object,
 *   ui: object,
 *   onHandlers: Map<string, Function[]>,
 *   insertContent: ReturnType<typeof vi.fn>,
 *   options: object,
 *   settings: object,
 *   trigger: (event: string, payload?: object) => void,
 * }}
 */
export function createMockTinyMCEEditor(initialBodyHtml = '') {
  const body = document.createElement('div');
  body.innerHTML = initialBodyHtml;

  const onHandlers = new Map();

  function on(event, handler) {
    const list = onHandlers.get(event) || [];
    list.push(handler);
    onHandlers.set(event, list);
  }

  function trigger(event, payload = {}) {
    const list = onHandlers.get(event) || [];
    list.forEach((handler) => handler(payload));
  }

  const insertContent = vi.fn();

  const dom = {
    hasClass(node, className) {
      return Boolean(node?.classList?.contains(className));
    },
    getParent(node, selector) {
      if (!node) return null;
      if (selector.startsWith('.')) {
        const cls = selector.slice(1);
        let cur = node;
        while (cur) {
          if (cur.nodeType === 1 && cur.classList?.contains(cls)) return cur;
          cur = cur.parentNode;
        }
        return null;
      }
      return node.closest?.(selector) ?? null;
    },
    setAttrib(node, name, value) {
      if (!node) return;
      if (value === null || value === undefined) {
        node.removeAttribute(name);
      } else {
        node.setAttribute(name, value);
      }
    },
    setStyle(node, prop, value) {
      if (!node?.style) return;
      if (value === null || value === undefined) {
        node.style.removeProperty(prop);
      } else {
        node.style[prop] = value;
      }
    },
    setOuterHTML: vi.fn((node, html) => {
      if (!node?.parentNode) return;
      const tpl = document.createElement('template');
      tpl.innerHTML = html;
      const replacement = tpl.content.firstChild;
      if (replacement) {
        node.parentNode.replaceChild(replacement, node);
      }
    }),
    create(tag) {
      return document.createElement(tag);
    },
    insertBefore(newNode, ref) {
      ref.parentNode?.insertBefore(newNode, ref);
    },
    insertAfter(newNode, ref) {
      ref.parentNode?.insertBefore(newNode, ref.nextSibling);
    },
    remove(node) {
      node?.parentNode?.removeChild(node);
    },
  };

  let lastDialogConfig = null;
  const windowManager = {
    open(config) {
      lastDialogConfig = config;
      config.onOpen?.();
      return { close: vi.fn() };
    },
    alert: vi.fn(),
    getLastDialogConfig() {
      return lastDialogConfig;
    },
  };

  const editor = {
    getBody: () => body,
    dom,
    selection: {
      getNode: () => body.querySelector('img, .mg-blog-carousel') || body.firstChild,
    },
    windowManager,
    undoManager: {
      transact(fn) {
        fn();
      },
    },
    ui: {
      registry: {
        addButton: vi.fn(),
        addContextToolbar: vi.fn(),
      },
    },
    on,
    insertContent,
    nodeChanged: vi.fn(),
    options: {
      set: vi.fn(),
    },
    settings: {},
    translate(key) {
      return key;
    },
    trigger,
    _test: { body, onHandlers, getLastDialogConfig: () => lastDialogConfig },
  };

  return editor;
}

/**
 * @param {File[]} files
 */
export function createFileList(files) {
  const list = {
    length: files.length,
    item(i) {
      return files[i] ?? null;
    },
  };
  files.forEach((file, i) => {
    list[i] = file;
  });
  return list;
}

/**
 * @param {string} name
 * @param {number} [size]
 * @param {number} [lastModified]
 */
export function createMockFile(name, size = 100, lastModified = 1) {
  return new File(['x'.repeat(size)], name, {
    type: 'image/jpeg',
    lastModified,
  });
}
