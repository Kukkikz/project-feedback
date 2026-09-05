# Weekly Feedback & Retro Tool — Project Scope

## 1. Purpose
A tool for teams to submit weekly feedback on a project and run a structured retrospective from that feedback.

## 2. Users
- All team members can contribute feedback (not just the project owner).
- No authentication for now — access via a shared link per project (MVP-style).

## 3. Feedback Submission
- **Fields:** Structured + free text, using the classic retro format:
  - Went Well
  - Went Wrong
  - Blockers
- **Attribution:** User chooses per card — named or anonymous.
- **Editing:** Cards are editable by their author anytime before the retro starts; locked once it begins.
- **Cadence:** No reminders — people submit on their own weekly rhythm.

## 4. Weekly Cycle Structure
- Each week is its own tab/page (not a fully cleared board, not an endless rolling board).
- Action items persist and stay visible across weeks until marked done.

## 5. Retro Flow
Enforced, facilitator-controlled phases:
1. **Submission** — feedback collected async during the week.
2. **Clustering** — manual drag-and-drop; anyone can group similar cards.
3. **Voting** — dot-voting, 3 votes per person, distributable (can stack multiple votes on one card/cluster).
4. **Discussion** — outcomes captured as structured action items (owner + due date).

### Facilitator Role
- Anyone can claim facilitator for that week's retro (first to claim it).
- Facilitator controls phase progression.
- Facilitator can explicitly hand off control to another person mid-retro.

## 6. Voting & Clustering Mechanics
- **Clustering:** No drag-and-drop — cards are assigned to a cluster via a simple "assign to cluster" control (dropdown/button per card). Avoids a JS drag-and-drop library and works the same on mobile.
- **Updates:** Near-real-time via short-interval polling (HTMX polling every 1-2s), not websockets. Good enough for small-group, low-frequency actions (one team, occasional drags/votes) and avoids running a websocket server.

## 7. Action Items
- Structured: owner + due date, tied to a specific topic/card/cluster.
- Persist across weeks on the board.
- Status: manually marked done/not-done (no auto-carry-forward logic beyond just staying visible).

## 8. Project & Access Structure
- One board per project (not per team, not shared across projects).
- Visibility: invite-only — only members of that project can see its board.
- Single-tenant: one deployment for one team/organization (no multi-tenant isolation needed).

## 9. Explicitly Out of Scope (for now)
- No cross-week analytics or trend tracking (e.g. morale over time) — each week stands alone.
- No notifications of any kind (no email, no in-app) — fully passive, users check the site themselves.
- No external tracker sync (e.g. Jira/Trello) for action items.
- No automatic card clustering (manual only).
- No SSO/password auth (shared link only, for now).

## 10. Tech Stack
- **Backend:** Django (plain WSGI — no ASGI server needed)
- **Frontend:** Django templates (server-rendered) + HTMX for partial updates + Alpine.js for small bits of client-side state (e.g. vote button state)
- **Real-time layer:** None (no Channels, no websockets, no Redis). "Live" updates are simulated via HTMX polling (`hx-trigger="every 1-2s"`) re-fetching board partials.
  - Simplification rationale: retro sessions are one small team acting infrequently, so a short poll feels responsive enough without the operational cost of a websocket server + channel layer.
  - Revisit if polling proves laggy in practice — an upgrade path exists to Server-Sent Events (one-way push, lighter than full websockets) or Django Channels later, without changing the overall server-rendered approach.
- **Clustering UI:** No drag-and-drop library — cards are assigned to a cluster via a simple control (dropdown/button), not dragged. Removes the need for a JS DnD library and its touch/mobile edge cases.

## 11. Open Questions / Not Yet Decided
- Deployment/hosting approach.
- Exact DB schema design.
- Whether "locked once retro starts" applies to editing only, or also deleting cards.
- What happens if two people try to claim facilitator at the same time.
- Whether there's any limit on number of projects/boards.