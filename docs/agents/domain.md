<!--
---------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
-->

# Domain Docs

Правила чтения доменной документации engineering skills перед исследованием кодовой базы.

## Before exploring, read these

- `CONTEXT.md` в корне репозитория.
- `CONTEXT-MAP.md` в корне, если он существует: он указывает на отдельные `CONTEXT.md`; читать контексты, релевантные задаче.
- Релевантные ADR из `docs/adr/`. В multi-context репозиториях также проверять `src/<context>/docs/adr/`.

Если этих файлов нет, продолжать работу без предупреждения и не предлагать создать их заранее. Skill `domain-modeling` создаёт их по мере определения доменных терминов и архитектурных решений.

## File structure

Репозиторий использует single-context layout:

```text
/
├── CONTEXT.md
├── docs/
│   └── adr/
└── src/
```

Multi-context layout определяется наличием `CONTEXT-MAP.md` в корне:

```text
/
├── CONTEXT-MAP.md
├── docs/
│   └── adr/
└── src/
    ├── ordering/
    │   ├── CONTEXT.md
    │   └── docs/adr/
    └── billing/
        ├── CONTEXT.md
        └── docs/adr/
```

## Use the glossary's vocabulary

В issues, предложениях по refactoring, гипотезах и названиях тестов использовать термины из `CONTEXT.md`, не заменяя их синонимами, которые glossary явно исключает.

Если нужного понятия нет в glossary, проверить, не вводится ли неиспользуемый проектом термин. Реальный пробел отметить для skill `domain-modeling`.

## Flag ADR conflicts

Если результат противоречит существующему ADR, указать конфликт явно, а не молча переопределять решение:

> _Противоречит ADR-0007 (event-sourced orders), но решение стоит пересмотреть, потому что..._
