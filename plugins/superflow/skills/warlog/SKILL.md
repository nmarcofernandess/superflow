---
name: warlog
description: "Create or update a Superflow WARLOG campaign board for multi-session, multi-sprint, plugin, architecture, forensic, or epic work. Use when the user asks for warlog, sprint map, WBS, dependencies, live next action, decision log, or durable progress across sessions."
---

# WARLOG

WARLOG is the **campaign board**. It keeps the next session from reconstructing
why the work exists, how sprints chain, and what to do next.

It absorbs the Product Owner job of Warlog Minimal (mission, WBS, dependencies,
sprints, chronology) under Superflow rules: Mermaid only, no microtask RFEs,
no parallel skill.

## Required Reading

1. `../../assets/references/warlog-contract.md`
2. `../../assets/references/status-schema.md`
3. `../../assets/references/mermaid-contract.md`
4. `../../assets/templates/WARLOG.md`
5. For code sprints: `../../assets/references/tdd-contract.md` (green contracts
   name behaviors; Plan owns RED/GREEN commands)

## When

- deep / forensic / multi-session / multi-sprint / plugin / architecture / epic
- user asks warlog, campaign board, sprint map, next action

Skip for lean one-shot packages (`progress.md` is enough).

## Procedure

1. Read the contract and existing `WARLOG.md` if any.
2. Prefer `../../scripts/superflow_warlog.py` to create the shell or append an event.
3. Fill **Mission**, **Scope**, **Campaign map** (Mermaid flowchart of sprints).
4. Write **Sprint cards** (mergeable slices). Rolling wave: detail the active
   and next sprint; leave later sprints thin until unlocked.
5. For each sprint set Budget (`direct` | `plan` | `spec`), Route, Human gate,
   Green contract, Artifacts, Next action.
6. Log durable **Decisions** and session-scale **Event Log** entries (not every
   microtask flip).
7. Keep **Next Action** to one concrete move.
8. Set `status.json.artifacts.warlog = "WARLOG.md"`.
9. Do not invent Plan tasks or TDD commands here. Point at SPEC/Plan when the
   active sprint needs them.

## Command

```bash
python3 <plugin-root>/scripts/superflow_warlog.py \
  specs/001-slug \
  --event "S1 active; Plan complete; execution can start."
```

## Required content

- Mission + Scope
- Campaign map (Mermaid)
- At least one Sprint card (`### S1 — …` with State/Budget/Green/Next action)
- Decisions, Event Log, Risks And Blocks, Next Action

## Ready Gate (campaign)

WARLOG is not “ready” if:

- only a diary of events with no sprints;
- sprints have no budget or green contract;
- Next Action is empty or multi-page waffle;
- PlantUML or microtask RFEs appear;
- it claims Execute progress that belongs in `implementation_log.json`.

Package-level Analyst/Build Ready still requires:

```bash
python3 <plugin-root>/scripts/validate_superflow.py <path-to-package>
```

## Mermaid

Snapshots: `flowchart` for WBS/deps, optional `timeline` / `stateDiagram-v2`.
Never PlantUML. Follow `../../assets/references/mermaid-contract.md`.
