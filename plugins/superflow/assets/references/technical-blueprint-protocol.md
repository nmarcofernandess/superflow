# Technical Blueprint Protocol

Use after PRD/recon when a task needs a concrete implementation path.

The Build artifact is `SPEC.md` by default. `technical_blueprint.md` is the
legacy filename and remains valid in existing specs (lazy migration).

## Mission

Bridge product intent and codebase reality into an implementation-safe
blueprint. Blueprint is the architect lane: file boundaries, contracts, trade
offs, sequencing, validation, and rollback.

Blueprint is the Build artifact. It may include implementation sequence, but it
does not own task status or worker ownership. Plan owns the executable subtask
catalog and TDD pre-compile (`tdd-contract.md`).

## Rules

- Ground the blueprint in real files, docs, commands, tests, and constraints.
- Reuse local patterns before inventing abstractions — **search first** (T4–T6).
- Separate **Product, Backend, Frontend, Copy, Validation, and Operations** as
  facets of one **Synthesis** (feature-mindset-contract.md). Not a freeze
  waterfall.
- Name likely files/modules, but do not edit them from this protocol alone.
- Sequence steps topologically: dependencies first.
- Keep validation proportional to risk.
- List testable behaviors for Plan; **do not invent test commands** (D2).

## Output Shape

```markdown
## Synthesis
One paragraph binding Product + Backend + Frontend + Copy.

## Goal
Concrete outcome.

## Current Terrain
Facts from recon and source files.

## Recommended Path
Chosen approach and why it fits the existing system.

## Files / Areas
| Path/Area | Action | Reason | Risk |
|---|---|---|---|

## Facets / Contracts
### Product
Promise, user-visible behavior, non-goals.

### Backend
Data shapes, API/action contracts, payload the UI receives, permissions,
state, migrations — path:line or UNPROVEN.

### Frontend
Components, shells, loading/error/empty states — reuse|mode|new + evidence.

### Copy
| String | Invariant | Structure | Forbidden safada |
|---|---|---|---|

## Cross-facet dependencies
| If this changes… | …must recode |
|---|---|

## Recode Log
| When | Trigger | Facet | Recode |
|---|---|---|---|

## Testable behaviors
Names for Plan/TDD — no fake commands.

## Sequence
Ordered implementation steps (not the final task tracker).

## Rollback / Containment
How to keep the blast radius bounded.

## Coherence check
Ready ≠ filled headings.

## Risks
Trade-offs and failure modes.
```

## Blueprint Quality Bar

- Every named file/area has a reason.
- Every critical contract has a validation path.
- Synthesis fails if any facet is removed.
- Legacy compatibility is isolated.
- Missing decisions are not hidden; they become open questions or blockers.
- If the blueprint cannot choose between two approaches, it explains the
  decision the human must make.
