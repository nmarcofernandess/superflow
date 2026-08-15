
# PRD: fixture

## State
ready

## Problem
Need clear plan change messaging.

## Goal
Honest UI for plan change.

## Users / Actors
Nutricionista.

## Story de Usuario
Como nutri, preciso ver o valor do plano sem prosa falsa.

## Story Tecnica
Expor payload real de plano no drawer.

## Scope
Drawer de atendimento.

## Expected Behavior
Mostra label+valor; sem "como combinado".

## Current Behavior / Bug
Copy inventa acordo.

## Desired Behavior
Estrutura label+valor.

## System Pattern / Contract
Reuse drawer shell.

## Acceptance Criteria
- valor exibido como dado
- sem prosa-instância

## Definition of Complete
SPEC + analysis mindset pass.

## Technical Context
fixture

## Data / Contracts
Plan value override field.

## UX / States
drawer

## Risks
string safada

## Open Questions
none

## Next Phase
build

