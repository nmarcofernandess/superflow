---
name: audit
description: "Audit a Superflow request, PRD, GitHub issue, or local package without writing files. Use when the user asks for route, readiness, gaps, gap_count, phase budget, confidence, or whether analyst/build/plan can be skipped."
---

# Audit

Audit is read-only. It classifies route and readiness gaps without creating
issues, PRDs, or local specs.

## Procedure

1. Read `../../assets/references/routing-protocol.md`.
2. Use `../../scripts/superflow_audit.py`, not
   `superflow_taskgen.py --classify-only`, when gaps or `gap_count` are needed.
3. Report route, phase budget, confidence, gaps, and next actions.

## Commands

```bash
python3 <plugin-root>/scripts/superflow_audit.py \
  --format json \
  "implementar exportacao CSV para registros filtrados"
```

```bash
python3 <plugin-root>/scripts/superflow_taskgen.py \
  --classify-only \
  --json \
  "implementar exportacao CSV para registros filtrados"
```

Use the classifier-only command only for route/budget/confidence, never for
readiness gaps.

## Mermaid

Do not add diagrams to a tiny audit response. If the user asks for a workflow
view, use Mermaid only.
