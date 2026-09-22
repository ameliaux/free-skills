# Output adapter: notion-board

An output adapter tells the skill **where the briefing goes and how it's stored, deduped, and rendered**, so the engine's logic stays identical no matter the destination. **The engine owns the coordination logic (dedupe on source reference, per-surface watermarks, read-before-write); the adapter only exposes the primitives for its platform.** Every adapter answers four things: **Target · State · Persist · Render.**

**Adapters come in two families, matched to the *kind* of target:**
- **Document surfaces** (note-taking apps: Notion, Google Docs, a Markdown file) — the briefing is a **living document/board**, rendered and updated in place. `notion-board` (this) and `markdown-file` are here.
- **Trackers** (PM/issue tools: Linear, Jira, Asana) — items become **native issues** in the tool, created/updated/closed through *its* MCP and workflow. The adapter integrates, it does NOT write a document into the tool. `linear`, `jira`, and `asana` are here.

Copy this file to `outputs/<your-name>.md`, rewrite the four sections for your system, then set `output: adapter: <your-name>` in your profile.

## Target
Notion. From the profile: a **Briefing page** (readable wrapper) containing an inline **Board** data source. IDs come from the profile's `Output` block. If missing, `/pm-sweep setup` scaffolds them.

## State (what the engine reads and writes to coordinate)
The engine needs three primitives from every adapter. This is what makes multi-user and incremental work anywhere, not just here:
- **List existing items (with their source reference).** `SELECT url, "Item", "Link", "Status", "Pinned", "Note" FROM <Board>`. The engine dedupes and reconciles against this **before** writing, so two people's runs (and repeat runs) never double up.
- **Per-surface watermarks.** NOT one global "last updated." A small **Sweep State** area maps each surface (channel / source) to its last-swept timestamp and who swept it. Each run reads it, sweeps only surfaces due, and advances only the surfaces it touched. (For notion-board: a tiny `Sweep State` inline table or a fenced block on the Briefing page.)
- **The dedupe key is the source reference (`Link`), which is identical for everyone**, so a duplicate is provable, not guessed. Title is the fallback for the same item arriving via two different sources.

## Persist (how each reconciled item is written)
- **Dedupe on the source reference first** (`Link`), else normalized `Item` title. Never create a second row for the same item.
- **Action task** → upsert a Board row (`Status` Todo/In Progress), on the active views.
- **Closed** → set `Status = Done`. **Waiting** → `Status = Waiting`. **Punted** → `Status = Punted` (human territory, never auto-set or un-set).
- **Intelligence (documentation task)** → a row prefixed `📌 Context:`, detail in `Note`, `Horizon = Someday`, `Status = Done`.
- **Conflict / Pinned / human-Noted row** → leave untouched; drop a `[scan:<runner>]` Note only.
- Always set `Link` to the source page URL (the dedupe fingerprint + click-through).
- On **create**, stamp `Assigned` = today; never change it on update.

## Render (the human-facing view)
- The **page header** carries, in order: `🕐 Last updated <timestamp>` (a *display* of the most recent sweep, separate from the per-surface Sweep State), a **How to use this board** blurb, and a **Today** summary (focus lead + ~3 sentences). Rewrite Last-updated + Today each run via `notion-update-page`; never drop the how-to.
- The **Board** shows grouped views (by horizon / by person / by stream). The adapter keeps rows current; it doesn't recreate views each run.
- **View type is a choice**, set in the profile: table, **kanban** (grouped by Status or Horizon), **calendar** (by Due), or **by sprint/cycle**. Default is grouped tables. A tracker adapter renders in that tool's native board/sprint structure instead.

---

### Writing a custom adapter (the `.md` escape hatch)
Same four headings, your system. The engine logic never changes; you only tell it how your platform stores things:
- **Target** — which connected MCP/tool + how to locate the destination (IDs, a doc URL, a file path).
- **State** — how to *list current items with their source reference*, and *where per-surface watermarks live* on your platform. This is what makes dedupe and multi-user work for you.
- **Persist** — how to create/update one item, deduped on the source reference, never clobbering a human.
- **Render** — your formatting, and where the human-facing "last updated" shows.

Examples:
- `markdown-file` (document family): items = lines each carrying a source ref; **State** = a `swept:` map in the file's frontmatter (per-surface timestamps) + the item refs themselves; dedupe = match the ref.
- `linear` (tracker family): items = native issues carrying the source ref (a link/attachment or custom field); **State** = a pinned config issue or labels holding per-surface watermarks; dedupe = search by ref; statuses map to Linear's workflow.
