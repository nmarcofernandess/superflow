# SPEC: {title}

## Inputs

- PRD: PRD.md
- Analyses consumed: list `analysis.md` / `ANALYSIS-*.md` actually read, or "none"
- Route: {route}
- Phase budget: {phase_budget}
- Mindset: `feature-mindset-contract.md`

## Synthesis

Um parágrafo que fecha a feature como **composição** de Produto + Backend +
Frontend + Copy. Colagem de headings = SPEC falho (F4, H2).

## Architecture Decision

Chosen path and why it fits existing terrain. Not the granular task list.

## Existing System Read

Real files, docs, schemas, commands — or marked UNPROVEN.

## Files / Boundaries

| Path/Area | Action | Reason | Risk |
|---|---|---|---|

## Facets

### Product

Promise, surface, non-goals, human decisions.

### Backend

Data path, payload shape, permissions, migrations if any — with path:line
or UNPROVEN (T1–T2).

### Frontend

Reuse map: shell/primitive/composition. Decision `reuse` | `mode` | `new`
with evidence. Plugin does not prescribe a fixed shell (T4–T6).

### Copy (strings-safadas)

| String / key | Invariant prose? | Structure (label+value / chip / count) | messages / emptyStates | Forbidden (safada) |
|---|---|---|---|---|
|  |  |  |  |  |

Cartesian test applied. Mock ≠ literal (S1–S6).

## Cross-facet dependencies

| If this changes… | …must recode |
|---|---|
| action payload | Product promise, Copy, Frontend counts/chips |
| chosen shell | Product surface, empty states |
| enum / plan type | Copy cartesian, Backend filters |

## Recode Log

| When | Trigger | Facet | Recode |
|---|---|---|---|
| from analysis / build |  |  |  |

## Testable behaviors (Plan handoff)

Lista de comportamentos que o Plan deve pré-compilar em RED/GREEN.
**Não** inventar comando de teste aqui (D1–D2). Ver `tdd-contract.md`.

- [ ] Behavior 1

## Implementation Sequence

- [ ] Step 1

Dependency order for Plan. Plan owns `implementation_plan.json` + TDD fields.

## Verification

- [ ] Static checks
- [ ] Targeted tests (via Plan/TDD)
- [ ] Runtime or visual proof when relevant

## Coherence check (ready)

- [ ] Synthesis breaks if any facet is removed
- [ ] No UI isolado without Backend path or Product non-goal
- [ ] No instance prose approved as system copy
- [ ] Ready ≠ filled headings alone (B1–B2)

## Risks

## Go / No-Go
