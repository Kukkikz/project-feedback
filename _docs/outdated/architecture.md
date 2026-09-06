# Architecture — Weekly Feedback & Retro Tool

Implements the tech stack chosen in [plan.md](./plan.md) §10 (Option A): Django + server-rendered
templates + HTMX + Alpine.js, no websockets, no drag-and-drop.

## 1. Overview

A single Django project, deployed as one WSGI app for one team (single-tenant, no auth beyond
shared links). All interactivity — submitting cards, clustering, voting, phase changes — is a
normal HTTP request that returns either a full page or an HTML partial. "Live" updates across
browsers are simulated by HTMX polling a partial on an interval; there is no websocket server,
no channel layer, and no background process beyond the Django app itself.

```
Browser (template + HTMX + Alpine)
   │  HTTP GET/POST (full page or partial)
   ▼
Django views (WSGI)
   │  ORM
   ▼
Database (Postgres/SQLite)
```

## 2. Django apps

A small number of apps, split by domain concept rather than by layer:

- **projects** — Project model, shared-link access control, membership.
- **boards** — weekly Board, phase state machine (Submission → Clustering → Voting →
  Discussion), facilitator claim/handoff.
- **cards** — feedback Card (Went Well / Went Wrong / Blockers), Cluster, Vote.
- **actions** — ActionItem (owner, due date, done/not-done), persists across weeks.

Each app owns its models, views, and templates; there is no separate "api" app since views return
HTML (full pages or HTMX partials), not JSON.

## 3. Data model (sketch)

- **Project** — id, name, shared_link_token
- **Board** — id, project (FK), week_start_date, phase (enum), facilitator (nullable, just a
  display name since there's no auth), locked_at
- **Card** — id, board (FK), category (went_well / went_wrong / blocker), body, author_name
  (nullable — anonymous if blank), created_at, cluster (FK, nullable)
- **Cluster** — id, board (FK), label
- **Vote** — id, card_or_cluster (FK), voter_identifier (session-based, no login), weight
- **ActionItem** — id, board (FK), card_or_cluster (FK, nullable), owner_name, due_date, status
  (done/not_done)

Exact schema (field types, indexes, constraints) is still an open question per plan.md §11 and
will be finalized during implementation, not here.

## 4. Access model

No authentication. A Project is reached via an unguessable shared-link token in the URL. Django
sessions (cookie-based, no login) are used only to:
- remember which name/session submitted a card, so "editable by author before retro starts" can
  be enforced without real auth
- track per-voter vote allocation (3 votes per person) via a session-scoped voter identifier

This is enforced at the view level, not via Django's auth system — there are no User accounts.

## 5. Retro phase flow

The Board's `phase` field is the single source of truth for what actions are allowed:

1. **Submission** — Card create/edit views open; Clustering/Voting views reject requests.
2. **Clustering** — Cards become read-only for editing (author lock); "assign to cluster" view
   opens (dropdown/button, no drag-and-drop).
3. **Voting** — Clustering view closes; vote-cast view opens, capped server-side at 3 votes per
   voter session, distributable across cards/clusters.
4. **Discussion** — Voting closes; ActionItem create view opens, scoped to a card/cluster.

Phase transitions are a single POST from whoever currently holds facilitator status; the view
checks the requester matches the current facilitator (or handoff target) before advancing.

## 6. Real-time simulation via polling

No Channels, no Redis, no websockets. Any part of the board that needs to reflect other users'
actions (new cards arriving, cluster assignments changing, vote counts updating) is rendered as an
HTML partial included via HTMX with a polling trigger, e.g.:

```html
<div hx-get="/boards/{id}/cards-partial/" hx-trigger="every 2s" hx-swap="outerHTML">
  {% include "cards/_card_list.html" %}
</div>
```

- Poll interval: 1-2s, tuned per-partial (e.g. vote counts may poll faster than the card list).
- Each poll is a normal Django view returning a template fragment — no separate serialization
  layer.
- Upgrade path (not built now): replace the polled endpoint with a Server-Sent Events stream, or
  Django Channels, without changing the surrounding page structure — the partial-swap boundary is
  the seam where that swap would happen later.

## 7. Clustering UI (no drag-and-drop)

Each card renders with an "assign to cluster" control (a `<select>` or set of buttons) instead of
being draggable. Submitting it is a normal POST that updates `Card.cluster` and re-renders the
card-list partial. This avoids a JS drag-and-drop library and behaves identically on touch/mobile.

## 8. What's explicitly not in this architecture

Per plan.md §9, and reinforced by the Option A simplification:
- No websocket/channel layer of any kind.
- No drag-and-drop library.
- No JSON API layer (views return HTML, not serialized data) — revisit only if a future client
  (mobile app, etc.) needs one; see plan.md §10 Option E as the fallback path.
- No notifications, no cross-week analytics, no external tracker sync, no SSO.

## 9. Open questions carried over from plan.md §11

Unresolved and not addressed by this architecture doc:
- Deployment/hosting approach.
- Exact DB schema (types, constraints, indexes).
- Whether "locked once retro starts" applies to deleting cards, not just editing.
- Facilitator-claim race condition (two people claiming simultaneously).
- Any limit on number of projects/boards.
