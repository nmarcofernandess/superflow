---
name: qa
description: "Close Superflow work with acceptance, tests, proof, and status updates. Use when the user asks for QA, verification, done criteria, proof, readiness before completion, or final validation of a Superflow package."
---

# QA

QA proves the PRD acceptance criteria. A green command that misses the criterion
is not proof.

## Procedure

1. Read `../../assets/references/execution-contract.md`.
2. Read `../../assets/references/status-schema.md`.
3. Compare implementation or artifact output against `PRD.md`.
4. If present, read `implementation_plan.json` and `implementation_log.json` to
   verify every planned task has evidence.
5. Run repo-native checks that cover the actual risk.
6. Write `qa_report.md` when the work is non-trivial.
7. Update `status.json`: `phases.qa = "complete"` only after evidence exists,
   and `artifacts.qa = "qa_report.md"` when local.
8. When a task board exists, close its remaining stations in `board-data.js`
   so the board ends honest: every station `done` or explicitly
   `blocked` with a note. A board left mid-race after QA is a defect.

## Evidence

- Docs-only: render/link/lint proof where relevant.
- Code: targeted tests and static checks.
- UI: browser/screenshot proof when visual behavior matters.
- Data/security: migration/auth/permission validation.

## Mermaid

Use Mermaid `requirementDiagram` or a small flowchart only when it clarifies
traceability. Mermaid only.
