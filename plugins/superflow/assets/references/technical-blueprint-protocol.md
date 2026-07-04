# Technical Blueprint Protocol

Use after PRD/recon when a task needs a concrete implementation path.

## Mission

Bridge product intent and codebase reality into an implementation-safe
blueprint. Blueprint is the architect lane: file boundaries, contracts, trade
offs, sequencing, validation, and rollback.

Blueprint is the Build artifact. It may include implementation sequence, but it
does not own task status or worker ownership. Plan owns the executable subtask
catalog.

## Rules

- Ground the blueprint in real files, docs, commands, tests, and constraints.
- Reuse local patterns before inventing abstractions.
- Separate Product, Backend, Frontend, Validation, and Operations contracts.
- Name likely files/modules, but do not edit them from this protocol alone.
- Sequence steps topologically: dependencies first.
- Keep validation proportional to risk.

## Output Shape

```markdown
## Goal
Concrete outcome.

## Current Terrain
Facts from recon and source files.

## Recommended Path
Chosen approach and why it fits the existing system.

## Files / Areas
| Path/Area | Action | Reason | Risk |
|---|---|---|---|

## Contracts
### Product
Promise, user-visible behavior, non-goals.

### Backend
Data shapes, API/action contracts, permissions, state, migrations.

### Frontend
Components, shells, loading/error/empty states, responsiveness, accessibility.

### Validation
Tests, manual checks, CI, route proof, performance/edge cases.

## Sequence
Ordered implementation steps.

These are dependency steps, not the final task tracker. Convert them into
`implementation_plan.json` during Plan.

## Rollback / Containment
How to keep the blast radius bounded.

## Risks
Trade-offs and failure modes.
```

## Blueprint Quality Bar

- Every named file/area has a reason.
- Every critical contract has a validation path.
- Legacy compatibility is isolated.
- Missing decisions are not hidden; they become open questions or blockers.
- If the blueprint cannot choose between two approaches, it explains the
  decision Marco must make.
