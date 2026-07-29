# Superflow Plugin

Superflow is a Claude Code / Codex plugin that routes work by maturity, risk,
and intent instead of forcing every request through analyst -> build -> plan ->
execute.

The spine is:

```text
raw request -> classify -> route -> durable artifact -> optional build/plan -> execute or stop honestly
```

This README is the runtime guide. For the marketplace repository shape,
publication history, and design rationale, read `README.md`,
`SPEC-superflow-plugin.md`, and `WARLOG.md` in the repository root.

## Shape

```txt
superflow/
├── .codex-plugin/plugin.json
├── .claude-plugin/plugin.json
├── skills/
│   ├── superflow/SKILL.md
│   ├── capture/SKILL.md
│   ├── taskgen/SKILL.md
│   ├── analyst/SKILL.md
│   ├── build/SKILL.md
│   ├── plan/SKILL.md
│   ├── warlog/SKILL.md
│   ├── execute/SKILL.md
│   ├── qa/SKILL.md
│   └── audit/SKILL.md
├── assets/references/
├── assets/templates/
├── assets/examples/
└── scripts/
```

## Exported skills

- `superflow:superflow` routes and orchestrates phases.
- `superflow:capture` captures ideas into GitHub-ready PRD issues.
- `superflow:taskgen` creates or promotes local PRD packages.
- `superflow:analyst` handles product/domain/system ambiguity with native grill,
  faceted recon (Produto/Backend/Frontend/Copy), **Reuse Guard** (anti-fork
  via `.context` or grep — crystallize-guard slice), Síntese, Recode Log,
  strings-safadas, and blueprint handoff — see
  `assets/references/feature-mindset-contract.md` +
  `assets/references/reuse-guard-protocol.md`.
- `superflow:build` writes the technical blueprint/spec as a **synthesis** of
  those facets (not a freeze-waterfall of headings).
- `superflow:plan` writes executable `implementation_plan.json` task catalogs
  with TDD RED/GREEN pre-compile (`tdd-contract.md` I1).
- `superflow:warlog` maintains Mermaid-first WARLOGs.
- `superflow:execute` implements from durable artifacts under iron-law TDD (I2).
- `superflow:qa` closes acceptance matrix + RED/GREEN evidence (I3).
- `superflow:audit` performs read-only route/readiness/gap checks.

## Validate

```bash
python3 scripts/validate_superflow.py .
python3 scripts/test_superflow_routes.py
python3 scripts/test_tdd_contract.py
python3 scripts/test_feature_mindset.py
python3 scripts/forward_test_superflow.py
```

Use `--mermaid` on `validate_superflow.py` when you need render-level Mermaid
proof.

The validator intentionally fails if the Analyst contract is reduced to a thin
section checklist. Existing-code analysis must carry `Evidence Matrix`,
`Implementation Map`, `Entities And State`, `Blueprint Handoff`, and grill
verdicts.

The validator also fails generated packages whose PRD lacks `Story de Usuario`,
`Story Tecnica`, current/desired behavior, system contract, or definition of
complete. `status.json` is the phase GPS; detailed tasks live in
`implementation_plan.json` (with `tdd.red` / `tdd.green` on code tasks), and
execution evidence lives in `implementation_log.json` (red+green excerpts).
Canonical TDD rules: `assets/references/tdd-contract.md`.

## Marketplace Distribution

Superflow is distributed from its own marketplace repository:
`nmarcofernandess/superflow`.

Product repositories are consumers. They should not vendor `plugins/superflow`,
create repo-local marketplace entries, or copy/symlink this plugin into their
trees just to use it. Keep one source of truth: the marketplace repo.

Install in Codex:

```bash
codex plugin marketplace add nmarcofernandess/superflow --ref main
codex plugin add superflow@superflow
```

Refresh after updates:

```bash
codex plugin marketplace upgrade superflow
codex plugin add superflow@superflow
```

Start a new thread after installing or updating so the runtime reloads the
available skills list.

## Smoke

```bash
tmp=$(mktemp -d /tmp/superflow-plugin.XXXXXX)
python3 scripts/superflow_taskgen.py --root "$tmp" --mode local \
  "implementar exportacao CSV para admin com teste e sem alterar filtros"
python3 scripts/superflow_taskgen.py --mode issue \
  "ideia solta para melhorar onboarding"
python3 scripts/superflow_github.py create --dry-run --title "Ideia: onboarding" \
  --label sf:inbox "ideia solta para melhorar onboarding"
python3 scripts/superflow_github.py link 79 --local-package specs/001-slug --dry-run \
  --body-file assets/examples/capture-issue.md
python3 scripts/superflow_taskgen.py --classify-only --json \
  "implementar exportacao CSV para admin com teste e sem alterar filtros"
python3 scripts/superflow_audit.py --format markdown \
  "implementar exportacao CSV para admin com teste e sem alterar filtros"
python3 scripts/superflow_warlog.py specs/001-slug \
  --event "Plan complete; execution can start."
```
