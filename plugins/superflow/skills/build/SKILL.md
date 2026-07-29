---
name: build
description: "Create the Superflow technical blueprint/spec for architecture, schema, migration, API, auth, shared primitive, cross-module, or high-risk implementation work. Use when route is build_plan_execute, when analyst output is ready for architecture, or when a mature PRD still needs file-level contracts before plan/execution."
---

# Build

Build turns a mature PRD or one or more analyses into an implementation-safe
technical spec. It is not brainstorm and not Plan.

Build closes architecture, contracts, boundaries, risks, and validation
strategy under **feature-mindset-contract.md** (facetas + Synthesis + Recode +
Copy). Plan later owns executable tasks and TDD pre-compile (`tdd-contract.md`).

## Required Reading

1. `../../assets/references/execution-contract.md`
2. `../../assets/references/status-schema.md`
3. `../../assets/references/feature-mindset-contract.md`
4. `../../assets/references/reuse-guard-protocol.md`
5. `../../assets/references/build-protocol.md`
6. `../../assets/references/code-recon-protocol.md`
7. `../../assets/references/technical-blueprint-protocol.md`
8. `../../assets/references/mermaid-contract.md`
9. `../../assets/templates/SPEC.md`

## Procedure

1. Confirm mature input (PRD, analyses, or explicit blueprint ask).
2. If promise/entities/evidence weak → route to `analyst`.
3. Read ALL analyses; Build is the single canonical synthesis listing sources.
4. Recon real files (payload, **Reuse Guard**, copy) before boundaries —
   re-run guard if analysis has `new` without evidence.
5. Close **facets** Product, Backend, Frontend, Copy — attention order may be
   P→B→F→Copy; if evidence breaks an earlier facet, **recode** and log it.
   Do not freeze waterfall stages.
6. Write **Synthesis** first (binding paragraph).
7. Fill Cross-facet dependencies + Recode Log + Copy contract table.
8. Write `SPEC.md` (default; legacy `technical_blueprint.md` ok).
9. List testable **behaviors** for Plan — **no fake test commands** (D1–D2).
10. Grill; update `status.json` build complete + blueprint artifact.
11. Leave granular tasks to Plan.

## Required Blueprint

- Synthesis (H2)
- Goal and product promise
- Terrain with evidence (path:line|UNPROVEN)
- Files and ownership boundaries
- Facets Product / Backend / Frontend / Copy
- Cross-facet dependencies
- Recode Log
- Reuse decisions vs new code
- Testable behaviors (names only)
- Implementation sequence (dependency order)
- Verification strategy + risks + rollback
- Coherence check (ready ≠ headings)

## Ready Gate

Build is not ready if:

- technical claims lack source proof;
- Synthesis missing or is section-collage;
- local patterns not searched before `new` (Reuse Guard missing);
- Copy approves safada instance prose;
- Cross-facet table missing when multiple facets change;
- sequence not dependency-ordered;
- validation vague;
- human decision can still change architecture;
- slice too large without split;
- blueprint tracks task progress instead of architecture;
- ready would only mean filled headings;
- invents TDD commands (belongs to Plan + tdd-contract).

## Mermaid

Architecture flow, sequence, ER, dependency graph. Mermaid only.
