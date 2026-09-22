---
name: pm-sweep
description: Use when the user types /pm-sweep, asks for "the briefing", the daily check-in, "what's happening / what needs doing", or wants the shared team board reconciled. Sweeps every connected work surface (Slack, Linear, Notion CRM, freeform note pages/text, and whatever else is mapped) for what changed since last run, compares against the existing Briefing table WITHOUT clobbering human or teammate edits, reports the deltas, then proposes actions. Incremental by default; /pm-sweep full forces a fresh sweep.
---

# /pm-sweep — the shared daily briefing

**Discovery comes first** — a one-time (re-runnable) onboarding: install the skill, run it, and it connects to all your PM tools and picks up your people, surfaces, and categories, then you curate and it scaffolds (`/pm-sweep setup`). After that, the recurring run is three phases: **Intake → Assess → Output.** Pull what changed (Intake), reconcile and calibrate with PM judgment (Assess), then write to the chosen destination (Output). **Intake and Output are swappable I/O per user; Assess is the fixed engine, identical for everyone.** You do the mechanical prep and propose; the humans steer.

**Compare before you write. Propose before you decide. Never clobber a human edit.**

## Load tools first
Confirm the MCPs this run needs are connected **in this client** — the Notion, Slack, task-tool, and notes MCPs named by the profile (in Claude.ai this is a tool search; in Claude Code, `/mcp`; elsewhere, the client's MCP panel). If a mapped source has no connected MCP it degrades gracefully in Phase 1 — but tell the user it's missing rather than silently skipping.

## Config — read the active profile
Load the **active profile** for this run's **sources, streams, owners, and output**: if the command names one (`/pm-sweep <profile>`), use it; if exactly one real profile exists in `profiles/`, use it; if several exist, ask which; if none exists, run `/pm-sweep setup` first. The profile maps each **role** (task / chat / CRM / notes / conversations log) to a connected MCP plus specifics (channel names, team names, data-source IDs), names the **output adapter** (default `notion-board`, defined in `outputs/<name>.md`), and may set the **runner name** (used in `[scan:<runner>]` tags) and a **sign-off** line (used in Output E). The Assess engine below is source-agnostic and identical no matter what the profile contains. **If no profile exists, run `/pm-sweep setup` first.** The bundled `profiles/example.md` is a **template, not a live profile** — if only it exists, treat the install as unconfigured and run `/pm-sweep setup` before sweeping. The `Board`, `Activity`, `Deals` etc. in the steps resolve from the active profile.

## Commands
- `/pm-sweep` — the daily incremental briefing (default).
- `/pm-sweep full` — ignore the per-surface watermarks; sweep everything.
- `/pm-sweep status` — connectivity readout only; no sweep.
- `/pm-sweep setup` — Discovery/onboarding; writes `profiles/<name>.md`.
- `/pm-sweep curate` — teams: skip intake entirely; read the board as it stands and refresh only the header/Today summary (Output B). No row writes.
- `/pm-sweep <profile>` — run against a named profile in `profiles/`.
Plain words count too: *"the briefing"*, *"what's happening"*, *"what needs doing"* all mean `/pm-sweep`.

---

# Phase 1 — INTAKE (pull what changed)

Intake runs against the sources **Discovery** already mapped into the profile; it does not re-learn your world each time.

**A. Health check.** Check which MCPs are actually connected in this session, then confirm each source **the profile maps** is live; skip any that are down or need auth and note it in one line (graceful degradation). **Never name or report on channels, teams, or data sources the profile doesn't map** — an unmapped tool doesn't exist for this run. This is a connectivity check, *not* discovery. `/pm-sweep status` prints just this readout.

**B. Watermark.** Read the `Last updated <timestamp>` token from the output (the notion-board adapter keeps it in the Briefing header); use it as `since`. If absent, use 7 days ago. `/pm-sweep full` ignores the watermark and sweeps everything. **Multi-user:** the watermark is **per surface** (see Coordination under Portability), each run reads each of its profile's surfaces' own last-swept time and sweeps only those, so people in different channels never collide on one global timestamp.

**C. Pull deltas since `since`** from every live source in the profile:
- **CRM — Activity (open next-actions):** `SELECT "Name","Owner","Type","date:Follow-up date:start","Company","Deal" FROM "<Activity>" WHERE "Follow-up needed"='__YES__' AND ("Status" IS NULL OR "Status"!='Done')`
- **CRM — Deals (open pipeline + next steps):** `SELECT "Name","Owner","Stage","Value","Next step","date:Expected close:start" FROM "<Deals>" WHERE "Stage" NOT IN ('Closed Won','Closed Lost')`
- **Task tool (Linear/Jira):** issues updated since `since`.
- **Chat + freeform inbox:** search since `since` over the signal channels + any note page/file. **Never read DMs, group DMs, or private channels — only the channels the profile explicitly maps. This holds for every user, every run, no exceptions.** Extract decisions and action items (owner @mentions, "next:", "we should", "TODO"). **Attribute each item to whoever raised it** — this is a team surface.

This produces the **proposed set** — what the sources say *should* be true.

---

# Phase 2 — ASSESS (reconcile → calibrate → propose)

The fixed engine. Same logic for every user, whatever fed Intake.

**A. Reconcile against the current board.** Pull the full board (`SELECT * FROM "<Board>"`). Match each proposed item to an existing row by `Link` first, else by normalized `Item` title. Sort every row into one bucket:
- **New** — proposed, no matching row → will add.
- **Aligned** — row exists and the source agrees → no change.
- **Safe update** — row exists, source has newer info, and the affected field is *empty* or the row is clearly scan-owned (has a `Link`, `Pinned` off, no human `Note`) → will update.
- **Conflict** — row exists but a human value disagrees with the source. A row is **human territory** if *any* of: `Pinned` checked, no `Link` (typed in by a teammate), or it carries a human `Note`. **Never overwrite human territory.** Hold and list for review.
- **Human-authored** — a row with no matching source at all → keep as-is. Only fill genuinely empty Stream/Owner/Horizon when confidently inferable; never touch filled fields.
- **Closed** — the source shows the item done/won/lost → propose `Status = Done`.
- **Intelligence → documentation task** — a running update or standing context with **no next step**. Do NOT make it an action Todo, and do NOT open a conversation-log page (that DB is for real conversations/meetings/decisions). Record it as a **documentation task**: a row prefixed `📌 Context:` with the detail in `Note`, tagged to its Stream/Owner, `Horizon = Someday`, `Status = Done`. Recording it *is* completing it, so it lands in history, off the active views.

**Status semantics.** `Waiting` = open but blocked on someone or something external; don't nag it as overdue, surface it under a `⏳ Waiting on` line, and if a source shows the blocker cleared (a reply landed, procurement approved), propose `Waiting → Todo`. **A reach-out or follow-up whose *outcome* needs their response is `Waiting`, not `Done`:** once the human has sent it, their part is complete, but the goal (booking the call, closing the loop) hinges on a reply they cannot force. Done means the objective landed; Waiting means "I did everything I could and now it is on them." Don't mark such items Done just because the action was taken. `Punted` = the human deliberately set it aside (might not happen); treat it as **human territory**, never resurface it as New, nag it, or auto-un-punt it, only the human revives it. Neither Waiting nor Punted counts as active work when calibrating capacity.

**B. Calibrate to capacity.** Derive each item's fields:
- **Stream** from the source (Deal → its stream; Activity → its deal's stream; chat → channel/topic; task → label).
- **Owner** from Deal/Activity `Owner` or chat attribution.
- **Horizon** from Due / Follow-up date **and lead time**: `Today` (due/overdue or starts today), `This week`, `Next week`, `Next month`, else `Someday`. **Pull prep forward** (a Wednesday deliverable that needs 2 days lands in *this* week). Subtract **fixed obligations** first (Calendar meetings if wired, Finance hard dates); if a horizon is over-committed, add a capacity note. **Read the sources' own planning structure as signal:** due dates, sprints/cycles, and milestones. A due date drives Today/overdue; a sprint or cycle maps to a horizon, or stays as its own grouping when the output is organized by sprint.

**C. Report the comparison in chat — before writing.** A short structured diff:
`✓ Done/moved since last run (n)` · `＋ New (n)` · `📌 Context captured (n)` · `⏳ Waiting (n)` · `↑ Safe updates (n)` · `⚠ Conflicts held (n)` · `✋ Human-authored kept (n)`.
**Lead with `✓ Done / moved since last run`** — board rows a human ticked Done, deal stage/next-step changes, new Activity — so the team sees what got *finished* before what's new. (The Notion CRM has no queryable last-edited timestamp, so detect this by reconciling current state against the board, not an edit-time filter.) List conflicts explicitly with both values ("*Website relaunch*: you have **This week**, the tracker says **Next week**; kept yours"). Attribute teammate items by author. Don't narrate every aligned row.

**D. Suggested actions (the PM layer).** A short *ranked* list drawn from the reconciled state — offered, not executed:
- Overdue / due-today items and who owns them.
- Deals or leads gone quiet (no activity in N days) → suggest a nudge.
- Over-committed horizons → capacity flag ("Today has 6 items across 2 people; 3 realistic — defer which?").
- New unowned items → suggest an owner.
- Items ripe to promote into the task tool.
Each one line, one proposed action. The human picks; **you do not auto-create issues or send anything** — that's their call.

---

# Phase 3 — OUTPUT (write / render / sync via the adapter)

The adapter named in the profile decides *how* the assessed items land (document surface vs tracker; see `outputs/<name>.md`). Default `notion-board`:

**A. Apply only the safe writes.** Create New rows, fill empty fields, mark Closed `Status = Done`, write the `📌 Context:` documentation rows. **Leave every Conflict and Pinned/human row untouched.** Set `Link` to the source page URL so each row clicks through, and **stamp `Assigned` = today's date on every row you create** (the date it landed on the board; never change it on an update). **Prefix every Note *you* write with `[scan]`** (conflict trails, status changes, context detail) so it's distinguishable from a human's Note — a human Note is sacred and protects the row; a `[scan]` Note does not. In a multi-user setup, tag the runner (`[scan:<runner>]`, the name from the profile) so appends are attributable and one person's sweep can tell its own prior writes from a teammate's. Hold a conflict by dropping a one-line `[scan]` Note. Never duplicate.

**B. Refresh the header (readable, humans first).** For notion-board, rewrite the Briefing page header, in order: `🕐 Last updated <today, time>` (the human timestamp *and* the machine watermark Intake reads), the **How to use this board** blurb (keep it, never drop it), and a **Today** summary (focus lead + ~3 plain sentences of what moved / what's hot / where the pressure is), then `☐ Reviewed by <owner>`. A tracker adapter has no header; it updates issue states instead.

**C. Apply the profile's Rules (write-backs).** Run any user-authored Rules whose trigger fired this sweep (e.g. logging a linked Activity row, setting a stream tag). Mechanical, authorized write-backs run with a `[scan]` trail; outward-facing actions still draft-and-confirm. See `## Rules`.

**D. End-of-day recap (optional, on the review pass).** Once the board is reviewed (box ticked, conflicts resolved), offer to post the **Today** summary + the day's closes + top open items to the team's chat channel. **Draft it and confirm before sending — never auto-post.** The board is the working surface; the recap is the digest.

**E. Sign-off (every run).** After everything else in the chat response — after the report, the suggested actions, and any adapter summary — close with the **sign-off line from the active profile**, if it defines one, rendered as markdown so links are clickable. This is per-user config, not engine content: one team's profile credits its maker, another's omits it or signs off differently.

---

## Principles
- **Intake and Output vary per user; Assess is the fixed engine.** That invariance is why it's portable, and why the reconcile logic never bends to the source or destination.
- **Everything becomes a task; nothing is dropped.** Action item with a next step → active row. Standing context with no next step → a `📌 Context:` documentation row (recording it *is* the deliverable). No fake Todos, no lost intelligence.
- **Summarize to PM altitude by default; granularity is a per-source setting.** This is a PM review surface, not a log. By default each source contributes rolled-up, decision-grade signal (a repo becomes "review backlog building on payments," not 40 PR rows; support becomes "spike on onboarding," not every ticket). But a profile can set a source's `detail: granular` when the user genuinely wants item-level rows from it (e.g. GitHub PRs, Zendesk tickets). Default is `signal`; opt into `granular` deliberately, per source.
- **Compare before write; propose before decide.** Surface deltas and calibrate; humans set direction.
- **Show what's done before what's new.** The report leads with completions and movement, not just fresh work.
- **Never clobber a human edit.** Pinned, Link-less, and Noted rows are sacred. When unsure whether a value is human, treat it as human and hold it.
- **Never scan private messages.** DMs, group DMs, and private channels are never read, in any service, for any user — only the channels the profile explicitly maps.
- **It's a team surface.** Parse and attribute everyone's input. Teammate notes are first-class.
- **Incremental, not full** — work off the watermark unless `full`.
- **Graceful degradation** — skip a disconnected source and say so. Same output shape regardless of how many sources fed in.

## Rules — per-profile, user-authored
Beyond sources and taxonomy, each profile can carry **Rules**: plain-language instructions the user writes to tell the engine what to *do* in their workflow, so the skill is instructable, not fixed. A rule is **trigger → action**, e.g. *"When chat shows a sales touchpoint, create a linked Activity row (Company + Deal + Contact) and point the board row's `Link` at it."* The engine reads the active profile's Rules and applies each whose trigger fired: **categorization/routing rules during Assess, write-backs during Output.**
- **Per-user** — everyone authors their own (during Discovery or later); nothing here is hardcoded to one org.
- **Safety rails still hold** — a rule never overrides *never-clobber-a-human*. Mechanical data-plumbing the user explicitly authorizes (logging an Activity, setting a link, tagging a stream) may run with a `[scan]` trail; anything outward-facing (sending a message, emailing) still drafts-and-confirms even if a rule says otherwise.

## Discovery — `/pm-sweep setup`
The **onboarding** phase, and the real front of the whole system: a person installs the skill, runs it, and it **connects to all their PM MCPs and picks up their people, surfaces, and categories** on its own, then they curate and it scaffolds. Run once; re-run whenever the stack changes. Produces a `profiles/<name>.md` so the skill works for anyone. **Discover and propose *for* the user; the taxonomy decisions stay theirs** (seed, don't dictate).
1. **Discover.** List the MCPs connected in this client (`claude mcp list` in Claude Code, or the client's MCP panel). Skip what's down or needs auth.
2. **Map tools to roles, confirm.** Linear/Jira/GitHub → *task*; Slack/Teams/Discord → *chat*; Notion/HubSpot/Salesforce → *CRM*; a Notion page / Google Doc / text file → *notes/freeform*; a *conversations log* if kept. Show the mapping; the user corrects. Establish the basics up front: is this one person or a team, and — before anything is built — does a shared board/surface already exist to **adopt**, or build new?
3. **Pin the specifics.** Which chat channels are signal, which task teams/projects, which CRM data sources. **Some sources are curated, not auto-discovered:** for code repos (GitHub/GitLab) the user **manually lists the specific repos to include**, never assume everything they can access (they may have a hundred and want three), and there's often no MCP, so ask; each repo is its own surface with its own `detail` (signal or granular). Same for anything where scope varies by access, team size, or plan caps. (Optional: Calendar → capacity input.)
4. **Design the board taxonomy (proposed, human-owned).** Where the person decides their surfaces and people; the skill seeds each from their own data so it's a guided interview, not a blank page:
   - **Owners (people)** — pull member lists from chat/task tools (Slack users, task assignees); propose the team, the user trims to who's in scope.
   - **Streams (their surfaces/categories)** — propose a starter set inferred from *their* signal (channel names, task labels/projects, deal types); the user renames / adds / drops. Seeded, not imposed.
   - **Horizons** — default `Today / This week / Next week / Next month / Someday`, editable.
5. **Choose the output.** If the team already has a board/surface (step 2), **adopt it** — record its IDs, leave its structure and views alone. Otherwise: a **document surface** (`notion-board`, `markdown-file`, a note app) or a **tracker** (`linear`, `jira`, items sync as native issues). Or a **custom `.md` adapter** (see `outputs/notion-board.md` for the Target · Persist · Render contract).
6. **Scaffold to match the taxonomy.** For a document output, build the destination with those Streams/Owners/Horizons as fields plus the standard views (by horizon / by person / by stream). For a tracker, map Streams → labels and Owners → assignees.
7. **Save.** Write it all to `profiles/<name>.md`. **Name the file for the org or workspace** — lowercase-hyphenated (`concept-to-cloud.md`, `acme.md`) — not the person: the profile is the team's surface config, and the person lives in its `runner` field. Confirm the proposed name with the user before writing, set `runner:` to whoever ran setup, and offer an optional `signoff` line. Then tell the user whether `/pm-sweep` picks it up automatically (one real profile) or needs `/pm-sweep <name>` (several exist).
8. **Rules (optional).** Offer to capture any custom `trigger → action` **Rules** (see `## Rules`) into the profile, e.g. write-backs to a CRM Activity log. Everyone authors their own.

## Portability — why it generalizes
Sources are defined by **role**, not vendor (Intake), and output is a swappable **adapter** (Output), so the **Assess** core — reconcile → calibrate → propose — is *identical* whether one source feeds it or six, and whether it renders to a Notion board or a Markdown file or syncs native issues into Linear/Jira. Pull from every mapped source that exists; skip the rest with a note. One engine, per-user Intake and Output on top.

**Coordination lives in the engine, never in the platform.** Dedupe on the **source reference** (the Link, identical for everyone, so a duplicate is provable), **per-surface watermarks** (not one global "last updated"), and **read-before-write against the shared output** are all engine logic, expressed through the adapter's **State** primitives (list current items + their refs, read/write per-surface watermarks). That is what lets many people, each in different channels, append to one shared output without duplicating or clobbering, and it works the same whether the output is a Notion board, a Markdown file, or a Linear project. No scan ever talks to another scan; they all talk to the output.
