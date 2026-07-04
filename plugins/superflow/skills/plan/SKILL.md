---
name: plan
description: "Write an implementation plan from a Superflow PRD and optional technical blueprint. Use when route is prd_plan_execute or build_plan_execute, when sequencing matters, or when execution should be split into concrete verifiable tasks."
---

# Plan

Plan converts the source of truth into ordered executable work. It should be
smaller than the PRD and more executable than the blueprint. Build decides the
architecture; Plan creates the task catalog.

## Procedure

1. Read `../../assets/references/execution-contract.md`.
2. Read `../../assets/references/status-schema.md`.
3. Read local `PRD.md` first. Then read `technical_blueprint.md`,
   `analysis.md`, `discovery.json`, or repo-native equivalents when present.
4. Read `../../assets/templates/implementation_plan.json` before writing a
   local plan.
5. Write `implementation_plan.json` as the executable task source. Optionally
   write `implementation_plan.md` only as a human-readable summary.
6. Update `status.json`: `phases.plan = "complete"`,
   `artifacts.plan = "implementation_plan.json"`, and
   `task_source.path = "implementation_plan.json"`.

## Required Plan

- Preconditions.
- Ordered tasks.
- File targets.
- Change per task.
- Validation per task.
- Done criteria mapped back to PRD acceptance criteria.
- Owner classification per task: `main_agent`, `explorer`, `worker`, or
  `reviewer`.
- `status: "pending"` for every task at plan creation. Execution progress goes
  to `implementation_log.json`, not into the plan.

## Task Ownership

If implementer agents are used, each one owns one complete plan task or an
explicitly re-planned complete subtask. Do not split one written task into
hidden technical slices across workers. Valid reports are `DONE`,
`DONE_WITH_CONCERNS`, `BLOCKED`, or `NEEDS_CONTEXT`.

## Ready Gate

Plan is not complete if:

- a PRD acceptance criterion has no mapped task or verification;
- a task has no file target, creation target, or explicit discovery target;
- verification is vague or non-runnable when a runnable check exists;
- architecture choices are still unresolved and should return to Build;
- task boundaries would cause overlapping write ownership.

## Mermaid

Use Mermaid for dependency order or execution flow when text would hide
sequencing. Follow `../../assets/references/mermaid-contract.md`.
