# Testing Guidelines

Applies to all tasks in [tasks.md](./tasks.md). Read alongside [architecture.md](./architecture.md)
(Django, server-rendered, no websockets, no JSON API) — tests target Django views and templates,
not a separate API layer.

## 1. Test runner

Use `pytest` + `pytest-django` (preferred) or plain `manage.py test` — either is fine, but be
consistent within a single task's PR. Don't introduce a second test runner mid-project.

## 2. Where tests live

One `tests.py` (or a `tests/` package once a single file gets unwieldy) per Django app, next to the
code it covers — e.g. `cards/tests.py` covers the `cards` app's models and views. A task that adds
a model or view must ship its own tests in the same PR; don't defer tests to a later task.

## 3. What to test, by layer

- **Models** — defaults (e.g. a new Board defaults to the Submission phase), field constraints,
  and any custom methods/properties. Don't test Django's ORM itself (e.g. don't test that
  `save()` persists a row — that's framework behavior).
- **Views** — status codes for the happy path, and explicitly for each permission/state rule the
  task describes:
  - session-identity checks (e.g. only the card's author can edit it)
  - phase-lock checks (e.g. editing rejected once a board leaves Submission)
  - facilitator checks (e.g. only the current facilitator can advance phases or hand off)
  - vote-cap enforcement (no visitor exceeds 3 votes on a board)
  Write one test per rule, not one big test that asserts everything at once — a failure should
  point at the specific rule that broke.
- **Templates/partials** — for HTMX-polled partials (see architecture.md §6), assert the partial
  endpoint returns the expected fragment (e.g. the new card's text appears in the response body),
  not the full page shell.

## 4. What NOT to test

- Django admin registration (task 18) — trust the framework; don't write tests asserting admin
  pages render.
- Browser-side polling/JS behavior (HTMX triggers, Alpine state) — this project has no
  browser-automation test layer. If a task's behavior can only be verified by actually clicking
  around in a browser, note that in the PR description instead of faking a test for it.
- Third-party libraries' own behavior (Django's session framework, the ORM, HTMX itself).

## 5. Test data

No factory library is required for a project this small — plain model creation in a test's setup
(or a small local helper function within that app's test file) is enough. Don't add `factory_boy`
or fixtures files unless a task's tests get complex enough to clearly need them.

## 6. Session-based identity in tests

Several rules key off a session-scoped visitor identifier (see tasks.md #6), not a logged-in user.
Use Django's test client's session support (`self.client.session`) to simulate "the same visitor"
across multiple requests in a test, and a second `Client()` instance to simulate "a different
visitor" when testing that authorship/facilitator checks correctly reject other people.

## 7. Definition of done for a task

A task from tasks.md is done when:
1. Its Goal line has at least one passing test demonstrating it.
2. Every explicit rule in its Description (permission check, phase lock, cap, etc.) has its own
   test, including the rejection case, not just the happy path.
3. `pytest` (or `manage.py test`) passes with no unrelated tests broken.
