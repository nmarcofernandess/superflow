# Tribunal — Superflow 0.2.0 production reference

Date: 2026-07-29  
Branch: `feat/superflow-fatality-analyst-build` (ship-ready; `main` promotion is Marco-gated)  
Version: **0.2.0** (all plugin + marketplace manifests)  
Scope: fatality gates + Ready boundary (skills require package validator) + marketplace hygiene.  
Install pin: README primary Codex/Claude blocks use **`--ref v0.2.0`** (not `main`); main stays older until PR merge.

This file is a **repro log**, not a self-attestation. Every claim has command + exit-class + excerpt.

## Suite (must be green)

```bash
cd ~/superflow
./scripts/validate-all.sh
# includes:
#   python3 plugins/superflow/scripts/validate_superflow.py plugins/superflow
#   python3 plugins/superflow/scripts/test_feature_mindset.py
#   python3 plugins/superflow/scripts/test_tdd_contract.py
```

Expected: exit 0, lines `OK: superflow feature mindset tests` and `OK: …/plugins/superflow`.

## Fixtures that must PASS

```bash
python3 plugins/superflow/scripts/validate_superflow.py plugins/superflow/assets/fixtures/mindset/deep
python3 plugins/superflow/scripts/validate_superflow.py plugins/superflow/assets/fixtures/mindset/docs-only
python3 plugins/superflow/scripts/validate_superflow.py plugins/superflow/assets/fixtures/mindset/string-trap
```

Expected: three `OK:` lines.  
`docs-only` depth comes from `status.json` (`route=prd_execute`, `phase_budget=lean`, `workflow_type=docs_only`) — **not** from `mindset-depth.txt`.

## Fixture that must FAIL

```bash
python3 plugins/superflow/scripts/validate_superflow.py plugins/superflow/assets/fixtures/mindset/empty-headings-fail
# → FAIL: … Síntese empty or placeholder
```

## Exploit re-probe (Claude A–E) — all must FAIL (rc ≠ 0)

Validator: `plugins/superflow/scripts/validate_superflow.py`

### C — delete `status.json` (was silent OK)

```bash
cp -R plugins/superflow/assets/fixtures/mindset/empty-headings-fail /tmp/sf-c
rm /tmp/sf-c/status.json
python3 plugins/superflow/scripts/validate_superflow.py /tmp/sf-c
```

**Observed:**  
`FAIL: … partial package — analysis/SPEC present but missing status.json (never silent OK)`

### D — `echo docs > mindset-depth.txt` cannot downgrade deep status

```bash
cp -R plugins/superflow/assets/fixtures/mindset/deep /tmp/sf-d
echo docs > /tmp/sf-d/mindset-depth.txt
# hollow Product + skip_reason-only Recode (would pass if depth became docs)
# … then validate → FAIL on placeholder Product / deep recode rules
```

**Observed:**  
`FAIL: … ## Faceta — Produto empty/placeholder`  
(depth still deep from status; hatch ignored)

### A — hollow deep analysis (backtick-only backend, `new` without guard, fake recode)

```bash
# Backend: only `corretamente`  → FAIL path:line|UNPROVEN
# Frontend: Decision: new       → FAIL Reuse Guard table
# Recode: | T1 | achei que sim | … | mudei de ideia | → not counted as real
```

**Observed (first gate hit):**  
`FAIL: … Backend facet needs path:line (e.g. file.ts:12) or UNPROVEN — backticks alone do not count`

### B — four novel safada paraphrases (not fixture literals)

Rows with second-person / currency / geometry / count, destination `manter`:

**Observed:**  
`FAIL: … strings-safadas — instance-form prose in table row without invariante|estrutura|morte destination`

### E — SPEC facets `TBD` + empty Recode Log

**Observed:**  
`FAIL: … ### Product empty/placeholder (SPEC/Analyst parity)`

## Bonus — `coherence_proof` allows honest zero-recode deep

Documented in `test_feature_mindset.py` temp case `good-coherence`:  
replace Recode table with  
`coherence_proof: initial synthesis already matched …` (≥12 chars) → package PASS.

## Patches landed (map)

| # | Fix | Where |
|---|-----|--------|
| 1 | No silent return when analysis/SPEC present without PRD/status/progress | `validate_package` |
| 2 | Depth from `status.json` via `derive_mindset_depth`; `mindset-depth.txt` not authority | `derive_mindset_depth` + package |
| 3 | SPEC↔Analyst parity (`_is_placeholder_body` on `###` facets); recode ≥1 real **or** `skip_reason` (docs) **or** `coherence_proof` (deep) | `validate_spec_mindset` / `_require_recode_honest` |
| 4 | Backend `PATH_LINE_RE` or `UNPROVEN`; Frontend `new` requires guard table | `_require_backend_evidence` / `_require_frontend_decision` |
| 5 | Safada by form (currency/count/date/geometry/2nd person), tests with novel phrases | `_reject_strings_safadas_approved` + `test_feature_mindset.py` |
| Bônus | `coherence_proof:` | `_has_coherence_proof` |

## Honest residual (not claimed closed)

- Plugin markdown **marker** lists in `validate_superflow.py` are still doctrine spell-check (theater for plugin docs, not agent package content).
- `coverage.json` still self-declares `present` — useful inventory, not behavioral proof.
- Analyst/Build skills still do not auto-invoke the validator (human/CI must run it).

Those are out of the “Ready = heading filled” exploit class that Claude blocked merge on. This tribunal only claims **A–E closed with repro**.
