# Code Recon Protocol

Use when a codebase, docs set, or existing system matters. Recon is read-only.

## Mission

Find what is real before Analyst, Build, Plan, Execute, or QA makes claims.
Separate proven facts from inference and mark unknowns instead of smoothing over
them.

Recon feeds the **feature-mindset** facets (Produto / Backend / Frontend /
Copy). It is not a waterfall of folders — it is evidence for synthesis and
recode. See `feature-mindset-contract.md`.

## Rules

- Inspect actual files before asserting behavior.
- Prefer `rg`, `rg --files`, focused reads, docs, schema, tests, and commands.
- Start from the user's concrete boundary.
- Use `path:line` for evidence wherever possible (T1).
- Capture **payload/shape** that UI actually receives, not only model names (T2).
- Before proposing `new` UI or new action/service, run **Reuse Guard**
  (`reuse-guard-protocol.md`) — crystallize-guard style: Tier-2 `.context` if
  fresh, else grep families (T4–T6). Do not prescribe a fixed shell name as
  universal dogma.
- If subagents are available, use explorer lanes for independent discovery, but
  the final artifact must cite the files directly.
- Do not edit files from recon.
- `UNPROVEN` beats confident invention (B5).

## Recon by facet (attention order, not freeze)

Order of attention is often Product → Backend → Frontend → Copy. New evidence
can force **recode** of earlier facets.

| Facet | Inspect |
|---|---|
| Product surface | routes, journey, when UI appears, consequence vs onboarding |
| Backend truth | schema, actions, services, guards, policies, hooks, queries, cache, **response/DTO shape** |
| Frontend pattern | shells, primitives, providers, forms, modals, cards, tables, charts — **grep family before inventing** |
| Copy surfaces | toasts, empty states, banners, modal body, helpers — candidates for strings-safadas audit |
| Tests/proof | unit, integration, E2E, CI, proof scripts, fixtures, known flakes |
| Operations | env, migrations, queue, auth, branch/worktree, deploy |

## Recon Lenses (legacy names)

Same as facets above; use only the lenses needed for the ask.

## Output Shape

```markdown
## Recon Scope
What was inspected and why.

## Current Behavior
What the system actually does.

## Evidence Matrix
| Path | Lines | Fact | Confidence |
|---|---:|---|---|

## Payload / data path
What the screen receives (fields, counts, nullability).

## Reuse Guard (anti-fork)
- Need named:
- Graph (`.context` Tier-2) result: reuse path | none | stale-hint
- Grep families / commands:
- Decision: reuse | mode | new (+ justification if new)
- Evidence paths:

## Copy inventory
UI strings / mock phrases that need invariant|structure|death.

## File Topology Map
```text
src/
  # relevant nodes only
```

## Flows
Runtime/data/user flows that matter.

## Patterns To Preserve
Reusable primitives, shells, conventions, contracts — **discovered**, not prescribed.

## Constraints And Risks
Coupling, missing tests, auth/env/deploy boundaries, performance concerns.

## Unknowns
Only what could not be proven from files or safe commands (`UNPROVEN`).

## Implications
What analyst/build/plan/execution must respect — including which facets to recode.
```

## Topology Labels

- `# reuse`: already covered by an existing module/pattern.
- `# mode`: existing primitive with thin wrapper/mode.
- `# new`: likely new derivation point needed (only after scan).
- `# legacy`: live only for compatibility; do not spread it.
- `# unknown`: needs more recon before decision.

## Repo-aware default (T7)

**If** the target repo has `AGENTS.md` and/or `.context/` (e.g. DietFlow):

1. Read `AGENTS.md` (or equivalent) — triad/reuse rules if present.
2. Read module map (e.g. `.context/domains/manifest.yaml`).
3. Read domain/pattern docs listed there — full files, not samples.
4. Schema / actions / hooks / components / tests for the module.

**If not**, use generic recon: entry routes, schema/API layer, UI composition
roots, test layout. Do not invent DietFlow shell names.

Do not call an analysis grounded until the applicable chain is followed or
explicitly out of scope with `UNPROVEN` where needed.
