# Design System

Purpose: this project's tasks (tasks.md) are built one small, independent piece at a time,
possibly across many separate sessions/contributors. Without a shared reference, each task's
templates will invent their own spacing, colors, and component markup, and the UI will visibly
drift. This document is that shared reference — it applies whether or not a task's description
mentions styling.

No CSS/JS framework is used — per architecture.md, this is a server-rendered Django app with HTMX
and Alpine.js, and pulling in Tailwind/Bootstrap would be more machinery than a single-tenant
internal tool needs. Instead: one small hand-written stylesheet with CSS custom properties as
tokens, described below.

## 1. Base template

Every page extends a single `base.html`, never builds its own `<html>`/`<head>`. `base.html`
defines these blocks and nothing else:
- `title`
- `content` — the page body
- `extra_head` — optional, for a page-specific `<style>`/`<script>` tag (used sparingly)

Any HTMX-polled partial (architecture.md §6) is its own template starting with an underscore
(e.g. `_card_list.html`, `_vote_counts.html`) and never extends `base.html` — it renders only the
fragment that gets swapped in.

## 2. Design tokens (CSS custom properties)

Defined once in a single stylesheet (`static/css/base.css`), referenced everywhere else — no
hard-coded colors/spacing in templates or per-app CSS files.

```css
:root {
  /* color */
  --color-bg: #ffffff;
  --color-text: #1a1a1a;
  --color-border: #d9d9d9;
  --color-accent: #2f6f4f;      /* primary actions: submit, vote, claim facilitator */
  --color-danger: #a6423a;      /* destructive/locking states, e.g. "locked" badge */
  --color-muted: #6b6b6b;       /* timestamps, secondary text */

  /* category colors, used consistently for Went Well / Went Wrong / Blocker */
  --color-went-well: #2f6f4f;
  --color-went-wrong: #a6423a;
  --color-blocker: #b8860b;

  /* spacing scale */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 16px;
  --space-4: 24px;
  --space-5: 40px;

  /* type */
  --font-body: system-ui, sans-serif;
  --font-size-base: 16px;
  --font-size-small: 14px;
  --radius: 6px;
}
```

Any new color/spacing value a task seems to need should be added here as a token, not inlined —
if it doesn't fit an existing token, that's a signal to raise it rather than improvise.

## 3. Core components

These are the recurring UI pieces across the retro flow. A task touching one of these must reuse
its existing markup/class names rather than inventing a parallel version.

- **Card** (`.card`) — one piece of feedback. Always shows: category badge (colored per §2),
  body text, author name or "Anonymous", timestamp. When clustered, shows its cluster label.
- **Category badge** (`.badge.badge--went-well` / `--went-wrong` / `--blocker`) — small pill,
  colored per the category tokens above. Used both on cards and in category-filter controls.
- **Cluster group** (`.cluster`) — a labeled container of cards assigned to it (per architecture.md
  §7, no drag-and-drop — cards are assigned via a control, not dragged into this container).
- **Vote control** (`.vote-control`) — shows current vote count for a card/cluster and a button/
  stepper to add a vote, disabled once the visitor has spent all 3 votes.
- **Phase banner** (`.phase-banner`) — persistent header on a board page showing the current phase
  (Submission/Clustering/Voting/Discussion) and who the facilitator is, if claimed.
- **Action item row** (`.action-item`) — owner name, due date, and a done/not-done toggle control.
- **Buttons** — one primary style (`.btn`, uses `--color-accent`) and one plain/secondary style
  (`.btn--secondary`, uses `--color-border`). No third button style without a documented reason.

## 4. HTMX conventions

- Polling intervals are standardized, not chosen per-task: card list and cluster views poll every
  **2s**; vote counts poll every **1s** (voting is the moment simultaneity matters most, per
  plan.md §6). Don't pick a different interval without updating this doc.
- Every HTMX-polled endpoint's URL ends in `-partial/` (e.g. `/boards/<id>/cards-partial/`) so
  it's visually obvious in urls.py which views return fragments vs. full pages.
- `hx-swap="outerHTML"` is the default swap strategy for polled partials, so the polled element
  fully replaces itself each tick — don't mix in `innerHTML`/`beforeend` without a reason.

## 5. Alpine.js conventions

Alpine is for small, page-local UI state only (e.g. "is this form expanded", "has this button
been clicked this render") — never for state that must sync across visitors, which belongs to
the HTMX polling layer instead. Keep `x-data` objects small and inline on the component they
control; don't introduce a global Alpine store.

## 6. Accessibility baseline

- Every form control has a `<label>`; no placeholder-only inputs.
- Interactive elements are real `<button>`/`<a>` tags, never a `<div onclick>`.
- Color is never the only signal — category badges and the phase banner also carry text, not just
  color, so the app remains usable without color differentiation.

## 7. What this document does not cover

Exact pixel-level layout/responsive behavior is intentionally left to each task's judgment — this
document fixes the vocabulary (tokens, component names, conventions) so pages compose together
visually, not a pixel-perfect mockup. If a task needs a genuinely new component not listed in §3,
add it here in the same PR rather than leaving it undocumented.
