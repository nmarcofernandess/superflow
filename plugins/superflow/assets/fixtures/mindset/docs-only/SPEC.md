# SPEC: Docs-only glossary fix

## Inputs

- PRD: PRD.md
- Analyses consumed: analysis.md
- Route: prd_execute
- Phase budget: lean
- Mindset: feature-mindset-contract.md

## Synthesis

Alterar README com definição invariante de “plano do paciente”; sem backend UI.

## Architecture Decision

Docs only.

## Existing System Read

README.

## Files / Boundaries

| Path/Area | Action | Reason | Risk |
|---|---|---|---|
| README.md | modify | wording | none |

## Facets

### Product

Clear term for readers.

### Backend

skip_reason: docs-only

### Frontend

skip_reason: docs-only

### Copy (strings-safadas)

| String / key | Invariant prose? | Structure | messages / emptyStates | Forbidden (safada) |
|---|---|---|---|---|
| plano do paciente definition | yes | — | README | — |

## Cross-facet dependencies

| If this changes… | …must recode |
|---|---|
| term meaning in product | this doc |

## Recode Log

skip_reason: docs-only

## Testable behaviors (Plan handoff)

- [ ] none — docs

## Implementation Sequence

- [ ] Edit README

## Verification

- [ ] link/lint docs if any

## Coherence check (ready)

- [x] proportional

## Risks

none

## Go / No-Go

Go
