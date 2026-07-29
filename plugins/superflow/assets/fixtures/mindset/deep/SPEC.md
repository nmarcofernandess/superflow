# SPEC: Drawer plan value honesty

## Inputs

- PRD: PRD.md
- Analyses consumed: analysis.md
- Route: build_plan_execute
- Phase budget: deep
- Mindset: feature-mindset-contract.md

## Synthesis

Mostrar `planValueOverride` do DTO do drawer (`drawer-actions.ts:88`) como
**label+valor** dentro do `UnifiedAgendaDrawer` reutilizado; matar prosa
“como combinado”; invariantes só para regras de concluído.

## Architecture Decision

Reuse drawer shell; no new modal; no billing rewrite.

## Existing System Read

DTO and drawer shell proven in analysis evidence matrix.

## Files / Boundaries

| Path/Area | Action | Reason | Risk |
|---|---|---|---|
| UnifiedAgendaDrawer | modify | host value row | low |
| drawer-actions | reuse | payload source | low |

## Facets

### Product

Honest plan value on open drawer; non-goal: onboarding copy.

### Backend

`planValueOverride: number | null` at `drawer-actions.ts:88`.

### Frontend

reuse `UnifiedAgendaDrawer`; reuse density label row; no new shell.

### Copy (strings-safadas)

| String / key | Invariant prose? | Structure | messages / emptyStates | Forbidden (safada) |
|---|---|---|---|---|
| mock “Continua Retorno por R$ 180…” | no | Valor + currency cell | — | morte |
| “Atendimentos concluídos não são alterados.” | yes | — | messages | — |

## Cross-facet dependencies

| If this changes… | …must recode |
|---|---|
| DTO loses planValueOverride | Product promise + Frontend row + Copy |
| Drawer shell replaced | Frontend reuse decision |

## Recode Log

| When | Trigger | Facet | Recode |
|---|---|---|---|
| from analysis T1 | DTO is number only | Copy/Product | kill combinado prose |

## Testable behaviors (Plan handoff)

- [ ] Null override renders empty structured value (no invented currency)
- [ ] Numeric override renders in label+value structure

## Implementation Sequence

- [ ] Wire field into drawer row
- [ ] Remove mock prose

## Verification

- [ ] Unit/component test via Plan TDD
- [ ] Manual drawer open

## Coherence check (ready)

- [x] Synthesis breaks without Backend path
- [x] No UI without data path
- [x] No instance prose as system copy
- [x] Ready ≠ headings alone

## Risks

Low.

## Go / No-Go

Go.
