# Build Protocol

Use Build to turn a mature PRD or analyst artifact into a grounded technical
blueprint/spec.

## Mission

Create a technical specification that proves the terrain and defines how the
product promise will be implemented or intentionally deferred.

Build is not the final implementation plan. It closes architecture, contracts,
boundaries, risk, validation strategy, and sequence. Plan later converts that
blueprint into executable subtasks in `implementation_plan.json` under
`tdd-contract.md` (D1–D2: do not invent fake test commands here).

Build must obey `feature-mindset-contract.md`: **facetas + síntese + recode**,
not waterfall freeze.

## Autocontained Dependencies

- Use `feature-mindset-contract.md` for facets, strings-safadas, ready gates.
- Use `code-recon-protocol.md` for real terrain.
- Use `technical-blueprint-protocol.md` for file-level plan and contracts.
- Use `analyst-protocol.md` when the PRD or analysis is too thin.
- Use a grill pass before calling the blueprint ready.

## Required Phases

### 1. Confirm Input

Require one of:

- GitHub Issue with PRD;
- one or more analyses (`analysis.md`, `ANALYSIS-*.md`);
- `PRD.md`;
- clear user request explicitly asking for blueprint/spec.

When multiple analyses exist, read all of them. The blueprint/spec is the
single canonical synthesis and lists the sources it consumed.

If the input lacks product promise, entities, scope, or source truth, route back
to Analyst.

### 2. Recon Terrain

Run recon before architecture when the target is an existing system.
Use facet lenses (Backend payload, Frontend reuse scan, Copy inventory).

### 3. Facets — attention order, not freeze

SPEC must close **all** of these as facets of one synthesis (not three frozen
stages):

1. **Product** — promise, journey, surface, non-goals.
2. **Backend** — data model, actions/API, **payload shape**, permissions, cache,
   migrations if any — with path:line or UNPROVEN.
3. **Frontend** — shell/composition **discovered** in-repo; reuse|mode|new.
4. **Copy** — strings-safadas table (invariant | structure | death).

Order of writing may follow Product → Backend → Frontend → Copy for attention.
If Backend/Frontend/Copy evidence breaks Product, **recode** Product (and log it).

### 4. Synthesis + cross-facet

- Write **Synthesis** first (or immediately after inputs): one coherent
  paragraph (F4, H2).
- Fill **Cross-facet dependencies** (F7).
- Carry **Recode Log** from analysis and add Build recodes.

### 5. Architecture Diagrams

Use Mermaid when it clarifies. Mermaid only.

### 6. Blueprint body

Files/areas, sequence, validation strategy, risks, rollback, testable behavior
names for Plan (no fake commands).

### 7. Handoff

If ready:

- write `SPEC.md` (default; `technical_blueprint.md` legacy ok);
- update `status.json` with `phases.build = "complete"` and
  `artifacts.blueprint = "SPEC.md"`;
- route to `plan` when executable tasks are needed.

## Ready Gate (binary)

Build is **not** ready if:

- technical claims lack proof (`path:line` or UNPROVEN missing where required);
- Synthesis is missing or is a paste of three disconnected sections;
- a reusable pattern was not searched before `new`;
- Copy approves instance prose / mock literal without cartesian test;
- Cross-facet table missing on multi-facet work;
- validation is vague;
- PR scope too large without split;
- human product decision still unresolved;
- ready would be “headings filled” only (B1–B2);
- blueprint invents TDD commands (D1–D2).

## Proportionality

Docs-only: light Product + Copy; Backend/Frontend may skip with reason.
Deep existing-code: full facets + real recode log when synthesis shifted.
