# Implementation Plan: {title}

> Human-readable summary only. The executable task source is
> `implementation_plan.json`. TDD rules live in
> `assets/references/tdd-contract.md` (plugin) — every code task must pre-compile
> RED and GREEN.

## Preconditions

- [ ] PRD reviewed (`prd_status: ready`)
- [ ] Route confirmed: {route}
- [ ] Phase budget confirmed: {phase_budget}
- [ ] TDD contract read for code tasks

## Tasks

- [ ] Task 1 — {behavior}
  - Files:
  - RED command:
  - Expected RED failure:
  - GREEN command:
  - Acceptance criteria:
  - Owner: main_agent

## Validation Commands

```bash
# Prefer the per-task tdd.red / tdd.green commands from the JSON plan
```

## Done Criteria

- [ ] All PRD acceptance criteria mapped and evidenced
- [ ] Each `tdd.required` task has red+green evidence in `implementation_log.json`
- [ ] `status.json` points at the current phase and final verdict
- [ ] QA evidence recorded
