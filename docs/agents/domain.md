<!--
---------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
-->

# Domain Docs

Engineering skills перед исследованием читают root `CONTEXT.md` и релевантные ADR из `docs/adr/`.

Если этих файлов нет, нужно продолжать работу без предупреждения. Skill `domain-modeling` создаёт глоссарий и ADR только когда устойчиво определены доменные термины или архитектурные решения.

## File structure

Репозиторий использует single-context layout:

```text
/
├── CONTEXT.md
└── docs/
    └── adr/
```

При подготовке issues, спецификаций, тестов и предложений использовать термины из `CONTEXT.md`. Конфликт с существующим ADR необходимо явно указать, а не молча обходить.
