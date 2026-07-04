# Code Recon Protocol

Use when a codebase, docs set, or existing system matters. Recon is read-only.

## Mission

Find what is real before Analyst, Build, Plan, Execute, or QA makes claims.
Separate proven facts from inference and mark unknowns instead of smoothing over
them.

## Rules

- Inspect actual files before asserting behavior.
- Prefer `rg`, `rg --files`, focused reads, docs, schema, tests, and commands.
- Start from the user's concrete boundary.
- Use `path:line` for evidence wherever possible.
- If subagents are available, use explorer lanes for independent discovery, but
  the final artifact must cite the files directly.
- Do not edit files from recon.

## Recon Lenses

Use only the lenses needed for the ask:

| Lens | Inspect |
|---|---|
| Product surface | routes, UI flow, screenshots, copy, empty/error/loading states |
| Backend truth | schema, actions, services, guards, policies, hooks, queries, cache |
| Frontend pattern | shells, primitives, providers, forms, modals, cards, tables, charts |
| Tests/proof | unit, integration, E2E, CI, proof scripts, fixtures, known flakes |
| Operations | env, migrations, queue, auth, branch/worktree, deploy |
| Topology | domain file tree with ownership comments and reuse/new/unknown labels |

## Output Shape

```markdown
## Recon Scope
What was inspected and why.

## Current Behavior
What the system actually does.

## Evidence Matrix
| Path | Lines | Fact | Confidence |
|---|---:|---|---|

## File Topology Map
```text
src/
  # relevant nodes only
```

## Flows
Runtime/data/user flows that matter.

## Patterns To Preserve
Reusable primitives, shells, conventions, contracts.

## Constraints And Risks
Coupling, missing tests, auth/env/deploy boundaries, performance concerns.

## Unknowns
Only what could not be proven from files or safe commands.

## Implications
What analyst/build/plan/execution must respect.
```

## Topology Labels

- `# reuse`: already covered by an existing module/pattern.
- `# new`: likely new derivation point needed.
- `# legacy`: live only for compatibility; do not spread it.
- `# unknown`: needs more recon before decision.

## DietFlow Recon Default

When the target repo is DietFlow and the ask touches a clinical/admin module,
the first pass normally reads:

1. `AGENTS.md`.
2. `.context/domains/manifest.yaml`.
3. Module domain YAML and listed pattern YAMLs.
4. `prisma/schema.prisma` for model truth.
5. Module actions/services/hooks/components/tests.

Do not call a DietFlow analysis grounded until this chain is either followed or
explicitly declared out of scope.
