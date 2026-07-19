# Analyst Protocol

Use Analyst to turn a loose request, weak issue, or scary code area into
PRD-quality understanding. Analyst is not a summary writer. Analyst is domain
distillation plus grounded reconnaissance plus a handoff that Build can execute
without guessing.

## Mission

Produce an `analysis.md` that proves the product promise, system terrain,
entities, state transitions, rules, risks, and next phase. If the target touches
an existing codebase, the analysis must include source-backed evidence and an
implementation map.

## Golden Lineage

This protocol intentionally merges the strongest parts of:

- Supervibe Analyst: phase discipline, native grill, grounding, entities,
  machine-executable rules, visual modeling, and blueprint handoff.
- Code Flow Analyst: PRD-quality issue semantics, implementation mapping,
  `code-recon`, grill verdicts, and repo-agnostic handoff.
- Build / technical blueprint: Product -> Backend -> Frontend contracts, file
  boundaries, sequencing, validation, and risks.

Do not collapse this into a short PRD. If the request has architecture or
existing-code risk, a thin analysis is a failed analysis.

## Non-Negotiables

- Produce or update a durable artifact: `analysis.md` for local packages, or the
  issue body for inbox-only work.
- No `TBD`, no "definir depois" as a central decision. Either ask one precise
  question or record an explicit assumption with risk.
- Use Mermaid only.
- Every code/system claim must be backed by `path:line` or marked `UNPROVEN`.
- If the request names an existing module, schema, action, service, component,
  or doc set, run code recon before verdict.
- If the analysis will feed implementation, include a blueprint-quality handoff:
  files/areas, contracts, sequence, validation, and risks.
- Run a grill pass before declaring `ready for build` or `ready for taskgen`.

## Phase 0 - Native Grill

Score the input before writing. Each missing item is one point of ambiguity:

| Signal | Question |
|---|---|
| Action | What action/result is desired? |
| Persona | Who uses or suffers from this? |
| Input/output | What enters, what changes, what is emitted? |
| Scope | What is in and out? |
| Objective criteria | Have vague words become measurable behavior? |

Rules:

- 0-1 ambiguity points: proceed.
- 2-3 ambiguity points: ask one precise question unless repo evidence can answer.
- 4-5 ambiguity points: stop after at most three surgical questions, then record
  assumptions if the user wants forward motion.

## Phase 1 - Mode And Scope

Classify the analyst job:

- `construction`: new product/system behavior.
- `extraction`: existing system behavior must be documented.
- `audit`: current architecture or implementation must be judged.
- `hybrid`: existing system plus proposed change.
- `investigation`: bug or unknown behavior without proven cause. There is no
  separate Discovery phase — reproduce, read logs/tests/code paths until the
  cause is proven with evidence or explicitly `UNPROVEN`; only then scope a
  fix and route forward.

Record:

- source: user request, issue, PRD, spec folder, or diff;
- route and phase budget;
- expected next phase;
- whether Build is mandatory after Analyst.

## Phase 2 - Code Recon

Use `code-recon-protocol.md` when reality matters. Do this before writing
technical conclusions.

Minimum recon for existing code:

1. Entry/context: local instructions, manifests, module docs, route/config maps.
2. Backend truth: schema, actions/API, services, guards, hooks, queries, cache.
3. Frontend truth when relevant: shells, providers, components, forms, tables,
   modals, empty/error/loading states.
4. Tests/proofs: unit/integration/E2E/proof scripts and missing coverage.
5. Operational constraints: branch/worktree, migrations, env, queue, deploy.

When useful, split recon into explorer lanes, but the final `analysis.md` must
cite the files itself. Subagents do not replace evidence.

## Phase 3 - Product Promise

Write the promise in one hard paragraph:

- user/persona;
- broken or desired outcome;
- current pain;
- success behavior;
- explicit non-goals.

Translate vague terms:

| Vague | Analyst must convert to |
|---|---|
| easy | steps, decisions, friction removed |
| fast | latency, wait states, queue/deploy impact |
| robust | failure modes, fallback, recovery |
| consistent | source of truth, derivation path, anti-drift rule |

## Phase 4 - Entities, State, Rules

For each meaningful object:

```text
ENTITY: <Name>
- Attributes:
- Actions:
- Relations:
- Source of truth:
- Runtime states:
- Invalid states to prevent:
```

Rules must pass the dumb-machine test:

- Can a machine execute it without "common sense"?
- Are edge cases covered: empty, duplicate, archived/deleted, missing profile,
  permissions, concurrent update, stale cache?
- Do conditionals overlap or leave gaps?

## Phase 5 - Implementation Map

Every analyst run that touches real code must include a navigable map.

Use this order:

1. Context / entry points.
2. Backend contracts.
3. Services / hooks / state.
4. Shells / shared primitives.
5. Frontend composition.
6. Tests and proof harness.

Each row must include:

| Path | Role | Evidence | Decision |
|---|---|---|---|
| `path:line` | what it owns | observed fact | reuse/new/legacy/unknown |

Do not write "see repo" or "inspect later". If it matters, inspect it now.

## Phase 6 - Blueprint Handoff

If the output can become implementation, include a blueprint-quality handoff.
Use `technical-blueprint-protocol.md` as the contract.

Minimum sections:

- Files / areas likely to change.
- Ownership boundaries.
- Product contract.
- Backend contract.
- Frontend contract when relevant.
- Sequence.
- Validation.
- Risks and rollback.

If architecture risk is high, verdict must be `ready for build`, not
`ready for execution`.

## Phase 7 - Visual Model

Use Mermaid only when it reduces ambiguity. Preferred diagram types:

- `flowchart TD`: request/data/runtime flow.
- `sequenceDiagram`: API/action/service chain.
- `erDiagram`: entities and relations.
- `stateDiagram-v2`: lifecycle/status transitions.

No decorative diagrams. Diagram must clarify a decision, entity relation, or
runtime path.

## Phase 8 - Grill Verdict

Run a final self-review:

- Does every major claim have evidence?
- Is product promise tied to implementation terrain?
- Are entities and state transitions explicit?
- Are legacy/debt and live paths separated?
- Are next phases sequenced correctly?
- Is the work one task, multiple slices, or a larger program?

Allowed verdicts:

- `ready for taskgen`;
- `ready for build`;
- `needs recon`;
- `needs human decision`;
- `split required`;
- `capture only`;
- `blocked: insufficient evidence`.

## Required `analysis.md` Shape

Use these headings for local package output:

```markdown
# Analyst: <Title>

## State
## TL;DR
## Phase 0 Grill
## Source And Scope
## Product Promise
## Current Terrain
## Evidence Matrix
## Implementation Map
## Entities And State
## Runtime / Data Flow
## Rules And Invariants
## Architecture Risks
## Blueprint Handoff
## Acceptance Criteria
## Open Questions
## Grill Verdict
## Recommended Next Phase
```

`Evidence Matrix` and `Implementation Map` are mandatory for existing-system
work. If either is missing, the analysis is not done.

## Anti-Patterns

| Anti-pattern | Why it fails |
|---|---|
| A list of risks without file/line evidence | Cannot be reviewed or executed safely |
| Product promise without entities/state | Nice prose, no system logic |
| Architecture critique without blueprint handoff | Leaves Build to rediscover everything |
| "Ready" with unresolved source-of-truth questions | Green false |
| Reusing Superflow route output as analyst output | Classifier is not analysis |
