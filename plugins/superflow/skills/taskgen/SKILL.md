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

Generated PRDs must include `Story de Usuario`, `Story Tecnica`, current vs
desired behavior, system pattern/contract, acceptance criteria, and definition
of complete. A shallow idea can have low confidence, but it still uses the same
shape as a mature PRD.

## PRD Gate

Every scaffolded package is born with `decision.prd_status = "gathering"`. The
script only scaffolds; it never promotes. Promotion to `ready` is this skill's
act after reviewing and filling the PRD content against
`../../assets/references/prd-contract.md` — record it in `status.json` with the
reason. A structurally complete but semantically empty PRD ("To be filled...")
stays `gathering`.

## Mermaid

PRD diagrams use `../../assets/references/mermaid-contract.md`. Do not generate
sintaxe visual legada.
