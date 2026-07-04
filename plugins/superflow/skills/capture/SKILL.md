---
name: capture
description: "Capture loose product ideas, braindumps, future work, or GitHub inbox requests into Superflow issue-shaped PRDs without creating local specs unless the user asks to promote. Use when the user asks for inbox, issue capture, braindump storage, GitHub issue body, or a lightweight PRD in an issue."
---

# Capture

Capture preserves ideas without pretending they are ready for implementation.

## Procedure

1. Read `../../assets/references/routing-protocol.md`.
2. Read `../../assets/references/github-issue-contract.md`.
3. Read `../../assets/references/prd-contract.md` if the issue needs PRD shape.
4. Use `../../scripts/superflow_taskgen.py --mode issue` to generate the body.
5. Use `../../scripts/superflow_github.py create` only when GitHub mutation is
   explicit.

## Output

- Loose idea: issue body with `sf:inbox`.
- Structured idea: issue body with PRD fields and confidence.
- No local `specs/NNN-*` folder unless the user explicitly asks to promote.

## Mermaid

If a diagram helps the issue explain lifecycle, dependency, or user flow, use
`../../assets/references/mermaid-contract.md`. Mermaid only.
