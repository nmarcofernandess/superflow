# WARLOG Contract

WARLOG is the **campaign board** for long-running work: multi-session, multi-sprint,
plugin, architecture, forensic, or epic. It is not a task tracker and not a diary
of microsteps.

DNA from Warlog Minimal (mission, WBS, dependencies, sprints, chronology, next
action) lives here. Visuals are **Mermaid only**. PlantUML is forbidden.

## When to create

Create or update `WARLOG.md` when:

- `phase_budget` is `deep` or `forensic`, or work spans multiple sessions;
- decisions must survive branch/issue/session changes;
- the user asks for warlog, campaign board, sprint map, or live next action.

Do **not** create WARLOG for lean one-shot work. Use `progress.md` and the
package validator.

## Ownership (do not blur)

| Artifact | Answers | Does not answer |
|----------|---------|-----------------|
| **WARLOG** | How sprints chain? What is blocked? Budget? Green contract? Next fatia? | Execute step 3; RED command |
| **status.json** | Where are we now? Active phase? Artifact pointers? | Campaign history |
| **SPEC / Plan** | Technical contracts and ordered tasks of the **active** sprint | Whole campaign |
| **implementation_log** | RED/GREEN evidence per code task | Sprint graph |

WARLOG may list sprint artifacts. It does not replace `implementation_plan.json`,
`implementation_log.json`, or Analyst/Build Ready gates
(`validate_superflow.py` on the package).

## Sprint = mergeable slice

A sprint is a mergeable fatia of the campaign (often one PR), not a calendar Scrum
sprint. Detail for a future sprint is born late (rolling wave).

Each sprint card:

```markdown
### S2 — Human-verifiable result title

- State: blocked | ready | active | qa | done
- Depends on: S1, decision X (or —)
- Budget: direct | plan | spec
- Route: Analyst? → Build? → Plan? → Execute → QA (only phases needed)
- Human gate: decision that changes the solution, or none
- Green contract: tests, visual proof, performance, regressions (names, not fake commands)
- Harness: existing | extend here | own sprint
- Artifacts: analysis/SPEC/PLAN/QA that actually exist (or —)
- Next action: one concrete action
```

### Budget (per sprint)

| Budget | Use | Expected prep |
|--------|-----|----------------|
| `direct` | Mature source, obvious change, low risk | Execute + QA |
| `plan` | Clear product/tech, sequencing needed | Plan + Execute + QA |
| `spec` | Ambiguity, architecture, data, multi-analysis | Analyst as needed + Build/SPEC + Plan if needed + Execute + QA |

Budget is proposed in WARLOG; the human may override. It is not a keyword score.

## Required structure

1. **Mission** — one-sentence end state + success metric.
2. **Scope** — in / out.
3. **Campaign map** — Mermaid `flowchart` (WBS or dependency graph).
4. **Sprints** — one card per mergeable slice (at least S1 when creating).
5. **Decisions** — durable choices that constrain later sprints.
6. **Event Log** — dated chronology (session-scale, not microtask ticks).
7. **Risks And Blocks** — open risks and unblockers.
8. **Next Action** — single concrete next move (same truth as dashboard).

Optional Mermaid: `timeline`, `stateDiagram-v2`, `gantt` when dates help.
Do not dump every phase state machine if the campaign map already answers.

## Forbidden

- PlantUML / legacy diagram syntax.
- Microtask RFEs, step-by-step execute trails, or invented TDD commands in WARLOG
  (those belong to Plan / Execute / `tdd-contract.md`).
- Tracking task DONE/blocked per line as the primary UI (use Plan board + log).
- Two parallel warlog systems (no “call warlog-minimal”). One official skill.
- WARLOG that contradicts a ready PRD without reconciling first.

## Status pointer

When `WARLOG.md` exists: `status.json.artifacts.warlog = "WARLOG.md"`.

## Shell generator

`scripts/superflow_warlog.py` may create the shell and append events. The agent
(or human) fills Mission, Sprints, and Green contracts with real content.
Placeholders must be replaced before claiming campaign ready.
