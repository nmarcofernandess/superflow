# Changelog

## 0.3.0 — 2026-08-14

### One line of truth

- Merges the clear-writing skill (`writing-clearly-and-concisely`, shipped on
  `main` as 0.1.1) into the 0.2.x contract line. `validate-all.sh` runs every
  test suite; the router keeps both the Ready boundary and the writing
  sub-skill step.

### Gates read meaning, not markdown shape

- **strings-safadas is scoped to the Copy facet** (`## Faceta — Copy`, SPEC
  `### Copy`) and reads **prose and tables alike** inside it. A sprint date, a
  geometry word in a schema note, or a number in evidence no longer fails a
  package; the contract's own anti-example no longer passes just by living
  outside a table. Outside the facet, only text claiming to BE approved copy is
  judged. `morta` counts as `morte`; a denied claim ("**não** aprovada como UI
  copy") is not a claim.
- **`new` always needs the Reuse Guard table.** Declaring `new` in prose counts
  as `new`, and writing `reuse` elsewhere in the section no longer stands the
  gate down.
- **Placeholder detection lost its magic number.** A facet whose body is only a
  table header (or rows with no content) is a placeholder — decided by parsing
  rows, not by looking for the literals `path`, `high`, and `88`.

### Proof

- Six cases in `test_feature_mindset.py`
  (`assert_safada_scope_and_decision_gates`): schedule table PASS, schema note
  PASS, Copy prose FAIL, prose `new` FAIL, header-only table FAIL,
  one-real-row PASS.
- Re-probed with phrases that appear in no fixture and no test.

## 0.2.1 — 2026-07-29

### WARLOG campaign board

- Official WARLOG absorbs Warlog Minimal DNA: mission, WBS/deps, sprints,
  chronology, next action — Mermaid only.
- Sprint cards: state, deps, budget (`direct|plan|spec`), green contract,
  artifacts, next action.
- Package gate: if `WARLOG.md` exists, diary-only / PlantUML fail.
- Fixture `assets/fixtures/warlog/campaign` + `test_warlog_contract.py`.
- Root `WARLOG.md` rewritten as real campaign board (not publish checklist).
- `warlog-minimal` command deprecated for Superflow packages (pointer only).

## 0.2.0 — 2026-07-29

### Ready boundary

- Analyst and Build Ready Gates require
  `scripts/validate_superflow.py <package>` with exit 0.
- Superflow router documents the same gate.
- Tests assert skills name the validator and package path.

### Feature mindset (Analyst / Build)

- Faceted contract: Produto / Backend / Frontend / Copy, Síntese, Recode Log.
- Strings-safadas: form-based rejection (currency, counts, geometry, 2nd person).
- Backend: `path:line` or `UNPROVEN` (backticks alone fail).
- Frontend `new` requires Reuse Guard table (Need | Source | Decision | path).
- Depth from `status.json` (`phase_budget` / `route` / `workflow_type`).
- Partial packages (analysis/SPEC without status/PRD/progress) fail.
- `coherence_proof:` allowed when the first synthesis already matches terrain.

### Reuse Guard

- Read-only slice of crystallize-guard (Tier-2 `.context` or grep).
- Spec: `assets/references/reuse-guard-protocol.md`.

### TDD (Plan / Execute / QA)

- I1–I3 in `tdd-contract.md`.
- Analyst/Build hand off behavior names only; no invented test commands.

### Packaging

- Version **`0.2.0`** on Claude/Codex plugin manifests and marketplace catalogs.
- Install pin: tag `v0.2.0` (see README).
- Command repro: `artifacts/proofs/superflow-fatality/tribunal.md`.

### Limits

- Plugin markdown marker lists check doctrine files, not user packages.
- `coverage.json` is an inventory (`present`), not a semantic proof engine.
- Skills require agents to run the validator; they do not install OS hooks.

## 0.1.x

Pre-0.2.0 work (TDD contract, mindset gates) lived on
`feat/superflow-fatality-analyst-build` with interim versions such as
`0.1.3+reuse-guard.20260729`.
