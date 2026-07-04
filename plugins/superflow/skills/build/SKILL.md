---
name: build
description: "Create the Superflow technical blueprint/spec for architecture, schema, migration, API, auth, shared primitive, cross-module, or high-risk implementation work. Use when route is build_plan_execute or when a PRD is mature but the technical boundary is not."
---

# Build

Build turns a mature PRD into an implementation-safe technical blueprint. It is
not a generic brainstorm and it does not replace execution.

## Procedure

1. Read `../../assets/references/execution-contract.md`.
2. Read `../../assets/references/status-schema.md`.
3. Read `../../assets/references/mermaid-contract.md`.
4. Inspect real repository files before choosing boundaries.
5. Write `technical_blueprint.md` or the repo-native equivalent.
6. Update `status.json`: `phases.build = "complete"` and
   `artifacts.blueprint = "technical_blueprint.md"`.

## Required Blueprint

- Existing system read.
- Files and ownership boundaries.
- Reuse decisions vs new code.
- Data/API/contracts.
- Migration/security/cache risks.
- Implementation sequence.
- Verification plan.
- Go/no-go verdict.

## Mermaid

Use Mermaid for architecture flow, runtime sequence, entity relationship, or
dependency graph. Never use legacy diagram syntax.
