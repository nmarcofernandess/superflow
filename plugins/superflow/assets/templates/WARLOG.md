# WARLOG: {title}

## Context

- Created: {created_at}
- Route: {route}
- Phase budget: {phase_budget}
- Confidence: {confidence}
- Source: {source}

## State Snapshot

```mermaid
stateDiagram-v2
  [*] --> Captured
  Captured --> PRD
  PRD --> Build
  Build --> Plan
  Plan --> Execute
  Execute --> QA
  QA --> Done
  QA --> Execute: fix
```

## Timeline

```mermaid
timeline
  title Superflow WARLOG
  Capture : idea recorded
  PRD : scope shaped
  Build : technical decision
  Execute : verified work
```

## Decisions

- Initial route: {route}
- Initial next phase: {next_phase}

## Event Log

- {created_at} | taskgen | Created WARLOG shell.

## Risks And Blocks

- {risks}

## Next Action

- {next_phase}
