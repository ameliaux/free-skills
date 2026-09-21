---
name: week-planner
description: Reclaim-style time-blocking. Reads a chosen set of work from any connected issue tracker (Linear, Jira, Asana, Monday, etc.) and lays free, moveable blocks onto your calendar around your meetings. Asks which tool and which scope every run. Use when the user says "plan my week", "time-block my tasks", "plan my roadmap", or runs /week-planner.
---

# /week-planner, Reclaim-style time-blocking

Read the user's calendar and a chosen set of tracker work, then lay down moveable focus blocks so they can finish it, placed around their real meetings, front-loaded, earliest-first. They review and drag the blocks; the blocks never bind them.

**On-demand, not a daemon.** It plans and reconciles when invoked. It does not run in the background auto-defending time the way Reclaim does. Rerun it to re-plan after meetings move or work completes.

Standing defaults live in the user's config (see `example-config.md`). Read them each run and offer them as the one-tap answer so the user can just say "usual."

## Confirm before running (one summary, every run)
Do not interrogate field by field. Resolve the settings from saved defaults plus any tokens passed, then show the whole thing back as one short summary and ask for adjustments before creating anything. For example: "Set to your usual: assigned issues from Linear, this week, sprint, free + visible, max 3/day, on your work calendar. Any adjustments?" The user tweaks in plain language or says go. The first run (or a new stack) walks the fields once to set the usual, then saves it; every later run just echoes the resolved settings, always including the scope so the user confirms what is being pulled. The settings it resolves and shows:
- **Plan from (ALWAYS ask this, every run, even with a mode):** first which tracker, any connected issue tool (Linear, Jira, Asana, Monday, etc.); if only one is connected use it, if several, ask which. Then which scope: everything across all projects, only items assigned to the user, a specific project, a cycle, or a roadmap/milestone. Never defaulted. The run always confirms exactly what it is pulling before spreading it across the timeframe.
- **Horizon:** this week (default), the month, a quarter (3 months, the standard planning stint), or up to 6 months for a roadmap.
- **Cadence:** dense (pack the earliest days to the daily cap, leave later days emptier) or sparse (spread evenly across the horizon).
- **Daily window:** the user's working hours (default mornings-leaning).
- **Block length:** the tracker estimate, else 60 min (default).
- **Max blocks per day:** default 3.
- **Availability (setup default = free):** free, moveable, never blocks their booking. Set once at setup and generally kept free. Override a single run with the `busy` token.
- **Visibility (default = visible):** blocks use the calendar's normal visibility by default. Override a single run with the `private` token to hide it.
- **Color:** a chosen event color, so the blocks read as suggestions against real meetings.

## Modes (composable, mix and match)
Invoke `/week-planner` with any combination of the tokens below, in any order. Anything omitted uses the saved default. Independent axes, not fixed presets, so `quarter loose private` is valid. `usual` is shorthand for the common combo. The user can name and save a new named combo any time.

**Timeframe (scope + source):**
- `week` (default): this week, assigned items.
- `month`: the month ahead, assigned items.
- `quarter`: 3 months, from a project or roadmap.
- `roadmap` or `6mo`: up to 6 months, from a project or roadmap.

**Density (how it fills the timeframe):**
- `sprint`: dense, pack the earliest days to the daily cap.
- `loose`: sparse, spread evenly across the timeframe.

**Load:**
- `light`: fewer blocks per day (1 to 2).

**Tack-ons (any timeframe/density):**
- `private`: hide the blocks (default is visible).
- `busy`: mark them busy instead of free (default, and the general setup, is free).

`usual` = week + assigned + normal density + free + visible (the defaults).
Examples: `/week-planner week sprint`, `/week-planner light private`, `/week-planner roadmap loose`.

A run only manages blocks inside its own timeframe. Running `week` after a `roadmap` run re-plans this week without duplicating or deleting the roadmap's later blocks; it only clears blocks whose item is Done or Canceled.

## 1. Read the calendar (the busy map)
`list_events` on the user's work calendar (from config) across the horizon. Record every real meeting's start and end. Blocks must never overlap a meeting.

## 2. Pull the work (tool-agnostic)
Detect the connected tracker MCPs first (a quick health check). Use whichever tool the user picked in the config; if only one is connected, use it. Pull the chosen scope:
- **Everything:** all open items across all projects.
- **Assigned:** items assigned to the user.
- **Project / cycle / roadmap / milestone:** items in that container.
Normalize each item to: title, priority, due date, estimate, status, project, url (map from whatever the tool calls them). Keep only active items (drop that tool's done / closed / cancelled states). **Dedupe:** same title + same project = one. **Skip recurring checklist-style items** (quick weekly ticks, not focus work).

## 3. Rank and lay out per cadence
Higher priority first, then soonest due date; overdue and due-today always take the earliest slots. Then apply cadence: dense fills the earliest days to the daily cap before moving on; sparse distributes evenly across the horizon.

## 4. Place the blocks
Create each event on the work calendar with:
- `availability` per config (default free).
- event color per config.
- `visibility` per config (default visible; or private).
- Title `<ID>, <short task>`; description = priority note + the item URL.
- Sequenced around the meetings from step 1, within the window, at most the per-day cap.
- Length = the item's estimate, else 60 min. Flag any item with no estimate so the user can set one.

## 5. Reconcile on every run (the "done" behavior)
Before placing anything, `list_events` for the horizon, find existing blocks the skill made, and check each one's current tracker status:
- Item **Done or Canceled** -> **delete its future block** (already-elapsed blocks stay as history). Report what was cleared.
- Item still open and already blocked -> leave it, no duplicate. Move it only if its priority or due date changed.
- New open item not yet blocked -> add it.
Completed work falls off automatically. Only touch the skill's own blocks. Never delete or move the user's meetings or events they created by hand.

## 6. Report
List the blocks by day. Note completions cleared, and any item defaulted to 60 min for want of an estimate.

## Notes
- The calendar must be connected with owner or writer access. If it returns free/busy only, the connector is on the wrong account; tell the user to reconnect it.
- Keep everything on the one work calendar named in config.
