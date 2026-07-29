# Analyst: {title}

## State

- Source: {source}
- Route: {route}
- Phase budget: {phase_budget}
- Confidence: {confidence}
- Created: {created_at}
- Verdict: pending
- Mindset: `feature-mindset-contract.md` (facetas, não waterfall)

## TL;DR

2–4 frases: o que é, o que o terreno prova, se está ready for build/taskgen
ou o que bloqueia.

## Síntese

Um parágrafo que **amarra** Produto + Backend + Frontend + Copy.  
Se remover qualquer faceta o parágrafo deve quebrar. Colagem de três
seções soltas = análise falha (F4).

## Phase 0 Grill

| Signal | Verdict | Notes |
|---|---|---|
| Action clear |  |  |
| Persona clear |  |  |
| Input/output clear |  |  |
| Scope clear |  |  |
| Objective criteria clear |  |  |

## Source And Scope

- Input source:
- In scope:
- Out of scope:
- Assumptions:

## Faceta — Produto

Promessa, jornada, superfície (tela/modal/editor/dashboard), non-goals.
Modal só para consequência real — não onboarding.

## Faceta — Backend (dados reais)

| Path | Lines | Payload / fact | Confidence |
|---|---:|---|---|
| `UNPROVEN` | - | Substituir por path:line do action/hook/schema ou manter UNPROVEN | low |

O que a tela **realmente** recebe (shape), não só “model existe” (T1–T2).

## Faceta — Frontend (reuso antes de criar)

| Need | Scan (grep/family) | Decision `reuse` \| `mode` \| `new` | Evidence path |
|---|---|---|---|
|  |  |  |  |

O plugin manda **procurar** equivalente no repo; não prescreve shell dogmático (T4–T6).

## Faceta — Copy (strings-safadas)

| Superfície | Texto candidato / mock | Pecado? | Destino: invariante \| estrutura \| morte |
|---|---|---|---|
|  |  |  |  |

Prosa só para invariantes. Dado em label/chip/contador. Teste do cartesiano
antes de aprovar copy (S1–S5).

## Recode Log

| When | Trigger (evidence) | Facet that broke | What was recoded |
|---|---|---|---|
|  |  |  |  |

Deep/existing-code: ≥1 entrada real se a síntese mudou, ou registro de que
a síntese inicial já casou com o terreno.  
Docs-only: `skip_reason` honesto (B3).  
Append-only sem revisit = FAIL (F5–F6).

## Product Promise

Who needs what outcome, what is broken today, and what success looks like.
Promise sem dado de Backend → UNPROVEN ou non-goal (T3).

## Story de Usuario

As a concrete user or operator, describe the outcome they need and why the
current system fails or underserves that outcome.

## Story Tecnica

As the implementing agent/system, describe the technical obligation that must
be satisfied to make the user story true without violating repository patterns.

## Current Terrain

Facts from the current system. Existing-code claims require evidence.

## Evidence Matrix

| Path | Lines | Fact | Confidence |
|---|---:|---|---|
| `UNPROVEN` | - | Replace with source-backed evidence before ready verdict. | low |

## Implementation Map

| Area | Path | Role | Decision |
|---|---|---|---|
| Context / entry | `UNPROVEN` |  | unknown |
| Backend contracts | `UNPROVEN` |  | unknown |
| Services / hooks / state | `UNPROVEN` |  | unknown |
| Shells / shared primitives | `UNPROVEN` |  | unknown |
| Frontend composition | `UNPROVEN` |  | unknown |
| Tests / proof | `UNPROVEN` |  | unknown |

## Entities And State

```text
ENTITY: <Name>
- Attributes:
- Actions:
- Relations:
- Source of truth:
- Runtime states:
- Invalid states to prevent:
```

## Runtime / Data Flow

Mermaid when it reduces ambiguity.

## Rules And Invariants

Machine-executable rules. Edge cases: empty, duplicate, archived, permission,
stale cache.

## Blueprint Handoff

- Files / areas:
- Product / Backend / Frontend / Copy contracts (summary):
- Testable behaviors for Plan (names only — no fake test commands) (D2):
- Sequence:
- Validation:
- Risks / rollback:

## Grill Verdict

- ready for taskgen | ready for build | needs recon | needs human decision |
  split required | capture only | blocked: insufficient evidence

## Open Questions

## Recommended Next Phase
