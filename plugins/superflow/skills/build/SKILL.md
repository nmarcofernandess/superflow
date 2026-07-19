---
name: build
description: "Create the Superflow technical blueprint/spec for architecture, schema, migration, API, auth, shared primitive, cross-module, or high-risk implementation work. Use when route is build_plan_execute, when analyst output is ready for architecture, or when a mature PRD still needs file-level contracts before plan/execution."
---

# Build

Build turns a mature PRD or `analysis.md` into an implementation-safe technical
blueprint. It is not a generic brainstorm and it does not replace execution.
It is also not Plan: Build closes architecture, contracts, boundaries, risks,
and validation strategy. Plan later turns those decisions into executable tasks.

## Required Reading

Read these completely before producing or updating a blueprint:

1. `../../assets/references/execution-contract.md`
2. `../../assets/references/status-schema.md`
3. `../../assets/references/build-protocol.md`
4. `../../assets/references/code-recon-protocol.md`
5. `../../assets/references/technical-blueprint-protocol.md`
6. `../../assets/references/mermaid-contract.md`

## Procedure

1. Confirm the input is mature: GitHub PRD, one or more analyses
   (`analysis.md`, `ANALYSIS-*.md`), `PRD.md`, or an explicit blueprint/spec
   request.
2. If product promise, entities, state, or evidence are weak, route back to
   `analyst`. Do not build on mush.
3. Read ALL analyses present in the package. The Build output is the single
   canonical synthesis and must list the sources it consumed; the status does
   not reconcile individual analyses — the spec does.
4. Inspect real repository files before choosing boundaries.
5. Close the design in Product -> Backend -> Frontend order.
6. Write `technical_blueprint.md` or the repo-native equivalent.
7. Include architecture/data flow diagrams when they clarify execution.
8. Run a grill pass before declaring the blueprint ready.
9. Update `status.json`: `phases.build = "complete"` and
   `artifacts.blueprint = "technical_blueprint.md"`.
10. Leave granular task ownership to Plan. Do not duplicate the final task
    tracker inside the blueprint.

## Required Blueprint

- Goal and product promise.
- Current terrain with evidence.
- Files and ownership boundaries.
- Reuse decisions vs new code.
- Data/API/contracts.
- Migration/security/cache/permission risks.
- Implementation sequence.
- Verification plan.
- Rollback/containment.
- Go/no-go verdict.

## Ready Gate

Build is not ready if:

- technical claims lack source proof;
- local patterns were not checked;
- sequence is not dependency-ordered;
- validation is vague;
- human decision can still change architecture;
- the implementation is too large for one slice and has not been split.
- the blueprint contains task status/progress instead of architecture decisions.

## Mermaid

Use Mermaid for architecture flow, runtime sequence, entity relationship, or
dependency graph. Never use legacy diagram syntax.
