# Changelog

## 0.2.0 — 2026-07-29

Production reference cut for the Superflow Agent Skills marketplace.

### Ready boundary

- Analyst and Build **Ready Gates** require running
  `scripts/validate_superflow.py` on the **real package path** (exit 0).
- Superflow router skill documents the same boundary.
- Automated checks assert skills name `validate_superflow.py` + package path.

### Feature mindset (Analyst / Build)

- Faceted truth contract: Produto / Backend / Frontend / Copy, Síntese, Recode Log.
- Strings-safadas: form-based rejection (currency, counts, geometry, 2nd person).
- Backend evidence: `path:line` or `UNPROVEN` (backticks alone do not count).
- Frontend `new` requires Reuse Guard table (Need | Source | Decision | path).
- Depth from `status.json` (`phase_budget` / `route` / `workflow_type`).
- Partial packages (analysis/SPEC without status/PRD/progress) fail — never silent OK.
- `coherence_proof:` allowed as honest alternative to inventing a Recode row.

### Reuse Guard

- Crystallize-guard **slice** only (Tier-2 `.context` or grep); no map/mine/apply campaign.
- Ported as `assets/references/reuse-guard-protocol.md`.

### TDD (Plan / Execute / QA)

- Contract I1–I3 unchanged as production law (`tdd-contract.md`).
- Analyst/Build must not invent test commands (behavior names only).

### Packaging

- Single version **`0.2.0`** across Claude/Codex plugin manifests and marketplace catalogs.
- README is the install contract for third parties.
- Tribunal/proof log: `artifacts/proofs/superflow-fatality/tribunal.md` (command + FAIL lines).

### Residual (explicit, non-blocking)

- Plugin markdown marker lists remain doctrine integrity checks, not package semantics.
- `coverage.json` inventory may self-report `present`.
- Skills instruct agents to run the validator; they do not inject OS-level tool hooks.

## 0.1.x

Earlier fatality and TDD work landed on `feat/superflow-fatality-analyst-build`
before the `0.2.0` production alignment (versions such as
`0.1.3+reuse-guard.20260729`).
