# Analyst: String safada trap (compliant kill)

## State

- Source: fixture trap
- Route: build_plan_execute
- Phase budget: deep
- Confidence: high
- Created: 2026-07-29
- Verdict: ready for build

## TL;DR

O mock propõe prosa-instância com R$ 180. Análise **mata** a frase e manda
estrutura. Não sobrevive como copy de sistema.

## Síntese

Substituir a frase de mock de valor de plano por **estrutura label+valor**
alimentada pelo DTO numérico; a prosa “como combinado” é pecado e morre.

## Phase 0 Grill

| Signal | Verdict | Notes |
|---|---|---|
| Action clear | yes |  |
| Persona clear | yes |  |
| Input/output clear | yes |  |
| Scope clear | yes |  |
| Objective criteria clear | yes |  |

## Source And Scope

mock trap

## Faceta — Produto

Mostrar valor sem inventar acordo.

## Faceta — Backend (dados reais)

Evidence: `src/lib/actions/agenda/drawer-actions.ts:88` — number override only (high).

## Faceta — Frontend (reuso antes de criar)

**Reuse Guard:**

| Need | Guard source | Decision | Evidence path |
|---|---|---|---|
| value row | grep | reuse | ui/density |

## Faceta — Copy (strings-safadas)

| Superfície | Texto candidato / mock | Pecado? | Destino: invariante \| estrutura \| morte |
|---|---|---|---|
| body | Continua Retorno por R$ 180,00, como foi combinado. | prosa-instância | **morte** → estrutura Valor + número |

Cartesian: 0/null, 1 valor, 1000 planos — a frase do mock não escala → morte.

## Recode Log

| When | Trigger (evidence) | Facet that broke | What was recoded |
|---|---|---|---|
| T1 | Mock prose; DTO is number | Copy | morte da prosa; estrutura |

## Product Promise

Honest value.

## Story de Usuario

Nutri vê valor.

## Story Tecnica

DTO → structure.

## Current Terrain

mock trap

## Evidence Matrix

| Path | Lines | Fact | Confidence |
|---|---:|---|---|
| drawer-actions.ts | 88 | number | high |

## Implementation Map

| Area | Path | Role | Decision |
|---|---|---|---|
| Backend | drawer-actions.ts:88 | dto | reuse |

## Entities And State

plan value number

## Runtime / Data Flow

dto → cell

## Rules And Invariants

no instance prose

## Blueprint Handoff

behaviors: null empty; number structured

## Grill Verdict

ready for build

## Open Questions

none

## Recommended Next Phase

build
