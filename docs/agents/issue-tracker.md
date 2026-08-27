<!--
---------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
-->

# Issue tracker: GitHub

Задачи и спецификации репозитория ведутся в GitHub Issues. Для всех операций используется `gh` CLI.

## Conventions

- Создание: `gh issue create --title "..." --body "..."`. Для многострочного body использовать heredoc.
- Чтение: `gh issue view <number> --comments`, при необходимости фильтруя комментарии через `jq` и получая labels.
- Список: `gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'` с нужными фильтрами `--label` и `--state`.
- Комментарий: `gh issue comment <number> --body "..."`.
- Метки: `gh issue edit <number> --add-label "..."` или `--remove-label "..."`.
- Закрытие: `gh issue close <number> --comment "..."`.

Репозиторий определяется по `git remote -v`; команды `gh`, запущенные из клона, используют его автоматически.

## Pull requests as a triage surface

**PRs as a request surface: no.** _(Изменить на `yes`, если внешние PR считаются feature requests; skill `triage` читает этот флаг.)_

При значении `yes` PR проходят через те же labels и states, что и issues:

- Чтение PR: `gh pr view <number> --comments`; diff: `gh pr diff <number>`.
- Список внешних PR: `gh pr list --state open --json number,title,body,labels,author,authorAssociation,comments`; оставить только `CONTRIBUTOR`, `FIRST_TIME_CONTRIBUTOR` и `NONE`.
- Комментарии, labels и закрытие: `gh pr comment`, `gh pr edit --add-label` / `--remove-label`, `gh pr close`.

GitHub использует общее пространство номеров для issues и PR. Для `#42` сначала выполнить `gh pr view 42`, затем при необходимости `gh issue view 42`.

## When a skill says "publish to the issue tracker"

Создать GitHub Issue.

## When a skill says "fetch the relevant ticket"

Выполнить `gh issue view <number> --comments`.

## Wayfinding operations

Skill `wayfinder` использует одну issue-карту и связанные с ней дочерние issues.

- Карта: issue с label `wayfinder:map`, содержащая Notes, Decisions-so-far и Fog. Создание: `gh issue create --label wayfinder:map`.
- Дочерняя задача: GitHub sub-issue карты. Если sub-issues недоступны, добавить задачу в task list карты и строку `Part of #<map>` в начало body. Labels: `wayfinder:<type>` (`research`, `prototype`, `grilling`, `task`).
- Блокировки: native issue dependencies через `gh api --method POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>`, где `<blocker-db-id>` — числовой database ID из `gh api repos/<owner>/<repo>/issues/<n> --jq .id`. Если dependencies недоступны, использовать строку `Blocked by: #<n>, #<n>` в начале body.
- Frontier query: получить открытые дочерние issues карты, исключить назначенные задачи и задачи с открытыми blockers; первая задача в порядке карты считается следующей.
- Claim: `gh issue edit <n> --add-assignee @me` — первая запись сессии.
- Resolve: добавить комментарий с ответом, закрыть issue и добавить в Decisions-so-far карты ссылку на сохранённый контекст.
