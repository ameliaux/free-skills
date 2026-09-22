# pm-sweep profile — <YOUR ORG>

Copy this to `profiles/<name>.md` and fill it in, or run `/pm-sweep setup` and it writes this for you from your connected tools.

## Sources (role → connected MCP → specifics)
Each source may set `detail: signal` (default, rolled up to PM altitude) or `detail: granular` (item-level rows). Some sources auto-discover (chat channels, task teams); others you curate by hand (code repos).
- **CRM / pipeline** — <tool>: <data-source IDs or names>
- **Chat** — <Slack / Teams / Discord>: signal channels <#a, #b>
- **Task / issue** — <Linear / Jira / Asana>: teams/projects <...>
- **Code repos (manual)** — <GitHub / GitLab>: list the specific repos to include <org/repo-a, org/repo-b>. Each repo is its own surface; `detail: signal` by default. Do not auto-include everything you can access.
- **Support (optional)** — <Zendesk>: <views/queues>; `detail: signal`
- **Notes / freeform inbox** — <optional: a page or text file>
- **Conversations log** — <optional: real conversations/meetings/decisions only, NOT standing context>

## Output
- **adapter:** notion-board    # or markdown-file / linear / jira / asana / your own outputs/<name>.md
- **destination:** <Briefing page id, file path, or project — depends on the adapter>
- **board data source:** <id, for the notion-board adapter>
- Fields: Item, Stream, Owner, Horizon, Status, Due, Assigned, Link, Pinned, Note
- Status options: Todo · In Progress · Waiting (blocked on someone/something) · Done · Punted (deliberately set aside)

## Streams (your surfaces/categories)
<your categories — setup proposes a starter set from your channels, labels, and deal types; you curate>

## Owners
<your people — setup pulls these from your chat/task tools; you trim to who's in scope>

## Capacity inputs (optional)
- <e.g. Calendar, to subtract real meetings from available hours>

## Rules (write-backs / custom handling)
Plain-language `trigger → action` instructions the engine applies (routing in Assess, write-backs in Output). Author your own; safety rails still hold (never clobber a human; outward-facing actions still confirm).
- _(example)_ **When** <a trigger appears in a source>, **do** <create/update a record, set a link, tag a stream>.
