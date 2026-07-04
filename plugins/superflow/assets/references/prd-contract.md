# PRD Contract

The PRD is the source of truth for a Superflow task. It can live in a GitHub
issue or in `specs/NNN-slug/PRD.md`. The layout stays the same; the maturity and
confidence fields say how ready it is.

## Required Sections

```md
# PRD: <title>

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

## Scope

### In Scope

### Out of Scope

## Expected Behavior

## Acceptance Criteria

- [ ] ...

## Technical Context

## Data / Contracts

## UX / States

## Risks

## Open Questions

## Next Phase
```

## Confidence

| Confidence | Meaning | Allowed next step |
|------------|---------|-------------------|
| `low` | Useful capture, missing core facts | inbox, analyst, ask, discovery |
| `medium` | Implementable after plan/build | plan, build, analyst |
| `high` | Ready for direct execution or plan | execute, plan |

## Acceptance Criteria Rules

- Criteria must be observable.
- Criteria must avoid "works well" language.
- Each criterion should be individually checkable.
- Include at least one regression/non-goal criterion for changes near existing
  behavior.

## Mermaid Usage

Use Mermaid only when it reduces ambiguity. Prefer:

- `flowchart` for phase and user flow.
- `stateDiagram-v2` for lifecycle/status.
- `sequenceDiagram` for tool/system interaction.
- `erDiagram` for data shape.

Do not include decorative diagrams.

## Local PRD Package

```txt
specs/NNN-slug/
├── PRD.md
├── status.json
└── progress.md
```

Optional artifacts:

```txt
discovery.json
technical_blueprint.md
implementation_plan.md
qa_report.md
units/*/PRD.md
```
