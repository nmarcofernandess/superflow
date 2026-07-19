# PRD: Investigar divergencia intermitente

## State

- Source: github_issue
- Confidence: low
- Route: investigate_first
- Phase budget: forensic
- Execution strategy: single
- Created: 2026-07-04T00:00:00Z

## Problem

Usuarios relatam divergencia intermitente entre totais exibidos e exportados,
mas a causa ainda nao foi provada.

## Goal

Provar a causa antes de definir fix.

## Users / Actors

- User comparing UI totals and exports.
- Maintainer responsible for the fix.

## Story de Usuario

As a user, I want exported totals to match displayed totals so I can trust the
report.

## Story Tecnica

As the investigating agent, I need to prove the source of divergence with logs,
tests, or code evidence before writing a fix.

## Current Behavior / Bug

Totals diverge intermittently, but the cause is unknown.

## Desired Behavior

Analyst investigation proves the cause and routes the work to the correct fix
path.

## System Pattern / Contract

Unknown bugs route to Analyst in investigation mode before PRD/build/plan.

## Acceptance Criteria

- [ ] Causa raiz provada por arquivo, log, teste ou reproduçao.
- [ ] Fix so e definido depois da investigacao do Analyst.
- [ ] QA cobre o caminho que reproduzia a divergencia.

## Definition of Complete

- [ ] Analyst investigation (`analysis.md`) proves or disproves the suspected
      cause.

## Next Phase

analyst (investigation mode)
