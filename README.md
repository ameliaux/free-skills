# free-skills

Free, practical skills for Claude Code, from [Concept to Cloud](https://concepttocloud.com).

These are the real tools we use to run a product studio, stripped of our private config and shared so you can drop them into your own Claude Code setup. Each skill is generic: your personal details (calendars, trackers, IDs) live in a small config you fill in, never in the skill itself.

## Skills

- **week-planner** — Reclaim-style time-blocking. Reads a set of work from any connected issue tracker (Linear, Jira, Asana, Monday) and lays free, moveable focus blocks onto your calendar, around your meetings, front-loaded and urgent-first. Composable modes (`week`, `quarter`, `sprint`, `loose`, `light`, `private`, `busy`). Self-cleans finished work on every run.

_More coming: pm-sweep (a shared daily briefing across your PM tools), portfolio-audit._

## Install

Copy a skill folder into your Claude Code skills directory:

```
cp -r skills/week-planner ~/.claude/skills/
```

Then fill in the skill's `example-config` with your own details, and invoke it (for example, `/week-planner`).

## License

MIT. Use them, fork them, ship your own.
