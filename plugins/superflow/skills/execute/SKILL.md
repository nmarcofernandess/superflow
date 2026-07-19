---
name: execute
description: "Execute implementation from a mature Superflow PRD, plan, or technical blueprint while keeping status and progress current. Use when the user asks to implement, resume execution, or continue a Superflow local package."
---

# Execute

Execution starts from a durable artifact, not from vibes. If the PRD is low
confidence or the route says investigate/build/plan first, do that before code.

## Procedure

1. Read `../../assets/references/execution-contract.md`.
2. Read `../../assets/references/status-schema.md`.
3. Read the local `PRD.md`, then `technical_blueprint.md` and
   `implementation_plan.json` if present. If only `implementation_plan.md`
   exists, treat it as human context and prefer creating/asking for JSON before
   multi-task execution.
4. Update `status.json`: `phases.execute = "running"` before code and
   `complete` only after implementation is done.
5. When a plan exists, implement the next pending task as a whole unit. Record
   files, checks, self-critique, and remaining tasks in `implementation_log.json`.
6. Record human context in `progress.md`; update `WARLOG.md` for deep,
   forensic, plugin, workflow, or multi-session work.
7. Run QA according to the risk before declaring done.

## Status Discipline

- Mark `phases.execute = "running"` before code changes.
- Keep `implementation_plan.json` as the task source. Do not rewrite it as a
  progress log.
- Update `implementation_log.json` after each task.
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
