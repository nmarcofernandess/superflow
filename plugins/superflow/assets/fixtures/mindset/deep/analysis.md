# Analyst: Drawer plan value honesty

## State

- Source: fixture mindset deep
- Route: build_plan_execute
- Phase budget: deep
- Confidence: high
- Created: 2026-07-29
- Verdict: ready for build
- Mindset: feature-mindset-contract.md

## TL;DR

O drawer deve mostrar o valor do plano como dado estruturado. O backend já
expõe override numérico; a copy “como combinado” é safada e morre. Reusar o
shell do drawer existente.

## Síntese

A feature é **mostrar o valor real do plano no drawer de atendimento** usando
o payload `planValueOverride` de `getAtendimentoDrawer` (`actions.ts:88`),
reusando o shell `UnifiedAgendaDrawer` com bloco label+valor — sem prosa que
invente acordo social. Copy invariante só para regras de não-edição de
concluídos; o número mora em chip/label.

## Phase 0 Grill

| Signal | Verdict | Notes |
|---|---|---|
| Action clear | yes | show plan value honestly |
| Persona clear | yes | nutricionista |
| Input/output clear | yes | drawer open → value visible |
| Scope clear | yes | drawer only |
| Objective criteria clear | yes | no instance prose |

## Source And Scope

- Input source: fixture
- In scope: drawer plan value display
- Out of scope: billing engine rewrite
- Assumptions: none material

## Faceta — Produto

Promessa: ao abrir o atendimento, o nutri vê o valor do plano **como fato do
sistema**, não como narrativa de acordo. Superfície: drawer (consequência de
abrir o item), não modal de onboarding. Non-goal: não “explicar o que é plano”.

## Faceta — Backend (dados reais)

| Path | Lines | Payload / fact | Confidence |
|---|---:|---|---|
| `src/lib/actions/agenda/drawer-actions.ts` | 88 | `planValueOverride: number \| null` no DTO do drawer | high |
| `prisma/schema.prisma` | 1204 | campo numérico no atendimento | high |

A tela recebe número ou null — não recebe “combinado”.

## Faceta — Frontend (reuso antes de criar)

**Reuse Guard** (antes da Síntese):

| Need | Guard source `graph` \| `grep` \| `both` \| `stale-hint` | Decision `reuse` \| `mode` \| `new` | Evidence path / canônico |
|---|---|---|---|
| Drawer shell | both (`.context` patterns/drawer + `rg UnifiedAgendaDrawer`) | reuse | `src/components/features/agenda/UnifiedAgendaDrawer.tsx:1` |
| Label+value row | grep | reuse | density / label primitives |

## Faceta — Copy (strings-safadas)

| Superfície | Texto candidato / mock | Pecado? | Destino: invariante \| estrutura \| morte |
|---|---|---|---|
| Drawer body | “Continua Retorno por R$ 180,00, como foi combinado.” | prosa-instância | **morte** → estrutura label “Valor” + valor formatado |
| Helper | “Atendimentos concluídos não são alterados.” | nenhum | **invariante** messages |

## Recode Log

| When | Trigger (evidence) | Facet that broke | What was recoded |
|---|---|---|---|
| T1 | Mock copy assumed social agreement; DTO only has number (`drawer-actions.ts:88`) | Product + Copy | Promise sem “combinado”; copy → estrutura |

## Product Promise

Nutri vê valor honesto do plano no drawer; sem inventar reunião.

## Story de Usuario

Como nutricionista, quero ver o valor do plano no atendimento sem o sistema
fingir que houve um acordo verbal.

## Story Tecnica

Como implementador, devo mapear `planValueOverride` para UI estruturada no
drawer existente, sem primitivo novo e sem prosa-instância.

## Current Terrain

Drawer e DTO já existem; copy mock é a mentira.

## Evidence Matrix

| Path | Lines | Fact | Confidence |
|---|---:|---|---|
| `src/lib/actions/agenda/drawer-actions.ts` | 88 | planValueOverride no payload | high |

## Implementation Map

| Area | Path | Role | Decision |
|---|---|---|---|
| Backend contracts | `drawer-actions.ts:88` | DTO | reuse |
| Shells | `UnifiedAgendaDrawer.tsx` | shell | reuse |
| Frontend composition | density label row | display | reuse |
| Tests / proof | plan value unit | coverage | new test behavior name only |

## Entities And State

```text
ENTITY: AtendimentoDrawerDTO
- Attributes: planValueOverride
- Source of truth: server action
- Invalid states: null shown as empty structure not invented prose
```

## Runtime / Data Flow

Open drawer → action → DTO → label+value.

## Rules And Invariants

- Null override → empty value cell, no fake currency prose.
- Concluded attendance: invariant “não são alterados” only.

## Blueprint Handoff

- Files: drawer shell + small display block
- Testable behaviors: “null override shows empty value cell”; “number shows formatted currency in structure”
- Sequence: wire field → kill mock string → test
- Risks: low

## Grill Verdict

ready for build

## Open Questions

none

## Recommended Next Phase

build
