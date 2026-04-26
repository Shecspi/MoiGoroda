import { describe, it, expect } from 'vitest';
import { parseBooleanAttr, parseNumberAttr, isEventOutside } from './dom.js';

describe('parseBooleanAttr', () => {
  it('возвращает fallback для пустого значения', () => {
    expect(parseBooleanAttr(undefined, true)).toBe(true);
    expect(parseBooleanAttr('', false)).toBe(false);
  });

  it('распознаёт явные true-значения, остальные строки — false (fallback не применяется к непустой строке)', () => {
    expect(parseBooleanAttr('1', false)).toBe(true);
    expect(parseBooleanAttr('true', false)).toBe(true);
    expect(parseBooleanAttr('on', false)).toBe(true);
    expect(parseBooleanAttr('off', true)).toBe(false);
  });
});

describe('parseNumberAttr', () => {
  it('возвращает fallback при NaN', () => {
    expect(parseNumberAttr('abc', 7)).toBe(7);
  });

  it('парсит целое число', () => {
    expect(parseNumberAttr('42', 0)).toBe(42);
  });
});

describe('isEventOutside', () => {
  it('считает вне, если target не внутри контейнера', () => {
    const a = document.createElement('div');
    const b = document.createElement('div');
    document.body.append(a, b);
    const event = { target: b };
    expect(isEventOutside(event, a)).toBe(true);
    a.remove();
    b.remove();
  });

  it('считает внутри, если target внутри контейнера', () => {
    const root = document.createElement('div');
    const child = document.createElement('span');
    root.appendChild(child);
    const event = { target: child };
    expect(isEventOutside(event, root)).toBe(false);
  });
});
