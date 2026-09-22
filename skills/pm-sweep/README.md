# pm-sweep

One command that turns your scattered work tools into one shared daily briefing.

It sweeps every connected surface — Slack, Linear/Jira, the Notion CRM, Gmail, meeting notes, Calendar — for what changed since the last sweep, reconciles what it found against a single shared board, reports what got done and what's new, and proposes what needs attention. You keep the judgment; it does the mechanical prep.

---

## Quickstart (first 5 minutes)

1. **Install the skill.** Drop the `pm-sweep/` folder into your skills directory (or share the folder with a teammate — they install their own copy).
2. **Run `/pm-sweep setup`.** It checks which tools you have connected, proposes how to map them, and asks a few plain questions:
   - *Does your team already have a shared board or tracking surface, or build one new?*
   - *Where should the briefing live?* (a Notion board, a Markdown file, or native issues in Linear/Jira)
   - *Which chat channels are signal?* (it proposes from your own channels; you trim)
   - *Who are the people in scope?*
3. **Run `/pm-sweep`.** That's the daily briefing. Nothing else to remember.

Re-run `setup` whenever your stack changes — new tool, new team, new channels.

## Daily use

- `/pm-sweep` — the daily incremental briefing. Run it in the morning (or just ask: *"the briefing"*, *"what's happening"*, *"what needs doing"*).
- `/pm-sweep full` — ignore the "last swept" bookmark and rebuild the whole picture. Use after a break or a long weekend.
- `/pm-sweep status` — "what am I wired to?" No sweep, just the readout.
- `/pm-sweep curate` — for teams: one person refreshes the shared summary at the top of the board without running a full sweep.
- `/pm-sweep <profile>` — run against a named profile if you keep several.

**What you'll see each run:**
- A one-line tally: done/moved · new · waiting · updates · conflicts.
- **What got finished first**, then what's new — completions lead, not fresh work.
- Ranked **suggested actions** — offered, never executed. You pick; it never auto-creates issues or sends messages.
- The shared board updated with only the safe changes, and a plain-English "Today" summary at the top.

You can also edit the board directly — tick things done, drop notes, set horizons. The next sweep reads your edits and protects them.

## How it works (three phases)

**Intake** — check which sources are live, then pull what changed since the last sweep. Sources that are down get skipped with a note, not a failure.

**Assess** — reconcile every found item against the board (new / matches / updates / conflicts / done), calibrate horizons against due dates and capacity, and report the comparison *in chat before writing anything*.

**Output** — apply only the safe writes, refresh the header, done. Every run signs off so you know it completed.

Sources and destination are configured per person; the reconcile engine is identical for everyone.

## On a team

Everyone installs their own copy and connects their own tools, and every run feeds **the same shared board**:

- Runs don't collide: each surface remembers its own "last swept" time, so two people can sweep the same channels without double-reporting.
- Every row the skill writes is tagged `[scan:yourname]`, so appends are attributable and one person's writes are never mistaken for yours.
- Deduping is provable: rows match on a source link, not a guess at a title.
- Teammate input is first-class — the sweep attributes items to whoever raised them.

## Safety rails

- **Never scans private messages or DMs. In any messaging service. At all.** The sweep reads only the channels your profile explicitly maps.
- **Never clobbers a human edit.** A row you pinned, noted, or typed in by hand is sacred — conflicts are held and listed, not overwritten. The skill's own notes are prefixed `[scan]` so they're never mistaken for a human's.
- **Proposes before it decides.** The comparison is reported in chat before any write.
- **Outward-facing actions are drafted, never sent.** A Slack recap or email waits for your explicit yes.

## Telling it your workflow (Rules)

Each profile can carry plain-language **Rules** — `trigger → action` — so the skill adapts to your workflow instead of the reverse. Example: *"When a partner touchpoint shows up in chat, log a linked Activity row in the CRM and point the board row's Link at it."* Rules can't override the safety rails.

## Where it points

The destination ("adapter") comes in two families:

- **Document surfaces** — Notion, Google Docs, a Markdown file. The briefing is a living document/board, kept current in place.
- **Trackers** — Linear, Jira, Asana. Items become native issues, synced through that tool's workflow.

Or write your own adapter: copy `outputs/notion-board.md`, fill in *Target · Persist · Render*, and point your profile at it.

## Files

```
pm-sweep/
├── SKILL.md            the engine — same for every user, don't edit per person
├── README.md           this file
├── profiles/<name>.md  per-user config: sources → roles, streams, owners, output choice
└── outputs/<name>.md   output adapters
```

## Sharing it

Hand someone the folder. They run `/pm-sweep setup` against their own tools and either join your shared board (point their profile at it) or scaffold their own. On **Claude**, Slack connects natively through account sign-in; on other MCP clients you may need a Slack MCP server configured first — setup will tell you if it's missing.

---

pm-sweep is built and shared free by Concept to Cloud. If it's saving you time, we'd love to hear how — feedback goes straight to the people building it → https://concepttocloud.com/free-tools/pm-sweep-feedback
