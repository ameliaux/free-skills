---
name: portfolio-audit
description: Use when the user wants a comprehensive, portfolio-wide audit or review of every project/repo in a directory at once — a cross-codebase assessment of what needs doing (build, product/UX, marketing/GTM, business/ops), especially before planning, triaging, prioritizing, or filing tasks across many projects. Triggers include "audit all my projects", "review every repo", "what needs doing across everything".
---

# Portfolio Audit

## Overview
Audit every project in a directory through **4 specialist lenses in parallel** — Developer, Product Designer, Marketing/GTM, Business/Ops — one agent per (repo × lens), then compile the findings into an **interactive HTML triage report**. Specialist-per-lens gives sharp, comparable assessments instead of mushy generalist ones.

## When to use
- "audit all my projects" · "review every repo" · "what needs doing across everything"
- Portfolio-wide planning / triage / prioritization before filing tasks into a tracker
- Many repos where you need one comparable map (build + product + marketing + business)

**Not** for a single project — just analyze that one directly.

## Steps
1. **Enumerate real repos** in the target dir (default `~/Projects`). Count a folder as a project if it has `.git`, `package.json`, or `README.md`; exclude asset/content-only dirs. Show the list and get a go-ahead — this is a real token spend (~4 agents × N repos).
2. **Run the grid workflow** — invoke `Workflow` with `scriptPath` = this skill's `scripts/portfolio-audit-grid.js`, passing `args: { dir: "<target dir>", projects: ["name1","name2",...] }`. It returns `[{project, lenses:[{lens, assessment, todos:[{title,type,priority,desc,deps}]}]}]`.
3. **Synthesize (required)** — dispatch ONE `Agent` that reads the grid output file and writes a structured **portfolio-level synthesis** JSON. It MUST produce all of:
   - **Per-project scores on EVERY dimension** (do not pick one weighting — score them all, 1–5): `revenue` (real demand + path to money), `differentiation` (uniqueness / did-it-first), `effort` (ease-to-ship; **higher = easier/closer to done**), `fit` (strategic fit + conviction). Plus `readiness` (near-launch / mvp / early / dormant).
   - **A default `verdict`** (keep / prioritize / park / kill) synthesized from the scores — **decisive**.
   - **Cross-cutting `themes`** — patterns only visible across the whole set (systemic gaps, redundancy, concentration/risk). NOT per-project restatement.
   - **`topPriorities`** — the few highest-leverage first moves portfolio-wide.
   - A one-line directional `note` per project.
   Schema: `{themes:[...], topPriorities:[...], projects:[{project, verdict, readiness, revenue, differentiation, effort, fit, note}]}`.
   **Decisiveness bar:** a synthesis that hedges everything to "keep" is a FAILURE — it must make real calls including kills. It **frames, never replaces** — every granular to-do remains. Flag any lens whose content is a "test"/placeholder so the reader knows what's judged on partial data.
   The HTML must let the user **sort/filter by any dimension** — so "what do I work on today" or "how to distribute a team" is a live re-slice, not a fixed ranking.
4. **Build the HTML** — `python3 <skill>/scripts/gen_audit.py <workflow-output-file> <out.html> [<synthesis-json>]`. The HTML shows the **synthesis up top AND every granular to-do below** — the user must be able to see it all synthesized *and* fully granular, with checkboxes on every item. The workflow's `output-file` path comes from its task-notification; the result array lives under the `result` key.
5. **Deliver** the HTML to the user (SendUserFile). It persists check-offs in localStorage and has an "Export selected" button.

## Out of scope — do NOT do these as part of the skill
- **Do NOT load anything into Linear or any other tracker.** That is a separate, explicitly user-initiated step — only do it when the user says so, never automatically.
- Do not drop or collapse granular items in favor of the synthesis. Both always ship.

## Notes
- **Don't read the full result into context** — it's often 300k–400k chars. Parse it with the script; let the synthesis Agent read it in its own context.
- If a lens fails (StructuredOutput retry cap on a huge repo), **resume** the workflow: `Workflow({scriptPath, resumeFromRunId})` — completed passes replay from cache instantly; only the failed cells re-run. Repeat once or twice; a persistently-failing cell can be filled with a single direct `Agent` call.
- The 4 lenses, their prompts, and the output schema live in `scripts/portfolio-audit-grid.js` — edit there to add/change lenses.
