---
name: warlog
description: "Create or update a Superflow WARLOG for long-running product, plugin, architecture, forensic, or multi-session work. Use when the user asks for warlog, live status, timeline, decision log, Mermaid status view, or durable progress across sessions."
---

# WARLOG

WARLOG is the durable story of a larger piece of work. It keeps the next session
from having to reconstruct why the work exists and what changed.

## Procedure

1. Read `../../assets/references/warlog-contract.md`.
2. Read `../../assets/references/status-schema.md`.
3. Use `../../scripts/superflow_warlog.py` for local packages when possible.
4. Keep narrative concise and evidence-oriented.
5. Update `status.json.artifacts.warlog = "WARLOG.md"`.

## Command

```bash
python3 <plugin-root>/scripts/superflow_warlog.py \
  specs/001-slug \
  --event "Plan complete; execution can start."
```

## Required WARLOG Content

- Context and objective.
- Mermaid state snapshot.
- Mermaid timeline or dependency graph when useful.
- Decisions.
- Event log.
- Risks, blocks, and next action.

## Mermaid

WARLOG is Mermaid-first for visual snapshots. Use
`../../assets/references/mermaid-contract.md` and never legacy diagram syntax.
