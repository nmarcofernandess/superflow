# Superflow

**Version `0.2.0`**. Agent Skills marketplace plugin for routing work by maturity
and risk.

```text
request → route → inbox/PRD → optional analyst → optional build → optional plan → execute → QA
```

Install from this Git marketplace (`nmarcofernandess/superflow`). Product repos
consume the plugin; they do not host a copy.

Codex and Claude Code are install surfaces. Source of truth:
`plugins/superflow/{skills,assets,scripts}`.

## What you get

| Layer | Contract | Enforcement |
|-------|----------|-------------|
| Routing | phase budget + route table | `routing-protocol.md`, `superflow` skill |
| Analyst / Build | faceted truth (Produto → Backend → Frontend → Copy), Recode Log, strings-safadas | `feature-mindset-contract.md` |
| Anti-fork | Reuse Guard before `new` | `reuse-guard-protocol.md` |
| Plan / Execute / QA | TDD iron laws I1–I3 | `tdd-contract.md` |
| **Ready boundary** | package must pass the shipped validator | `scripts/validate_superflow.py` |

Declaring Analyst or Build **ready** requires:

```bash
python3 <plugin-root>/scripts/validate_superflow.py <path-to-package>
```

Exit `0` only. Hollow headings, partial packages, fake Recode rows, instance
prose as UI copy, backtick-only backend “evidence”, and `new` without a Reuse
Guard table **fail**.

DietFlow-shaped paths may appear in fixtures/examples; the contracts are
portable.

## Install (Codex) — pin `v0.2.0`

Canonical ref: tag **`v0.2.0`**.  
`main` may still report an older plugin version. Do **not** use `--ref main`
until `main`’s `plugin.json` also says `0.2.0`.

```bash
codex plugin marketplace add nmarcofernandess/superflow --ref v0.2.0
codex plugin add superflow@superflow
```

Development tip (moving branch — prefer the tag):

```bash
codex plugin marketplace add nmarcofernandess/superflow --ref feat/superflow-fatality-analyst-build
codex plugin add superflow@superflow
```

After `main` carries `0.2.0`:

```bash
codex plugin marketplace add nmarcofernandess/superflow --ref main
codex plugin add superflow@superflow
```

Refresh:

```bash
codex plugin marketplace upgrade superflow
```

Start a new thread after install or update so skills reload.

## Install (Claude Code) — pin `v0.2.0`

Pin the tag. Unpinned marketplace add usually resolves `main` and will not
install `0.2.0` until that branch is updated.

```text
/plugin marketplace add nmarcofernandess/superflow@v0.2.0
/plugin install superflow@superflow
/reload-plugins
```

Shell:

```bash
claude plugin marketplace add nmarcofernandess/superflow --ref v0.2.0
claude plugin install superflow@superflow
```

Branch tip (prefer tag):

```bash
claude plugin marketplace add nmarcofernandess/superflow --ref feat/superflow-fatality-analyst-build
claude plugin install superflow@superflow
```

After merge, unpinned `main` is fine only when
`plugins/superflow/.claude-plugin/plugin.json` on `main` reports
`"version": "0.2.0"`.

## Repository shape

```text
.agents/plugins/marketplace.json      # Codex marketplace catalog (v0.2.0)
.claude-plugin/marketplace.json       # Claude Code marketplace catalog (v0.2.0)
plugins/superflow/
  .codex-plugin/plugin.json           # version 0.2.0
  .claude-plugin/plugin.json          # version 0.2.0
  skills/                             # portable Agent Skills
  assets/references/                  # contracts (mindset, TDD, reuse, …)
  assets/fixtures/mindset/            # golden + negative package fixtures
  scripts/validate_superflow.py       # package + plugin validator
  scripts/test_feature_mindset.py     # A–E exploit regression
  scripts/test_tdd_contract.py
```

**Do not** copy `plugins/superflow` into consumer apps. Install the marketplace
from Git.

## Skills (exported)

| Skill | Role |
|-------|------|
| `superflow` | Route + orchestrate |
| `capture` | Inbox / issue-shaped PRD |
| `taskgen` | Local `specs/NNN-*` package |
| `analyst` | Faceted analysis (`analysis.md`) |
| `build` | Technical SPEC / blueprint |
| `plan` | `implementation_plan.json` + TDD I1 |
| `execute` | Implementation + TDD I2 |
| `qa` | Acceptance + red+green I3 |
| `warlog` | Long-running Mermaid status |
| `audit` | No-write readiness/gaps |
| `backlog-status` | Issue vs merged PR truth |
| `html-didatico` | Visual HTML docs |

## Validate (maintainers / CI)

From this repo root:

```bash
./scripts/validate-all.sh
```

Must print OK for plugin root, routes, TDD, feature-mindset, and forward tests.

Package-level Ready (consumer work folder):

```bash
python3 plugins/superflow/scripts/validate_superflow.py path/to/specs/NNN-slug
```

Golden fixtures (must PASS):

```bash
python3 plugins/superflow/scripts/validate_superflow.py plugins/superflow/assets/fixtures/mindset/deep
python3 plugins/superflow/scripts/validate_superflow.py plugins/superflow/assets/fixtures/mindset/docs-only
python3 plugins/superflow/scripts/validate_superflow.py plugins/superflow/assets/fixtures/mindset/string-trap
```

Negative cases (must FAIL): `plugins/superflow/scripts/test_feature_mindset.py`
and the command log in `artifacts/proofs/superflow-fatality/tribunal.md`.

## Core contracts (read these)

- `plugins/superflow/assets/references/feature-mindset-contract.md`
- `plugins/superflow/assets/references/reuse-guard-protocol.md`
- `plugins/superflow/assets/references/tdd-contract.md`
- `plugins/superflow/assets/references/routing-protocol.md`
- `plugins/superflow/assets/references/execution-contract.md`

## Design rules

1. Agent Skills are portable; manifests are thin adapters.
2. Ready ≠ filled headings — Ready = validator green on the real package.
3. Analyst/Build hand off **behavior names**; Plan/Execute own test commands.
4. Prefer reuse/mode over `new`; document Reuse Guard when `new` is justified.
5. Mermaid only for diagrams.

## Version

All marketplace and plugin manifests ship **`0.2.0`** together. See
`CHANGELOG.md`.
