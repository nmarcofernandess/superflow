# PRD: Exportar CSV filtrado

## TL;DR

O administrador já consegue combinar busca, filtros e ordenação até enxergar
na tela exatamente os registros de que precisa. Hoje esse recorte fica preso à
tela porque não existe uma ação de exportação.

A mudança cria um CSV a partir da mesma seleção que alimenta a lista visível.
Ela não cria uma segunda lógica de filtros nem muda a ordem dos resultados;
apenas permite levar para fora do sistema o recorte que o administrador já
montou.

## State

- Source: inline
- Confidence: high
- Route: prd_execute
- Phase budget: lean
- Execution strategy: single
- Created: 2026-07-04T00:00:00Z

## Problem

Admin precisa exportar a lista filtrada em CSV sem alterar os filtros existentes.

## Goal

Adicionar exportacao CSV no fluxo atual preservando busca, filtros e ordenacao.

## Users / Actors

- Admin user.

## Story de Usuario

As an admin user, I want to export the currently filtered report list to CSV so
I can use the same view outside the app.

## Story Tecnica

As the implementing agent, I need to reuse the existing filter source of truth
and add export behavior without changing search, filters, or ordering.

## Current Behavior / Bug

The filtered list is visible but not exportable.

## Desired Behavior

CSV export includes exactly the currently visible filtered records.

## System Pattern / Contract

Lean route can execute directly because behavior is clear, low-risk, and
testable.

## Acceptance Criteria

- [ ] Exporta exatamente os registros visiveis pelo filtro atual.
- [ ] Nao altera filtros existentes.
- [ ] Existe teste ou prova focada do comportamento.

## Definition of Complete

- [ ] Export behavior is implemented and verified without filter regressions.

## Next Phase

execute
