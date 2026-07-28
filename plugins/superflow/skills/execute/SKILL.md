---
name: execute
description: "Execute implementation from a mature Superflow PRD, plan, or technical blueprint while keeping status and progress current. Use when the user asks to implement, resume execution, or continue a Superflow local package."
---

# Execute

Execution starts from a durable artifact, not from vibes. If the PRD is low
confidence or the route says investigate/build/plan first, do that before code.

## Procedure

1. Read `../../assets/references/execution-contract.md`.
2. Read `../../assets/references/tdd-contract.md` (I2 — iron law RED before
   production code).
3. Read `../../assets/references/status-schema.md`.
4. Read the local `PRD.md`, then `SPEC.md` (or legacy
   `technical_blueprint.md`) and `implementation_plan.json` if present. If
   only `implementation_plan.md` exists, treat it as human context and prefer
   creating/asking for JSON before multi-task execution.
5. Update `status.json`: `phases.execute = "running"` before code and
   `complete` only after implementation is done with evidence.
6. When a plan exists, implement the next pending task as a whole unit using
   the TDD cycle below. Record files, RED/GREEN evidence, self-critique, and
   remaining tasks in `implementation_log.json` (template:
   `../../assets/templates/implementation_log.json`).
7. Record human context in `progress.md`; update `WARLOG.md` for deep,
   forensic, plugin, workflow, or multi-session work.
8. Run QA according to the risk before declaring done.

## TDD cycle per task (I2)

For each task with `tdd.required: true` (default for code):

1. Write or adjust the planned test (`tdd.red.test_file` / `test_name`).
2. Run `tdd.red.command`. Confirm RED for the **expected** reason (feature
   missing or bug), not unrelated setup failure.
3. Only then write minimal production code.
4. Run `tdd.green.command`. Confirm GREEN.
5. Optional refactor while green.
6. Append log entry with `red` and `green` objects (`command`, `excerpt`,
   `ok`). Booleans alone are not evidence.

**Iron law:** production code before observed RED invalidates the task. Do not
keep the production edit as reference — replay RED→GREEN.

For lean direct execution without a plan file, still follow RED→GREEN and log
a synthetic task id such as `direct-1`.

Skipped TDD (`tdd.required: false`) requires a non-empty `skip_reason` and
must not touch unproven production behavior.

## Status Discipline

- Mark `phases.execute = "running"` before code changes.
- Keep `implementation_plan.json` as the task source. Do not rewrite it as a
  progress log.
- Update `implementation_log.json` after each task with RED/GREEN evidence.
- Task status `DONE` without red+green evidence (when TDD required) is
  invalid.
- When a task board exists (`board.html` + `board-data.js`), rewrite
  `board-data.js` in the SAME boundary as `status.json`: task finished,
  pitstop inserted (`state: "added"`), or blocked. Status changed without the
  board changed means the boundary is not finished. If no board exists yet and
  execution has three or more tasks, create one from
  `../../assets/task-board/board-data.example.js`.
- Mark `phases.execute = "complete"` only when all planned tasks are complete
  or direct execution is fully implemented with evidence.
- If blocked, set `phases.execute = "blocked"` and record the blocking reason.

## Mermaid

Execution itself does not need diagrams by default. If documenting a runtime
flow or dependency, use Mermaid only.
