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
   `implementation_plan.md` if present.
4. Update `status.json`: `phases.execute = "running"` before code and
   `complete` only after implementation is done.
5. Record human context in `progress.md`; update `WARLOG.md` for deep,
   forensic, plugin, workflow, or multi-session work.
6. Run QA according to the risk before declaring done.

## Mermaid

Execution itself does not need diagrams by default. If documenting a runtime
flow or dependency, use Mermaid only.
