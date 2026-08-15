---
name: qa
description: "Close Superflow work with acceptance, tests, proof, and status updates. Use when the user asks for QA, verification, done criteria, proof, readiness before completion, or final validation of a Superflow package."
---

# QA

QA proves the PRD acceptance criteria. A green command that misses the criterion
is not proof.

## Procedure

1. Read `../../assets/references/execution-contract.md`.
2. Read `../../assets/references/tdd-contract.md` (I3 — acceptance + RED/GREEN
   evidence).
3. Read `../../assets/references/status-schema.md`.
4. Compare implementation or artifact output against `PRD.md`.
5. If present, read `implementation_plan.json` and `implementation_log.json` to
   verify every planned task has evidence and every `tdd.required` task has
   red+green entries with command and excerpt.
6. Read `review_log.json`. QA does not close over an unanswered review: every
   finding needs a verdict, and accepted blockers/majors need proof. When code
   shipped and no `kind: "code"` round exists, route to `review` first
   (`../../assets/references/review-contract.md`).
7. Build the acceptance matrix: each PRD criterion → task id → command/artifact
   → status. Prefer the table shape in
   `../../assets/templates/qa_report.md`.
8. Run repo-native checks proportional to risk (targeted tests first; type,
   lint, UI/proof only when the change needs them).
9. Write `qa_report.md` when the work is non-trivial.
10. Update `status.json`: `phases.qa = "complete"` only after evidence exists,
   and `artifacts.qa = "qa_report.md"` when local.
11. When a task board exists, close its remaining stations in `board-data.js`
    so the board ends honest: every station `done` or explicitly
    `blocked` with a note. A board left mid-race after QA is a defect.

## Evidence

- Docs-only: render/link/lint proof where relevant.
- Code: targeted tests plus static checks; RED/GREEN log for required TDD tasks.
- UI: browser/screenshot proof when visual behavior matters.
- Data/security: migration/auth/permission validation.

## Ready Gate (I3)

QA is not complete if:

- a PRD acceptance criterion has no evidence row;
- a completed `tdd.required` task lacks red or green evidence;
- the only "proof" is prose or an unmapped green suite;
- code shipped without a `kind: "code"` review round, or a finding is still
  `pending`;
- the task board is left mid-race when one exists.

## Mermaid

Use Mermaid `requirementDiagram` or a small flowchart only when it clarifies
traceability. Mermaid only.
