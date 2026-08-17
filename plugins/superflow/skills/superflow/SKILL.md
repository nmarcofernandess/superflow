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
7. If maintaining a WARLOG, follow `../../assets/references/warlog-contract.md`
   (campaign board: sprints, budget, green contract — not a microtask diary).
8. If executing, follow `../../assets/references/execution-contract.md` and
   `../../assets/references/tdd-contract.md`, and keep `status.json` current.
   Code goes through `review` (`../../assets/references/review-contract.md`)
   between GREEN and QA: findings get verdicts, accepted blockers get proof.
9. Treat Build and Plan as different phases: Build writes the technical spec
   (`SPEC.md`; legacy `technical_blueprint.md` stays valid); Plan writes
   executable tasks in `implementation_plan.json` with TDD pre-compile (I1).
10. The phase executor owns its own status update. The router initializes and
    resumes from `status.json`; it does not mark a phase complete without the
    phase artifact and evidence.
11. **Ready boundary:** run
    `python3 <plugin-root>/scripts/validate_superflow.py <path-to-package>`
    on the real package directory before declaring Analyst, Build, or package
    **ready**. Exit 0 is required. Hollow headings, partial packages (missing
    `status.json`), fake Recode, and strings-safadas fail the gate. Analyst and
    Build skills restate this Ready Gate; do not skip it.
12. For human-facing prose, **REQUIRED SUB-SKILL:** Use
    `writing-clearly-and-concisely` before finalizing the artifact.
13. If the deliverable is a visual mural/one-pager for a non-technical reader
    (status wall, feature explainer, or a proof-final wireframe), use the
    `html-didatico` skill; use Direction C when a verification wireframe is
    filled into the proof in the same file.
14. If the work spans several `specs/NNN-*` packages, use the `campaign` skill
    and `../../assets/references/campaign-contract.md`: the motor computes
    what is actionable from the real packages and refuses `done` while any
    package is open. The WARLOG stays the narrative; it is not a second board.
15. If asked whether existing issues are truly resolved, use the
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
| `forensic` | analyst (investigation mode), build, plan, execute, review, qa | none |

Budget controls phases first. Model strength is secondary and can be chosen
inside each phase.

## Exported Skills

Superflow exposes the router and each major phase:

- `superflow`: route and orchestrate the smallest honest workflow.
- `capture`: GitHub inbox and issue-shaped PRD capture.
- `taskgen`: create or promote local PRD packages.
- `analyst`: product/domain ambiguity analysis before PRD hardening.
- `build`: technical blueprint/spec for risky or architectural work.
- `plan`: executable `implementation_plan.json` from PRD/blueprint with TDD
  RED/GREEN pre-compile.
- `warlog`: campaign board (sprints, deps, budget, green contract, Mermaid).
- `execute`: implementation from a durable Superflow source under iron-law TDD.
- `review`: spec review before Plan, code review after GREEN — findings with
  verdicts and re-verification in `review_log.json`.
- `campaign`: drive several packages to the end — computed next/blocked/done
  over the real packages, never done while one is open.
- `qa`: acceptance matrix and RED/GREEN proof closure.
- `audit`: no-write route/readiness/gap analysis.
- `html-didatico`: self-contained visual HTML docs with CSS dioramas —
  manuals, murals, and verification wireframes.
- `writing-clearly-and-concisely`: clear, direct human-facing prose for every
  phase and presentation artifact.
- `backlog-status`: verify whether existing GitHub issues are actually
  resolved against merged PRs and real code.

Standalone tools — call them with `/name`. They are not phases, they do not
write `status.json`, and no Superflow route requires them:

- `grill-me`: interview one question at a time until the design tree is
  resolved.
- `grill-with-docs`: the same grill, against `CONTEXT.md` / ADRs.
- `gauntlet-loop`: write a short prompt that loops a builder against a real
  bar until a blind critic picks ours.

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

Validate the **plugin root** (doctrine + manifests) or a **user package**:

```bash
# Plugin install integrity (CI / after pull)
python3 <plugin-root>/scripts/validate_superflow.py <plugin-root>
python3 <plugin-root>/scripts/test_feature_mindset.py
python3 <plugin-root>/scripts/test_tdd_contract.py
python3 <plugin-root>/scripts/test_superflow_routes.py
python3 <plugin-root>/scripts/forward_test_superflow.py

# Real work package (required before Analyst/Build ready)
python3 <plugin-root>/scripts/validate_superflow.py \
  path/to/specs/NNN-slug
```

Full tree gate from this marketplace repo: `./scripts/validate-all.sh`.

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
- Code tasks follow `tdd-contract.md`: plan pre-compiles RED/GREEN (I1),
  execute observes RED before production code (I2), QA maps PRD criteria to
  evidence including red+green (I3).
- Build is a technical blueprint, not a super PRD and not the final task list.
- Plan is the task list, not an architecture decision phase.
- Use `WARLOG.md` for product/plugin, forensic, deep, or multi-session work;
  keep it Mermaid-first for visual snapshots.
- Use Mermaid fenced blocks only for diagrams.
- For audit/gaps/readiness/gap_count requests, use `superflow_audit.py` and
  compute `gap_count` from `len(gaps)`.
- Mutate GitHub only when the user explicitly asks for issue creation/update or
  when the active workflow already requires it.
- Apply `writing-clearly-and-concisely` to human-facing prose. Preserve a warm,
  natural voice; clarity does not require corporate or bureaucratic language.

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
- Read `../../assets/references/tdd-contract.md` before planning or executing
  code tasks.
- Read `../../assets/references/feature-mindset-contract.md` before Analyst or
  Build (facetas, recode, strings-safadas, truth-seeking).
- Read `../../assets/references/reuse-guard-protocol.md` before creating UI or
  actions (anti-fork: .context Tier-2 or grep — crystallize-guard slice).
- Read `../../assets/references/backlog-status-protocol.md` before verifying
  existing issues against merged PRs.
