---
name: analyst
description: "Distill product, domain, workflow, and architecture ambiguity into a source-backed analysis artifact. Use when Superflow route is analyst_prd, when an issue/request needs product meaning before PRD/build, or when current-system truth must be proven before planning."
---

# Analyst

Analyst is the Superflow distillation phase. It does not code. It turns fuzzy
intent or a weak issue into an `analysis.md` that Build, Plan, or Taskgen can
trust.

Heavy standard: native grill, grounding, entities/state, dumb-machine rules,
Mermaid, blueprint handoff — plus **feature-mindset**: facetas (not waterfall),
síntese, Recode Log, strings-safadas, path:line|UNPROVEN, reuse-before-new.

## Required Reading

Read completely before producing or updating analysis:

1. `../../assets/references/routing-protocol.md`
2. `../../assets/references/prd-contract.md`
3. `../../assets/references/feature-mindset-contract.md`
4. `../../assets/references/reuse-guard-protocol.md`
5. `../../assets/references/analyst-protocol.md`
6. `../../assets/references/code-recon-protocol.md`
7. `../../assets/references/technical-blueprint-protocol.md`
8. `../../assets/references/mermaid-contract.md`
9. `../../assets/templates/analysis.md`

## Investigation Mode

No separate Discovery phase. Bugs/unknowns without proven cause: reproduce,
read logs/tests/code, prove or `UNPROVEN`, then route.

## Multiple Analyses, One Active Synthesis

Default one `analysis.md`. Extra lenses: `ANALYSIS-<lens>.md`. Status points at
the active analysis. Build synthesizes the canonical SPEC from all analyses.

## Procedure

1. Classify source (inline, issue, PRD, package, diff).
2. Phase 0 grill (`analyst-protocol.md`).
3. Faceted recon (`code-recon-protocol.md`) before technical conclusions —
   attention order often P→B→F→Copy; **never freeze** when later evidence
   contradicts; append Recode Log and rewrite the set.
4. **Reuse Guard** (`reuse-guard-protocol.md`) for each UI/code need before
   closing Frontend/Backend with `new` — graph Tier-2 if fresh, else grep;
   table need → source → reuse|mode|new → path. Run **before** final Síntese.
5. Write four facets (or proportional skip_reason): Produto, Backend
   (payload + path:line|UNPROVEN), Frontend (guard + reuse|mode|new), Copy
   (invariante|estrutura|morte).
6. Write **Síntese** that binds facets (not a paste of three sections).
7. Maintain **Recode Log** (deep: real entries when synthesis moves; docs-only:
   skip_reason ok).
8. Stories de Usuario e Técnica; entities; implementation map.
9. Blueprint handoff with testable **behavior names** only — no fake test
   commands (`tdd-contract.md` owns RED/GREEN later).
10. Grill verdict; update `status.json` (`phases.analyst`, `artifacts.analysis`).
11. **Run the package validator** on the package directory (see Ready Gate).
    Non-zero exit = not ready. Do not skip this step.

## Mandatory Output

Use template headings from `../../assets/templates/analysis.md`.

Mandatory for existing-system / UI work:

- TL;DR + **Síntese** near the top
- **Faceta — Produto / Backend / Frontend / Copy**
- **Recode Log**
- Evidence Matrix with `path:line` or UNPROVEN
- Implementation Map with reuse decisions
- Blueprint Handoff + Grill Verdict

## Ready Gate

**Package validator is mandatory.** Before declaring `ready for taskgen` or
`ready for build`, run the shipped validator on the **real package path**
(the folder that contains `analysis.md` / `status.json` / `PRD.md`):

```bash
python3 <plugin-root>/scripts/validate_superflow.py <path-to-package>
```

- Exit code **must be 0**. Non-zero means **not ready** — fix the package and
  re-run until green.
- Filled headings alone are never ready. The validator rejects hollow
  synthesis, fake Recode, instance-prose Copy, backtick-only Backend, and
  `new` without Reuse Guard table.
- Depth is derived from `status.json` (`phase_budget` / `route` /
  `workflow_type`), not from agent-written depth markers.

Do not declare ready if any of the following hold (even if the validator was
not run — run it anyway):

- package validator not run or exit ≠ 0;
- source-backed evidence missing for a technical claim;
- Synthesis missing or is heading-collage only;
- implementation map absent for existing codebase;
- `new` UI/code without Reuse Guard (graph or grep) evidence;
- Copy still approves instance/mock prose as system copy;
- Recode Log dishonest for depth (fake N/A on deep without `coherence_proof`);
- product promise needs data that is UNPROVEN without non-goal;
- ready would only mean “sections filled”;
- TDD commands invented in handoff (behavior names only — `tdd-contract.md`
  owns RED/GREEN in Plan/Execute).

## Mermaid

Use Mermaid when it reduces ambiguity. Follow
`../../assets/references/mermaid-contract.md`. Mermaid only.
