# Weekly Feedback & Retro Tool

A tool for teams to submit weekly feedback on a project and run a structured retrospective from
that feedback. See [`_docs/plan.md`](./_docs/plan.md) for full project scope.

## Documentation

- [`_docs/plan.md`](./_docs/plan.md) — project scope, requirements, and the chosen tech stack.
- [`_docs/architecture.md`](./_docs/architecture.md) — how the Django + HTMX + Alpine stack is
  structured (apps, data model, phase flow, polling instead of websockets).
- [`_docs/api.md`](./_docs/api.md) — the app's HTTP routes (HTML/HTMX responses, not a JSON API).
- [`_docs/design-system.md`](./_docs/design-system.md) — shared UI tokens, components, and HTMX/
  Alpine conventions, so the UI stays consistent across tasks/sessions.
- [`_docs/testing-guidelines.md`](./_docs/testing-guidelines.md) — what and how to test for each
  task, and each task's definition of done.
- [`_docs/tasks.md`](./_docs/tasks.md) — the backlog; each task is also tracked as a GitHub issue.
- [`_docs/process.md`](./_docs/process.md) — how work moves through the backlog day to day.

## Development

See [`AGENTS.md`](./AGENTS.md) for setup commands and repo rules.
