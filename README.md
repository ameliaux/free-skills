# free-skills

Free, practical skills for Claude Code, from [Concept to Cloud](https://concepttocloud.com).

These are the real tools we use to run a product studio, stripped of our private config and shared so you can drop them into your own Claude Code setup. Each skill is generic: your personal details (calendars, trackers, IDs) live in a small config you fill in, never in the skill itself.

## Skills

- **week-planner**: Reclaim-style time-blocking. Reads work from any connected issue tracker (Linear, Jira, Asana, Monday) and lays free, moveable focus blocks onto your calendar, around your meetings, front-loaded and urgent-first. Composable modes (`week`, `quarter`, `sprint`, `loose`, `light`, `private`, `busy`), and it self-cleans finished work on every run.
- **pm-sweep**: a shared daily briefing. Sweeps your connected PM tools (CRM, chat, tracker, notes), reconciles what changed since the last look, and writes it to the surface your team already uses (a Notion board, a Markdown file, or native issues). Source-agnostic, and it never clobbers a human edit.
- **portfolio-audit**: a cross-codebase review. Audits every project in a directory through four specialist lenses in parallel (developer, product design, marketing, business and ops) and compiles an interactive HTML triage report of what needs doing.

## Install

Copy a skill folder into your Claude Code skills directory:

```
cp -r skills/week-planner ~/.claude/skills/
```

Then fill in the skill's example config with your own details, and invoke it (for example, `/week-planner`). pm-sweep has a first-run setup (`/pm-sweep setup`) that writes your profile for you.

## License

MIT. Use them, fork them, ship your own.
