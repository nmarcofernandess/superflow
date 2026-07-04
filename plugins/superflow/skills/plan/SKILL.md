---
name: plan
description: "Write an implementation plan from a Superflow PRD and optional technical blueprint. Use when route is prd_plan_execute or build_plan_execute, when sequencing matters, or when execution should be split into concrete verifiable tasks."
---

# Plan

Plan converts the source of truth into ordered work. It should be smaller than
the PRD and more executable than the blueprint.

## Procedure

1. Read `../../assets/references/execution-contract.md`.
2. Read `../../assets/references/status-schema.md`.
3. Read `../../assets/templates/implementation_plan.md` before writing a local
   plan.
4. Write `implementation_plan.md` or the repo-native equivalent.
5. Update `status.json`: `phases.plan = "complete"` and
   `artifacts.plan = "implementation_plan.md"`.

## Required Plan

- Preconditions.
- Ordered tasks.
- File targets.
- Change per task.
- Validation per task.
- Done criteria mapped back to PRD acceptance criteria.

## Mermaid

Use Mermaid for dependency order or execution flow when text would hide
sequencing. Follow `../../assets/references/mermaid-contract.md`.
