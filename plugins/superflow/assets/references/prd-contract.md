# PRD Contract

The PRD is the source of truth for a Superflow task. It can live in a GitHub
issue or in `specs/NNN-slug/PRD.md`. The layout stays the same; the maturity and
confidence fields say how ready it is.

The PRD is written for two readers: the people who need to understand the
product problem and the people who will implement it. The short explanation at
the top must serve the first reader without replacing the precise contract
below.

## Required Sections

```md
# PRD: <title>

## TL;DR

<standalone causal explanation written after the full PRD has been drafted and reread>

## State

- Source:
- Confidence:
- Route:
- Phase budget:
- Execution strategy:
- Created:

## Problem

## Goal

## Users / Actors

## Story de Usuario

## Story Tecnica

## Scope

### In Scope

### Out of Scope

## Expected Behavior

## Current Behavior / Bug

## Desired Behavior

## System Pattern / Contract

## Acceptance Criteria

- [ ] ...

## Definition of Complete

- [ ] ...

## Technical Context

## Data / Contracts

## UX / States

## Risks

## Open Questions

## Next Phase
```

## TL;DR rule

`## TL;DR` is the first section after the title and the last PRD section to be
written. It is a standalone causal explanation, not a shorter pile of the PRD's
existing abstractions.

**REQUIRED SUB-SKILL:** use `explain-clearly` in TL;DR mode after completing and
rereading the full PRD. It reconstructs the object model, separates current
truth from decisions and in-flight work, pays inference debt, and runs the
reasonable-objection and closed-book paraphrase gates. Then use
`writing-clearly-and-concisely` for the final copyedit.

The TL;DR must explain the familiar user situation, concrete current mechanism,
reason for the mismatch, observable consequence, target behavior, and scope
boundary. There is no hard word limit. It is the shortest version that preserves
the causal chain, not the shortest text the writer can produce.

An ASCII sketch or Mermaid diagram may follow the prose when it materially
reduces inference work. The visual supports the explanation; it never replaces
the missing sentence. Mermaid follows `references/mermaid-contract.md`.

The TL;DR must not introduce a decision, promise, or scope boundary absent from
the body. If the semantic pass exposes a contradiction, fix the body first and
regenerate the TL;DR.

A scaffold in `gathering` may contain an explicit placeholder. Before the PRD
is promoted to `ready`, replace it with a real summary. The validator checks
placement and placeholders; semantic quality belongs to `explain-clearly` and
human review.

## Confidence

| Confidence | Meaning | Allowed next step |
|------------|---------|-------------------|
| `low` | Useful capture, missing core facts | inbox, analyst, ask |
| `medium` | Implementable after plan/build | plan, build, analyst |
| `high` | Ready for direct execution or plan | execute, plan |

## PRD States

`decision.prd_status` in `status.json` tracks the deliverable state of the
PRD itself:

| State | Meaning |
|---|---|
| `gathering` | Still collecting decisions/evidence. Every scaffold is born here. |
| `ready` | Fulfills this contract and can feed the next phase. |
| `blocked` | Depends on an external decision or missing evidence. |
| `superseded` | Another version/artifact is canonical now. |

Promotion `gathering -> ready` is an act of the skill that wrote or reviewed
the PRD content against this contract — never of a script or keyword score. A
structurally complete file that is semantically empty ("To be filled...")
stays `gathering`. Legacy specs may contain `draft`/`complete`/`discarded`;
read them as `gathering`/`ready`/`superseded` (lazy migration).

## Acceptance Criteria Rules

- Criteria must be observable.
- Criteria must avoid "works well" language.
- Each criterion should be individually checkable.
- Include at least one regression/non-goal criterion for changes near existing
  behavior.

## Visual Usage

Use Mermaid only when it reduces ambiguity. Prefer:

- `flowchart` for phase and user flow.
- `stateDiagram-v2` for lifecycle/status.
- `sequenceDiagram` for tool/system interaction.
- `erDiagram` for data shape.

Do not include decorative diagrams.

The narrow TL;DR exception is a small ASCII sketch for a contrast or mapping
that is clearer as text. Other PRD diagrams remain Mermaid.

## Local PRD Package

```txt
specs/NNN-slug/
├── PRD.md
├── status.json
└── progress.md
```

Optional artifacts:

```txt
analysis.md
ANALYSIS-*.md
SPEC.md
technical_blueprint.md   (legacy name for SPEC.md)
implementation_plan.json
implementation_plan.md
implementation_log.json
qa_report.md
units/*/PRD.md
```

## Story Rules

- `Story de Usuario` states who needs the outcome, what changes for them, and
  why it matters.
- `Story Tecnica` states the system obligation that makes the user story true:
  source of truth, contract, state, or integration expectation.
- `Current Behavior / Bug` can say "Not proven yet" for new work, but existing
  bug or gap claims need evidence before execution.
- `System Pattern / Contract` names the local pattern to preserve or says what
  the next phase must prove.
- `Definition of Complete` is broader than acceptance criteria: it includes
  artifact/status updates and proof closure.
