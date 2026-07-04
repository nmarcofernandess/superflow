# PRD: Migrar status de pagamentos

## State

- Source: inline
- Confidence: medium
- Route: build_plan_execute
- Phase budget: deep
- Execution strategy: single
- Created: 2026-07-04T00:00:00Z

## Problem

O status de pagamentos hoje mistura estado operacional e estado financeiro.

## Goal

Separar contrato de estado antes de alterar telas e relatórios.

## Risks

- Migracao de dados.
- Compatibilidade com relatórios existentes.
- Risco de cobrança incorreta.

## Acceptance Criteria

- [ ] Existe blueprint antes de codar.
- [ ] Migração tem plano de rollback ou estratégia expand-only.
- [ ] Relatórios existentes continuam consistentes.

## Next Phase

build
