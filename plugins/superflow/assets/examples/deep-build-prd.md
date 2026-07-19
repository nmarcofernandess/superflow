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

## Users / Actors

- Finance operator.
- Maintainer implementing billing/reporting changes.

## Story de Usuario

As a finance operator, I want payment status to mean one clear thing so reports
and screens do not disagree.

## Story Tecnica

As the implementing agent, I need a blueprint that separates operational and
financial status before any schema, UI, or report change is coded.

## Current Behavior / Bug

Payment status mixes operational and financial meaning.

## Desired Behavior

The system has separate, validated contracts before implementation starts.

## System Pattern / Contract

High-risk schema/report changes require Build before Plan.

## Risks

- Migracao de dados.
- Compatibilidade com relatórios existentes.
- Risco de cobrança incorreta.

## Acceptance Criteria

- [ ] Existe blueprint antes de codar.
- [ ] Migração tem plano de rollback ou estratégia expand-only.
- [ ] Relatórios existentes continuam consistentes.

## Definition of Complete

- [ ] `SPEC.md` closes contracts, sequence, validation, and rollback.

## Next Phase

build
