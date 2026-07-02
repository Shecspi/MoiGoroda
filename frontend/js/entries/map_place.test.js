// ---------------------------------------------
//
// Copyright © Egor Vavilov (Shecspi)
// Licensed under the Apache License, Version 2.0
//
// ----------------------------------------------

import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const currentDir = dirname(fileURLToPath(import.meta.url));
const source = readFileSync(join(currentDir, 'map_place.js'), 'utf8');

describe('map place popup action buttons', () => {
  it('uses hidden-safe inline-flex on all actions toggled by switch_popup_elements', () => {
    expect(source).not.toContain('hidden py-2 px-4 inline-flex');
    expect(source).not.toContain('hidden shrink-0 inline-flex');
    expect(source).toContain('id="btn-edit-place"');
    expect(source).toContain('id="btn-cancel-place"');
    expect(source).toContain('id="btn-update-place"');
    expect(source).toContain('id="btn-delete-place"');

    [
      ['edit', false],
      ['cancel', true],
      ['update', true],
      ['delete', false],
    ].forEach(([action, initiallyHidden]) => {
      expect(source).toMatch(
        new RegExp(
          `class="${initiallyHidden ? 'hidden ' : ''}\\[&:not\\(\\.hidden\\)\\]:inline-flex py-2 px-4[^\`]+id="btn-${action}-place"`,
        ),
      );
    });
  });
});
