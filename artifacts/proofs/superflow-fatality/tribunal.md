# Tribunal — Superflow 0.2.0 (command repro)

Date: 2026-07-29  
Branch: `feat/superflow-fatality-analyst-build`  
Version: **0.2.0**  
Scope: package validator Ready gates; install pin `v0.2.0`.  

Command log with exit class and FAIL/OK excerpts. Not a self-approval scorecard.

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

## Out of scope for this log

- Plugin markdown marker lists (doctrine file integrity, not user packages).
- `coverage.json` inventory (`present`), not a semantic proof engine.
- OS-level hooks that force the validator without agent/CI action.

This log claims only what the commands above show: A–E fail; golden fixtures pass.

---

# Tribunal — Superflow 0.3.0 (scope repro)

Date: 2026-08-14  
Version: **0.3.0**  
Scope: gates judge meaning, not markdown shape; `main` and the contract line
merged into one release.

## Suite

```bash
cd ~/superflow
./scripts/validate-all.sh
```

Observed: exit 0, with `OK: superflow feature mindset tests` and
`OK: Superflow writing contract` in the same run.

## What was wrong in 0.2.1

The safada gate scanned every line starting with `|` in the whole document, so
markdown shape decided guilt:

| Probe | 0.2.1 | 0.3.0 |
|---|---|---|
| `\| S1 \| 12/08/2026 \| motor de busca \|` (sprint table) | FAIL | PASS |
| `\| Schema \| conforme a tabela acima… \|` (schema note) | FAIL | PASS |
| `"Continua Retorno por R$ 180,00, como foi combinado."` in Copy **prose** | PASS | FAIL |
| Decision `new` in prose, no guard table | PASS | FAIL |
| Facet body = table header only | PASS | FAIL |

The third row is the contract's own anti-example. It survived the validator by
not being inside a table.

## Fixed gates

| # | Fix | Where |
|---|-----|-------|
| 1 | safada scoped to the Copy facet; prose and rows read alike; approval claims still judged anywhere | `_copy_scopes` / `_iter_decision_blocks` / `_reject_strings_safadas_approved` |
| 2 | `morta` accepted as `morte`; denied claim is not a claim | `_DEST_OK_RE` / `_APPROVAL_CLAIM_RE` |
| 3 | declared `new` always requires the guard table (prose included) | `_NEW_DECISION_RE` / `_declares_new_decision` |
| 4 | placeholder table detected by parsing rows, not by the literals `path`/`high`/`88` | `_is_placeholder_body` |

## Re-probe with unseen data

Phrases below appear in no fixture and no test — varying the data, not only the
path:

```bash
# PASS: "| Beta fechado | 03-09-2027 | squad de dados |" appended outside Copy
# PASS: "| unidade | o seletor fica a direita do input, ao lado do rotulo |"
# FAIL: Copy prose "Voce ainda tem 4 consultas neste plano, aproveite…"
# FAIL: "| Picker de categoria | new |" with no guard columns
# PASS: same need with a full Need|Guard source|Decision|Evidence path table
```

Observed: PASS, PASS, FAIL, FAIL, PASS.

## Still out of scope

- Safada detection is form-based and PT-BR-shaped (`consultas|pacientes|dias…`,
  `acima|à direita`). An English package gets weaker coverage.
- `coverage.json` remains an inventory, not a semantic proof engine.
- No OS hook forces the validator; skills instruct, agents run.

---

# Tribunal — Superflow 0.4.0 (review phase)

Date: 2026-08-14  
Version: **0.4.0**  
Scope: the `critic` slot becomes the `review` phase, with artifact and gate.

## What was missing in 0.3.0

`status.json` shipped `"critic": "skipped"` in every package. `plan` could
classify a task owner as `reviewer`. Neither had a skill, an artifact, or a
gate — the vocabulary existed, the motor did not.

```bash
grep -rn "critic" plugins/superflow --include="*.md" --include="*.py"
# → status-schema.md, taskgen generator, one route-table cell. No contract.
grep -rn "reviewer" plugins/superflow --include="*.md"
# → skills/plan/SKILL.md:47, a word in a list.
```

## Suite

```bash
cd ~/superflow
./scripts/validate-all.sh
```

Observed: exit 0, 8 `OK` lines including `OK: superflow review contract tests`.

## Gates (each observed RED before the code existed)

| Probe | Expected |
|---|---|
| finding left `pending` while QA is complete | FAIL |
| `rejected` with empty reason | FAIL |
| reason = "Boa observação, você tem razão!" | FAIL |
| accepted `blocker` without proof | FAIL |
| proof = `{"ok": true}` with no command/excerpt | FAIL |
| round with `findings: []` and no `no_findings_reason` | FAIL |
| round with `findings: []` and a signed reason | PASS |
| shipped code, QA complete, no `review_log.json` | FAIL |

## Re-probe with unseen data

```bash
# FAIL: reason "Faz sentido, valeu! Perfeito."
# PASS: reason "Concordo que o formatter roda a cada render, mas o drawer monta
#       sob demanda e o array de deps custa mais manutencao do que o ganho medido"
# FAIL: accepted major with task_id but no proof
# PASS: workflow_type docs_only with no review_log at all
```

Observed: FAIL, PASS, FAIL, PASS.

The second row is the one that matters: agreement is refused by measuring what
survives after the agreement phrases are stripped, so a real argument that
happens to open with "concordo" is not punished for politeness.

## Still out of scope

- Nothing forces a *different* agent to be the reviewer; the contract says it,
  the validator cannot see it.
- Review quality is not measured — an honest empty round is accepted on its
  signed reason.
- No multi-package campaign motor: review closes one package, not a queue.

---

# Tribunal — Superflow 0.5.0 (campaign motor)

Date: 2026-08-15  
Version: **0.5.0**  
Scope: several packages driven to the end; `done` becomes a computed verdict.

## What was missing in 0.4.0

The WARLOG carried mission, sprint cards, dependencies and a next action — for
a human to read. Nothing read the real packages. A campaign could be declared
finished by whoever got tired first.

## Design decision (Reuse Guard)

The WARLOG contract forbids "two parallel warlog systems". So the motor does
**not** introduce a campaign file. A package joins with `campaign` and
`depends_on` in its own `status.json`; the motor derives the graph. Nothing is
duplicated, so nothing can drift.

## Suite

```bash
cd ~/superflow
./scripts/validate-all.sh
```

Observed: exit 0, 9 `OK` lines including `OK: superflow campaign contract tests`.

## Gates (each observed RED before the motor existed)

| Probe | Expected |
|---|---|
| fixture campaign, 001 closed | exit 10, next = `002-consumer` |
| every package closed | exit 0, verdict `done` |
| one package still open | never `done` |
| dependency cycle | exit 1, cycle named |
| `depends_on` pointing nowhere | exit 1 |
| `qa: complete` on a package the validator refuses | exit 1, names the validator |
| phase `blocked` with no `blocked_reason` | exit 1 |
| phase `blocked` with a signed reason | exit 20, blockers listed |
| `--campaign` scope | foreign packages excluded |

## Re-probe with an unseen graph

A diamond built from scratch (`010-schema` → `011-api` + `012-ui` →
`013-release`), plus one package belonging to another campaign:

```text
D1  010 closed          → exit 10, next 011-api, 013 waiting on both parents
D2  011 and 012 closed  → exit 10, next 013-release
D3  013 closed          → exit 0, DONE
D4  no --campaign       → exit 10, the foreign package keeps the scope open
D5  foreign package "qa complete" with PRD.md deleted → exit 1, validator refuses
```

Observed: as above. D5 also exposed a validator bug fixed in this release —
a package with `status.json` and no `progress.md`/`PRD.md` used to return a
silent OK.

## Still out of scope

- The motor names the next package; it does not execute phases and never writes
  another package's `status.json`.
- Order comes from dependencies only. Priority and value stay human, in the
  WARLOG.
- Nothing enforces that a *different* agent works each package.
