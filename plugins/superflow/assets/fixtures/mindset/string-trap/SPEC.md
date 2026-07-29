# SPEC: String safada trap (kill)

## Inputs

- PRD: PRD.md
- Analyses consumed: analysis.md
- Route: build_plan_execute
- Phase budget: deep
- Mindset: feature-mindset-contract.md

## Synthesis

DTO numérico vira label+valor; a prosa de mock com R$ 180 e “combinado” está
**morta**, não aprovada como UI copy.

## Architecture Decision

Structure not prose.

## Existing System Read

DTO number.

## Files / Boundaries

| Path/Area | Action | Reason | Risk |
|---|---|---|---|
| drawer | modify | display | low |

## Facets

### Product

Honest value display.

### Backend

planValueOverride number path drawer-actions.ts:88

### Frontend

reuse drawer row

### Copy (strings-safadas)

| String / key | Invariant prose? | Structure | messages / emptyStates | Forbidden (safada) |
|---|---|---|---|---|
| mock Continua Retorno por R$ 180… | no | Valor + currency | — | **morte** |

## Cross-facet dependencies

| If this changes… | …must recode |
|---|---|
| payload type | Copy structure |

## Recode Log

| When | Trigger | Facet | Recode |
|---|---|---|---|
| analysis | mock prose | Copy | morte |

## Testable behaviors (Plan handoff)

- [ ] structured value only

## Implementation Sequence

- [ ] kill prose
- [ ] wire structure

## Verification

- [ ] tests via Plan

## Coherence check (ready)

- [x] no safada as system copy

## Risks

none

## Go / No-Go

Go
