# Execution Contract

Execution starts only after a route has a durable source of truth. For local
work, that source is `specs/NNN-slug/PRD.md`.

## Execute Directly

Allowed when all are true:

- `confidence = high`
- `route = prd_execute`
- Risk score is 0-1
- Acceptance criteria are testable
- No schema/security/cross-module ambiguity
- User asked to implement or the task is already in execution mode

Direct execution still requires QA.

## Plan First

Use plan when:

- There are multiple files or subtasks with dependencies.
- There is sequencing risk.
- More than one acceptance criterion needs separate validation.
- The change may be partially implemented across sessions.

Write `implementation_plan.md` or the repo-native equivalent.

## Build First

Use build/spec when:

- Data model or architecture changes are involved.
- Existing abstractions must be selected or extended.
- The PRD names behavior but not implementation boundaries.
- A wrong implementation would be expensive to unwind.

Write `technical_blueprint.md` or the repo-native equivalent.

## Investigate First

Use discovery before PRD/build/plan when:

- The request is a bug without proven cause.
- The user asks "why" or "verifica".
- Logs, tests, runtime behavior, or code paths must be inspected before
  defining the fix.

## Status Updates

For local packages, update `status.json` at phase boundaries:

```txt
pending -> running -> complete
pending -> running -> failed
pending -> blocked
pending -> skipped
```

Log human context in `progress.md`. Keep `status.json` terse.

For deep, forensic, plugin, workflow, migration, or multi-session work, also
maintain `WARLOG.md` with Mermaid snapshots according to
`warlog-contract.md`.

## QA

QA must match the change:

- Docs-only: lint/render/link checks where relevant.
- Code: targeted tests plus static checks.
- UI: screenshot/browser proof when behavior is visual.
- Data/security: explicit migration/auth/permission validation.

Do not declare done from a green check that does not cover the acceptance
criteria.
