# Build Protocol

Use Build to turn a mature PRD or analyst artifact into a grounded technical
blueprint/spec.

## Mission

Create a technical specification that proves the terrain and defines how the
product promise will be implemented or intentionally deferred.

## Autocontained Dependencies

- Use `code-recon-protocol.md` for real terrain.
- Use `technical-blueprint-protocol.md` for file-level plan and contracts.
- Use `analyst-protocol.md` when the PRD or analysis is too thin.
- Use a grill pass before calling the blueprint ready.

Do not depend on external Build, Analyst, feature-development, or custom agent
plugins. Subagents may accelerate recon, but this plugin's artifacts own the
final evidence and decisions.

## Required Phases

### 1. Confirm Input

Require one of:

- GitHub Issue with PRD;
- `analysis.md`;
- `PRD.md`;
- clear user request explicitly asking for blueprint/spec.

If the input lacks product promise, entities, scope, or source truth, route back
to Analyst.

### 2. Recon Terrain

Run recon before architecture when the target is an existing system.

For DietFlow:

- read `AGENTS.md`;
- use `.context/domains/manifest.yaml` to find the module;
- read relevant pattern YAMLs and READMEs;
- inspect schema/actions/hooks/services/components/tests for the module.

### 3. Product -> Backend -> Frontend

SPEC must close in this order:

1. Product: promise, journey, user consequence, non-goals.
2. Backend: data model, actions/API, permissions, state, cache/revalidation,
   migrations if any.
3. Frontend: shell, components, loading/error/empty states, layout,
   interactions, validation.

### 4. Architecture Diagrams

Use Mermaid:

- `flowchart TD` for implementation flow;
- `sequenceDiagram` for call chains;
- `erDiagram` for data;
- `stateDiagram-v2` for lifecycle;
- controlled `flowchart` for component/module map.

No PlantUML.

### 5. Blueprint

Produce:

- files/areas;
- contracts;
- sequence;
- validation;
- risks;
- rollback/containment.

### 6. Handoff

If ready:

- write `technical_blueprint.md` or repo-native equivalent;
- update `status.json` with `phases.build = "complete"` and
  `artifacts.blueprint = "technical_blueprint.md"`;
- route to `plan` or `warlog` only when sequencing is clear.

Build is not ready if:

- technical claims lack proof;
- a reusable pattern is ignored;
- validation is vague;
- PR scope is too large;
- human product decision is still unresolved.
