---
name: superflow
description: "Route product ideas, GitHub issues, PRDs, specs, and implementation requests through the minimum honest workflow: inbox, PRD, analyst, build/spec, plan, execute, and QA. Use when the user asks for superflow, taskgen, PRD/spec generation, issue-to-task promotion, phase-budget routing, or a flexible alternative to rigid analyst-build-plan-execute chains."
---

# Superflow

Use Superflow to decide which phases a request actually needs. Do not force a
fixed chain. Classify maturity and risk, then route to the smallest workflow that
can produce a durable artifact or a verified implementation.

## Core Loop

1. Inspect the input source: inline request, file, GitHub issue, existing PRD, or
   existing `specs/NNN-*` folder.
2. Read `../../assets/references/routing-protocol.md` and choose a route.
3. If creating or promoting work, use `../../scripts/superflow_taskgen.py` unless the
   repository has a stronger local task generator.
4. If the user asks to audit, review readiness, find gaps, or return
   `gap_count`, use `../../scripts/superflow_audit.py`. Do not substitute
   `--classify-only`; classification has no gap model.
5. If generating diagrams, follow `../../assets/references/mermaid-contract.md`; Mermaid only.
6. If writing a PRD or issue body, follow `../../assets/references/prd-contract.md` and
   `../../assets/references/github-issue-contract.md`.
7. If maintaining a WARLOG, follow `../../assets/references/warlog-contract.md`.
8. If executing, follow `../../assets/references/execution-contract.md` and keep
   `status.json` current.
9. Treat Build and Plan as different phases: Build writes the technical spec
   (`SPEC.md`; legacy `technical_blueprint.md` stays valid); Plan writes
   executable tasks in `implementation_plan.json`.
10. The phase executor owns its own status update. The router initializes and
    resumes from `status.json`; it does not mark a phase complete without the
    phase artifact and evidence.
11. Validate the package with `../../scripts/validate_superflow.py` before declaring it
   ready.
12. If the deliverable is a visual mural/one-pager for a non-technical reader
    (status wall, feature explainer, or a proof-final wireframe), use the
    `html-didatico` skill; use Direction C when a verification wireframe is
    filled into the proof in the same file.
13. If asked whether existing issues are truly resolved, use the
    `backlog-status` skill to reconcile each issue against merged PRs and real
    code; this is not `audit`, which scores one forward request.

## Route Table

| Route | Use when | Output |
|-------|----------|--------|
| `inbox_only` | Loose braindump, future idea, no decision to think now | GitHub issue body |
| `inbox_prd` | Loose idea deserves structure but not local work yet | GitHub issue body with PRD shape |
| `local_prd` | User asks taskgen/local spec or scope is mature | `specs/NNN-slug/PRD.md` |
| `prd_execute` | Clear scope, low risk, direct implementation | PRD package, then execute |
| `prd_plan_execute` | Clear scope but sequencing matters | PRD package, `implementation_plan.json`, execute |
| `analyst_prd` | Product/domain/rule ambiguity dominates | Analyst artifact, then PRD |
| `build_plan_execute` | Technical risk, architecture, migration, cross-module work | `SPEC.md`, `implementation_plan.json`, execute |
| `investigate_first` | Bug or unknown behavior lacks proven cause | Analyst in investigation mode, then route again |

## Phase Budget

| Budget | Required phases | Default skip |
|--------|-----------------|--------------|
| `capture` | inbox | analyst, build, plan, execute |
| `lean` | taskgen, execute, qa | analyst, build, plan |
| `standard` | taskgen, plan, execute, qa | analyst, build |
| `deep` | analyst, taskgen, build, plan, execute, qa | none |
| `forensic` | analyst (investigation mode), build, critic, plan, execute, qa | none |

Budget controls phases first. Model strength is secondary and can be chosen
inside each phase.

## Exported Skills

Superflow exposes the router and each major phase:

- `superflow`: route and orchestrate the smallest honest workflow.
- `capture`: GitHub inbox and issue-shaped PRD capture.
- `taskgen`: create or promote local PRD packages.
- `analyst`: product/domain ambiguity analysis before PRD hardening.
- `build`: technical blueprint/spec for risky or architectural work.
- `plan`: executable `implementation_plan.json` from PRD/blueprint.
- `warlog`: long-running Mermaid WARLOG creation and updates.
- `execute`: implementation from a durable Superflow source.
- `qa`: acceptance and proof closure.
- `audit`: no-write route/readiness/gap analysis.
- `html-didatico`: self-contained visual HTML docs with CSS dioramas —
  manuals, murals, and verification wireframes.
- `backlog-status`: verify whether existing GitHub issues are actually
  resolved against merged PRs and real code.

## Commands

Create a local PRD package:

```bash
python3 <plugin-root>/scripts/superflow_taskgen.py \
  --root "$PWD" \
  --mode local \
  "implementar exportacao CSV para registros filtrados"
```

Create an issue-ready PRD body without writing repo files:

```bash
python3 <plugin-root>/scripts/superflow_taskgen.py \
  --mode issue \
  "ideia solta para melhorar onboarding"
```

Audit route without writing files:

```bash
python3 <plugin-root>/scripts/superflow_taskgen.py \
  --classify-only \
  --json \
  "implementar exportacao CSV para registros filtrados"
```

Audit readiness/gaps without writing files:

```bash
python3 <plugin-root>/scripts/superflow_audit.py \
  --format json \
  "implementar exportacao CSV para registros filtrados"
```

Promote a saved GitHub issue body to a local package:

```bash
python3 <plugin-root>/scripts/superflow_taskgen.py \
  --root "$PWD" \
  --from-file issue-79.md \
  --promote-issue 79
```

Create or promote through `gh` when explicit GitHub mutation is desired:

```bash
python3 <plugin-root>/scripts/superflow_github.py \
  create \
  --title "Ideia: onboarding" \
  --label sf:inbox \
  "ideia solta para melhorar onboarding"

python3 <plugin-root>/scripts/superflow_github.py \
  promote 79 --root "$PWD"

python3 <plugin-root>/scripts/superflow_github.py \
  link 79 --local-package specs/001-slug
```

Create or update a Mermaid WARLOG for a local package:

```bash
python3 <plugin-root>/scripts/superflow_warlog.py \
  specs/001-slug \
  --event "Build approved; execution can start."
```

Validate a Superflow skill/package:

```bash
python3 <plugin-root>/scripts/validate_superflow.py \
  <plugin-root> --mermaid
python3 <plugin-root>/scripts/test_superflow_routes.py
python3 <plugin-root>/scripts/forward_test_superflow.py
```

## Non-Negotiables

- Do not create a local `specs/NNN-*` folder for every thought. Create it when
  the user asks for local taskgen or when the PRD is mature enough to act on.
- A scaffolded PRD is born `gathering`. Only the skill that wrote or reviewed
  the PRD content promotes it to `ready`; scripts never do. Do not run
  execute phases while the PRD is `gathering`.
- Use the same PRD layout in GitHub issues and local files. A shallow idea is a
  low-confidence PRD, not a different artifact species.
- Skip `analyst` when the product logic is already clear.
- Skip `build` when there is no technical architecture risk.
- Skip `plan` when execution is obvious and acceptance criteria are testable.
- Never skip QA for implementation.
- Keep `status.json` machine-readable and `progress.md` human-readable.
- Keep executable tasks in `implementation_plan.json`, not `status.json`.
- Keep execution evidence in `implementation_log.json`; do not rewrite the plan
  as a progress log.
- Build is a technical blueprint, not a super PRD and not the final task list.
- Plan is the task list, not an architecture decision phase.
- Use `WARLOG.md` for product/plugin, forensic, deep, or multi-session work;
  keep it Mermaid-first for visual snapshots.
- Use Mermaid fenced blocks only for diagrams.
- For audit/gaps/readiness/gap_count requests, use `superflow_audit.py` and
  compute `gap_count` from `len(gaps)`.
- Mutate GitHub only when the user explicitly asks for issue creation/update or
  when the active workflow already requires it.

## Reference Loading

- Read `../../assets/references/routing-protocol.md` for every route decision.
- Read `../../assets/references/prd-contract.md` before writing PRD content.
- Read `../../assets/references/github-issue-contract.md` before creating or updating issue
  bodies.
- Read `../../assets/references/warlog-contract.md` before creating or updating
  `WARLOG.md`.
- Read `../../assets/references/status-schema.md` before editing `status.json`.
- Read `../../assets/references/execution-contract.md` before executing from a Superflow
  package.
- Read `../../assets/references/backlog-status-protocol.md` before verifying
  existing issues against merged PRs.
