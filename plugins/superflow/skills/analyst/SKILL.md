---
name: analyst
description: "Distill product, domain, workflow, and architecture ambiguity into a source-backed analysis artifact. Use when Superflow route is analyst_prd, when an issue/request needs product meaning before PRD/build, or when current-system truth must be proven before planning."
---

# Analyst

Analyst is the Superflow distillation phase. It does not code. It turns fuzzy
intent or a weak issue into an `analysis.md` that Build, Plan, or Taskgen can
trust.

This skill inherits the heavy Analyst standard: native grill, grounding,
entities/state, dumb-machine rules, Mermaid modeling, and blueprint handoff. A
short risk list is not Analyst.

## Required Reading

Read these completely before producing or updating analysis:

1. `../../assets/references/routing-protocol.md`
2. `../../assets/references/prd-contract.md`
3. `../../assets/references/analyst-protocol.md`
4. `../../assets/references/code-recon-protocol.md`
5. `../../assets/references/technical-blueprint-protocol.md`
6. `../../assets/references/mermaid-contract.md`
7. `../../assets/templates/analysis.md`

## Procedure

1. Classify the source: inline ask, GitHub issue, PRD, spec folder, or diff.
2. Run Phase 0 grill from `analyst-protocol.md`. Ask one precise question only
   when repo evidence cannot answer the ambiguity.
3. If code truth matters, run code recon before scope/verdict. Use actual repo
   files, `rg`, docs, schema, tests, and commands. Evidence must be cited as
   `path:line` or explicitly marked `UNPROVEN`.
4. Separate product promise, entities/state, rules, current behavior, and
   implementation terrain.
5. Produce or update `analysis.md` inside the local package. For inbox-only
   work, write the analysis into the GitHub issue body only if local artifact
   creation is not appropriate.
6. Include a blueprint handoff when the analysis can become implementation.
   High architecture risk should end as `ready for build`, not direct execute.
7. Run a final grill pass and record the verdict.
8. Update `status.json`: set `phases.analyst = "complete"` and
   `artifacts.analysis = "analysis.md"` when local.

## Mandatory Output

Local `analysis.md` must use the template headings from
`../../assets/templates/analysis.md`.

Mandatory for existing-system work:

- `Evidence Matrix` with concrete file evidence.
- `Implementation Map` in context -> backend -> services/hooks -> shells ->
  frontend -> tests order.
- `Entities And State` with source of truth and invalid states.
- `Runtime / Data Flow` with Mermaid when it reduces ambiguity.
- `Rules And Invariants` that a dumb machine can execute.
- `Blueprint Handoff` with files/areas, contracts, sequence, validation, and
  risks.
- `Grill Verdict` with one of the allowed verdicts from
  `analyst-protocol.md`.

## Ready Gate

Do not declare `ready for taskgen` or `ready for build` if any of these is true:

- source-backed evidence is missing for a technical claim;
- implementation map is absent for an existing codebase;
- entities/state/source-of-truth are vague;
- product promise is not tied to user-visible behavior;
- blueprint handoff is absent for architecture or implementation work;
- unresolved human decision changes the solution shape;
- the scope is really multiple slices and has not been split.

## Optional Acceleration

Explorer or architect subagents may help gather terrain or compare approaches,
but they are not dependencies and they do not replace the final artifact. The
analysis must contain the cited evidence and decisions itself.

## Mermaid

Use Mermaid for user flow, lifecycle, data flow, entity relation, or decision
trees when it reduces ambiguity. Follow
`../../assets/references/mermaid-contract.md`. No PlantUML.
