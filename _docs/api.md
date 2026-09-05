# API (HTTP Interface)

A note on naming: per [architecture.md](./architecture.md) (Option A), this app has **no JSON API**
— views return full HTML pages or HTMX partials, not serialized data. "API" here means the app's
HTTP interface: its routes, what each expects, and what it returns. Treat this document as the
contract for urls.py + views across all apps, so tasks built independently (tasks.md) land on the
same routes instead of each inventing its own.

If a real JSON API is ever needed (e.g. a future mobile client), that's a separate addition — see
plan.md §10 Option E — not a change to the routes below.

## Conventions

- Routes are namespaced per Django app: `/projects/...`, `/boards/...`, `/cards/...`, etc.
- A project is addressed by its shared-link token (architecture.md §2), never by numeric id, in
  any URL a visitor sees.
- Every HTMX-polled endpoint's path ends in `-partial/` and returns a template fragment, not a
  full page (design-system.md §4).
- Mutating routes (create/update/vote/claim/etc.) are POST; everything else is GET.
- No route requires a request body format beyond standard HTML form encoding — no JSON request
  bodies anywhere.
- Permission/state failures (wrong author, wrong phase, wrong facilitator, vote cap exceeded)
  return a 403 with a plain-text or minimal HTML explanation, per testing-guidelines.md §3.

## Projects

| Method | Path | Purpose | Notes |
|---|---|---|---|
| GET | `/p/<token>/` | Project home — lists its boards (weekly navigation, tasks.md #15) | Establishes the visitor's session identifier on first hit (tasks.md #6) |

## Boards

| Method | Path | Purpose | Notes |
|---|---|---|---|
| GET | `/p/<token>/boards/<board_id>/` | Full board page for a given week | Shows current phase, facilitator, and embeds the polled partials below |
| POST | `/p/<token>/boards/<board_id>/advance-phase/` | Advance to the next phase in sequence | Facilitator-only (tasks.md #10) |
| POST | `/p/<token>/boards/<board_id>/claim-facilitator/` | Claim facilitator role | Only succeeds if unclaimed (tasks.md #11) |
| POST | `/p/<token>/boards/<board_id>/handoff-facilitator/` | Reassign facilitator to another named visitor | Current-facilitator-only (tasks.md #12) |

## Cards

| Method | Path | Purpose | Notes |
|---|---|---|---|
| POST | `/p/<token>/boards/<board_id>/cards/create/` | Submit a new card | Body: category, body text, optional author_name (tasks.md #5) |
| GET/POST | `/p/<token>/cards/<card_id>/edit/` | Edit an existing card | Author + Submission-phase only (tasks.md #7) |
| POST | `/p/<token>/cards/<card_id>/assign-cluster/` | Assign a card to a cluster (create-or-choose) | No drag-and-drop; simple control (tasks.md #8) |
| GET | `/p/<token>/boards/<board_id>/cards-partial/` | Polled card list fragment | 2s poll (design-system.md §4, tasks.md #16) |

## Clusters

| Method | Path | Purpose | Notes |
|---|---|---|---|
| POST | `/p/<token>/boards/<board_id>/clusters/create/` | Create a new cluster label | Used inline from the assign-to-cluster control |

## Votes

| Method | Path | Purpose | Notes |
|---|---|---|---|
| POST | `/p/<token>/cards/<card_id>/vote/` | Cast a vote on a card | Capped at 3 total per visitor per board (tasks.md #9) |
| POST | `/p/<token>/clusters/<cluster_id>/vote/` | Cast a vote on a cluster | Same 3-vote cap, shared with card votes on that board |
| GET | `/p/<token>/boards/<board_id>/vote-counts-partial/` | Polled vote-count fragment | 1s poll (design-system.md §4, tasks.md #17) |

## Action Items

| Method | Path | Purpose | Notes |
|---|---|---|---|
| POST | `/p/<token>/boards/<board_id>/action-items/create/` | Create an action item | Optionally tied to a card/cluster; owner + due date (tasks.md #13) |
| POST | `/p/<token>/action-items/<action_item_id>/toggle/` | Flip done/not-done | tasks.md #14 |

## Not part of this interface

- Django admin (`/admin/`) is a separate, framework-provided interface (tasks.md #18) — not
  documented here since it's not app-specific routing.
- No authentication endpoints (login/logout/register) exist — access is entirely via the shared
  project link (plan.md §2, §8).
