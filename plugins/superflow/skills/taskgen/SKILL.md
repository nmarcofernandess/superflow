---
name: taskgen
description: "Create or promote Superflow PRD packages from inline ideas, files, or GitHub issue bodies. Use when the user asks for taskgen, local PRD/spec folder creation, issue promotion, specs/NNN structure, or turning a mature request into a durable local work package."
---

# Taskgen

Taskgen creates the durable local source of truth when the work is mature enough
to think or execute.

## Procedure

1. Read `../../assets/references/routing-protocol.md`.
2. Read `../../assets/references/prd-contract.md`.
3. Run `../../scripts/superflow_taskgen.py` for creation or promotion.
4. Validate the generated folder with `../../scripts/validate_superflow.py`.

## Commands

```bash
python3 <plugin-root>/scripts/superflow_taskgen.py \
  --root "$PWD" \
  --mode local \
  "implementar exportacao CSV para registros filtrados"
```

```bash
python3 <plugin-root>/scripts/superflow_taskgen.py \
  --root "$PWD" \
  --from-file issue-79.md \
  --promote-issue 79
```

## Output

- `specs/NNN-slug/PRD.md`
- `specs/NNN-slug/progress.md`
- `specs/NNN-slug/status.json`
- Optional `WARLOG.md` only for deep, forensic, plugin, workflow, or
  multi-session work.

## PRD Contract

Generated PRDs must include `TL;DR`, `Story de Usuario`, `Story Tecnica`,
current vs desired behavior, system pattern/contract, acceptance criteria, and
definition of complete. A shallow idea can have low confidence, but it still
uses the same shape as a mature PRD.

The TL;DR is not a first-draft shortcut. **REQUIRED SUB-SKILL:** after completing
and rereading the PRD, use `explain-clearly` in TL;DR mode. It must reconstruct
the subject from evidence, not copyedit the PRD's abstractions. Then use
`writing-clearly-and-concisely` for the final prose.

Run the reasonable-objection and closed-book paraphrase gates before promotion.
A generated `gathering` package may keep the explicit placeholder, but a PRD
cannot become `ready` until that placeholder is replaced with a causal,
standalone summary.

## PRD Gate

Every scaffolded package is born with `decision.prd_status = "gathering"`. The
script only scaffolds; it never promotes. Promotion to `ready` is this skill's
act after reviewing and filling the PRD content against
`../../assets/references/prd-contract.md` — record it in `status.json` with the
reason. A structurally complete but semantically empty PRD ("To be filled...")
stays `gathering`.

## Mermaid

PRD diagrams use `../../assets/references/mermaid-contract.md`. A TL;DR may use
a small ASCII contrast when that is clearer than a diagram. Do not generate
sintaxe visual legada.
