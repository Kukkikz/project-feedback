# Backlog — Weekly Feedback & Retro Tool

Reference: [plan.md](./plan.md) for scope/requirements, [architecture.md](./architecture.md) for
the Django + HTMX + Alpine architecture (no websockets, no drag-and-drop, polling for
near-real-time updates).

Each task below is scoped to be completable in one session and self-contained enough to hand to
someone who has only read this backlog entry, not the others.

## 1. Project scaffolding with a passing test
Goal: Get an empty Django project running with a CI-style test that passes.
Description: Create a new Django project (single app skeleton is fine, e.g. `retro/`), wire up
the standard project settings for local dev (SQLite is fine for now), and add one trivial test
(e.g. a test that the health-check/home URL returns 200) that passes via `manage.py test` or
`pytest`. No features yet — this task only proves the project boots and the test runner works.

## 2. Project model with shared-link token
Goal: Store a Project and give it an unguessable shared-link identifier.
Description: Add a `Project` model (name, and a random unguessable token used in its URL instead
of a numeric id) with a migration. There is no user authentication in this app — anyone with the
link can access the project — so the token itself is the only access control; make sure it's
generated automatically and is not sequential/guessable.

## 3. Board model with weekly structure
Goal: Store one Board per project per week.
Description: Add a `Board` model belonging to a `Project` (FK), with a `week_start_date` field and
a `phase` field (one of: Submission, Clustering, Voting, Discussion — a plain choices field, no
enum library needed). Each week gets its own Board row; boards are never deleted or merged across
weeks. No view/UI needed yet, just the model, migration, and a couple of tests confirming a board
defaults to the Submission phase.

## 4. Card model for feedback entries
Goal: Store a single piece of retro feedback.
Description: Add a `Card` model belonging to a `Board` (FK), with a `category` field (one of "Went
Well", "Went Wrong", "Blocker"), a free-text `body`, an optional `author_name` (blank means
anonymous), and a `created_at` timestamp. This task is model-only — no submission form or view.

## 5. Card submission view and template
Goal: Let a user submit a new feedback card to a board.
Description: Build a view + template + URL for creating a `Card` on a given Board (assumes the
`Card` model from a prior task already exists — if it doesn't yet, add the minimal fields needed:
category, body, author_name). The form must let the submitter choose to attribute their name or
leave it blank for anonymous. No edit/delete logic here, just create.

## 6. Session-based submitter identity
Goal: Let the app recognize "you" across requests without any login system.
Description: Using Django's built-in session framework (no user accounts, no passwords), assign
each visitor a session-scoped identifier the first time they hit a project's shared link. Store
this identifier alongside anything a visitor creates (e.g. a card) so a later task can check
"is this the same person who created it" — this task only needs to establish and persist the
identifier, not enforce anything with it yet.

## 7. Card edit view with author + phase lock
Goal: Let a card's author edit it, but only before the retro's Clustering phase begins.
Description: Build an edit view for an existing `Card` that only succeeds if (a) the requester's
session identifier matches the one that created the card, and (b) the card's Board is still in
the Submission phase. Assume a session identifier already exists per visitor and a Board has a
`phase` field — if either assumption doesn't hold in the current codebase, add the minimal support
needed to check them. Return a clear rejection (e.g. 403 or a disabled form) once locked.

## 8. Cluster model and assign-to-cluster control
Goal: Let cards be grouped into named clusters without drag-and-drop.
Description: Add a `Cluster` model (belongs to a Board, has a label) and a `cluster` FK on `Card`
(nullable). Build a simple control per card — a dropdown or button, not a drag target — that lets
any visitor assign a card to an existing cluster or create a new one. This deliberately avoids any
JS drag-and-drop library, per the project's chosen architecture.

## 9. Vote model and vote-casting view
Goal: Let each visitor cast up to 3 votes, distributable across cards or clusters.
Description: Add a `Vote` model recording who voted (session identifier — no login) and what they
voted for (a card or a cluster) with a weight. Build a view that lets a visitor cast a vote on a
card/cluster, enforcing server-side that no single visitor exceeds 3 total votes on a board, while
allowing them to stack more than one vote on the same item.

## 10. Board phase transition control
Goal: Let the current facilitator advance a board through its phases in order.
Description: Build a view that advances a Board's `phase` field to the next stage in the fixed
sequence (Submission → Clustering → Voting → Discussion) and rejects any request not made by
whoever currently holds facilitator status for that board. Assume a `phase` field and some
facilitator-identity field exist on Board already; if not, add the minimal field needed to check
"is this requester the facilitator" (a name/session identifier is enough for now).

## 11. Facilitator claim endpoint
Goal: Let any visitor claim the facilitator role for a board, first-come-first-served.
Description: Add a field on Board to track who the current facilitator is (nullable — unclaimed by
default), and a view that lets a visitor claim it, succeeding only if nobody has claimed it yet.
This task does not need to solve simultaneous double-claims perfectly (that's an explicit open
question in plan.md) — a reasonable first-write-wins behavior at the database level is enough.

## 12. Facilitator handoff endpoint
Goal: Let the current facilitator explicitly hand control to someone else mid-retro.
Description: Build a view, usable only by whoever currently holds the facilitator field on a
Board, that reassigns that field to a different named visitor. Assume the facilitator field from
the claim task already exists; this task only adds the transfer action, not the initial claim.

## 13. ActionItem model and creation view
Goal: Let a discussion outcome be captured as a structured, assignable action item.
Description: Add an `ActionItem` model (belongs to a Board, optionally tied to a specific Card or
Cluster, with an `owner_name`, a `due_date`, and a done/not-done status) and a view for creating
one, intended for use during a board's Discussion phase. No editing/deleting logic needed here,
just creation.

## 14. ActionItem status toggle
Goal: Let anyone mark an action item done or not-done.
Description: Build a simple view (e.g. a button/checkbox) that flips an existing `ActionItem`'s
status between done and not-done. Assume the `ActionItem` model already has a status field; if it
doesn't, add the minimal boolean/choice field needed. Action items are never deleted or hidden by
this task — only their status changes, and they keep showing on the board regardless of week.

## 15. Weekly board navigation
Goal: Let a visitor move between a project's weekly boards as separate tabs/pages.
Description: Build a view listing all Boards belonging to a Project (most recent week first) with
links into each one, matching the requirement that each week is its own page rather than one
endless rolling board or a fully-cleared board. Assume the Project and Board models already exist;
this task is purely the navigation/listing view and template.

## 16. Polling partial for the card list
Goal: Make newly submitted or reassigned cards show up in other open browser tabs without a full
page reload.
Description: Extract the board's card list into a template partial and add an HTMX-polled endpoint
(e.g. `hx-trigger="every 2s"`) that returns that partial, per the project's "polling instead of
websockets" architecture decision. This task only wires up the polling for the card list — vote
counts are handled separately.

## 17. Polling partial for vote counts
Goal: Make vote tallies update live across open browser tabs during the Voting phase.
Description: Extract the per-card/per-cluster vote count display into its own template partial and
add an HTMX-polled endpoint refreshing it on a short interval (e.g. every 1-2s), separate from the
card-list polling. Assume votes are stored with a queryable total per card/cluster already; if not,
add the minimal aggregation query needed.

## 18. Django admin registration for all models
Goal: Give whoever runs this app a way to inspect/fix data directly without building custom UI.
Description: Register `Project`, `Board`, `Card`, `Cluster`, `Vote`, and `ActionItem` with Django's
built-in admin site, with reasonable `list_display` columns for each (e.g. Board shows its phase
and facilitator; Card shows category and author). This is an operational/debugging aid, not a
user-facing feature — no permissions work needed beyond Django admin's defaults.
