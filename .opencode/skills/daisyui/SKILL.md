---
name: daisyui
description: Use when generating or reviewing Tailwind HTML, Django templates, daisyUI components, UI layouts, visual design, component classes, themes, colors, badges, cards, tables, forms, alerts, collapse, modal, or navbar in this project.
---

<!--
---------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
-->

# daisyUI

## Overview

Use daisyUI as the preferred compact component layer for Tailwind UI work in this project, while preserving the current Django templates + Vite architecture.

The authoritative reference is `https://daisyui.com/llms.txt`. Fetch it before non-trivial daisyUI work, especially when choosing components or class names.

## Project Rules

- On stable Tailwind 3 branches, use `daisyui@4.12.x`; daisyUI 5 requires Tailwind CSS 4 and does not generate `dui-*` CSS in the Tailwind 3 build pipeline.
- On Tailwind 4 migration branches, use `daisyui@5.x` and configure it from `frontend/css/tailwind.css` with `@plugin "daisyui"`.
- `https://daisyui.com/llms.txt` is daisyUI 5 documentation. Use it directly on Tailwind 4 branches; on Tailwind 3 branches use it for component discovery only.
- All daisyUI classes must use the configured prefix: `dui-`.
- Use `dui-card`, not `card`; `dui-btn`, not `btn`; `dui-badge`, not `badge`.
- Keep the prefix because the project already has custom `.btn`, `.badge`, and `.progress` classes.
- Prefer daisyUI components plus Tailwind layout utilities over custom CSS.
- Use custom CSS only when component classes and utilities are insufficient.

## Install Shapes

Tailwind 3 stable branches:

```js
plugins: [require('daisyui')],
daisyui: {
  prefix: 'dui-',
},
```

Tailwind 4 migration branches:

```css
@import "tailwindcss";
@plugin "daisyui" {
    prefix: dui-;
}
```

## Component Selection

Before writing daisyUI markup:

1. Identify the UI intent: navigation, data display, action, feedback, disclosure, form, layout.
2. Fetch `https://daisyui.com/llms.txt` and check it for matching components and rules.
3. Prefer the simplest daisyUI component that matches the behavior.
4. Add Tailwind utilities only for spacing, responsive layout, and small project-specific adjustments.
5. Avoid stacking many nested decorative cards unless the information hierarchy requires it.

## Common Mappings

| Intent | Use |
| --- | --- |
| Panel or grouped content | `dui-card`, `dui-card-body` |
| Actions | `dui-btn`, `dui-btn-primary`, `dui-btn-outline`, `dui-btn-sm` |
| Status | `dui-badge`, `dui-badge-success`, `dui-badge-warning`, `dui-badge-error` |
| Empty/error/info state | `dui-alert` |
| Collapsible details | `dui-collapse`, `dui-collapse-arrow`, `dui-collapse-title`, `dui-collapse-content` |
| Data table | `dui-table` |
| Metrics | `dui-stats`, `dui-stat` |
| Form controls | `dui-input`, `dui-select`, `dui-textarea`, `dui-checkbox`, `dui-label` |

## Verification

After changing Tailwind/daisyUI templates or config, run from `frontend/`:

```bash
npm run build
```

If a Django template changed in `premium/`, run from the project root:

```bash
poetry run pytest premium/tests -q
```

## Common Mistakes

| Mistake | Fix |
| --- | --- |
| Using unprefixed `btn`, `badge`, `card` | Use `dui-btn`, `dui-badge`, `dui-card` |
| Following Tailwind 4 install docs in this Tailwind 3 project | Keep `tailwind.config.js` plugin config |
| Rebuilding Bootstrap-style layouts with excessive utility classes | Start from daisyUI components |
| Mixing many semantic colors in one screen | Use one primary action color and status colors only where meaningful |
| Adding custom CSS for ordinary component styling | Use daisyUI classes or Tailwind utilities first |
