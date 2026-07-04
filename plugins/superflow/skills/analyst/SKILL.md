---
name: analyst
description: "Analyze product, domain, workflow, user pain, ambiguity, scope, and acceptance criteria before PRD hardening. Use when Superflow route is analyst_prd, when the user asks to think/analyze first, or when product rules are unclear enough that building now would be theater."
---

# Analyst

Analyst clarifies the product promise before build or execution. It does not
write production code.

## Procedure

1. Read `../../assets/references/routing-protocol.md`.
2. Read `../../assets/references/prd-contract.md`.
3. If code truth matters, inspect the repository before deciding scope.
4. Produce or update `analysis.md` inside the local package, or write the
   analysis directly into the GitHub issue if the work is still inbox-only.
5. Update `status.json`: set `phases.analyst` and
   `artifacts.analysis = "analysis.md"` when local.

## Required Analysis

- Product promise and target user.
- Pain and failed current workflow.
- Concrete examples.
- In scope / out of scope.
- Acceptance criteria that can be tested.
- Open questions and human decisions.
- Verdict: `ready for taskgen`, `ready for build`, `needs recon`,
  `needs human decision`, `split required`, or `capture only`.

## Mermaid

Use Mermaid for user flow, lifecycle, or decision trees when it reduces
ambiguity. Follow `../../assets/references/mermaid-contract.md`.
