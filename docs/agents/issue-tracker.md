<!--
---------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
-->

# Issue tracker: GitHub

Задачи и спецификации репозитория ведутся в GitHub Issues. Для всех операций используется `gh` CLI.

## Conventions

- Создание: `gh issue create --title "..." --body "..."`.
- Чтение: `gh issue view <number> --comments`.
- Список: `gh issue list --state open` с необходимыми фильтрами.
- Комментарий: `gh issue comment <number> --body "..."`.
- Метки: `gh issue edit <number> --add-label "..."` или `--remove-label "..."`.
- Закрытие: `gh issue close <number> --comment "..."`.

Репозиторий определяется по `git remote -v`; команды `gh`, запущенные из клона, используют его автоматически.

## Pull requests as a triage surface

**PRs as a request surface: no.**

## When a skill says "publish to the issue tracker"

Создать GitHub Issue.

## When a skill says "fetch the relevant ticket"

Выполнить `gh issue view <number> --comments`.
