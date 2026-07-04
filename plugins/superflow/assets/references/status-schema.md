# Status Schema

`status.json` e o GPS do fluxo. Ele nao substitui o PRD, nao substitui o log e
nao vira documento narrativo.

## Campos

```json
{
  "id": "001-slug",
  "title": "Titulo humano",
  "route": "prd_execute",
  "phase_budget": "lean",
  "execution_strategy": "single",
  "source": {
    "type": "inline",
    "github_issue": null,
    "file": null
  },
  "confidence": "high",
  "phases": {
    "inbox": "skipped",
    "discovery": "skipped",
    "analyst": "skipped",
    "taskgen": "complete",
    "build": "skipped",
    "critic": "skipped",
    "plan": "skipped",
    "execute": "pending",
    "qa": "pending"
  },
  "artifacts": {
    "prd": "PRD.md",
    "analysis": null,
    "blueprint": null,
    "progress": "progress.md",
    "warlog": null,
    "plan": null,
    "qa": null
  },
  "updated_at": "YYYY-MM-DDTHH:mm:ssZ"
}
```

## Valores

### `route`

```txt
inbox_only
inbox_prd
local_prd
prd_execute
prd_plan_execute
analyst_prd
build_plan_execute
investigate_first
```

### `phase_budget`

```txt
capture
lean
standard
deep
forensic
```

### `execution_strategy`

```txt
single
per_unit
manual
```

### fase

```txt
pending
running
complete
skipped
blocked
failed
```

## Invariantes

1. `source.type = github_issue` exige `source.github_issue`.
2. `route = inbox_only` nao deve ter `specs/NNN` obrigatorio.
3. `route` com execucao exige `artifacts.prd`.
4. Fase pulada precisa ter motivo no `progress.md` ou `WARLOG.md`.
5. `confidence = low` nunca deve ir para `execute` sem confirmacao ou melhoria
   do PRD.
6. `progress.md` e o log humano padrao de task local.
7. `WARLOG.md` e reservado para produto/plugin, investigacao ou epico longo.
8. Quando `artifacts.warlog` existir, o arquivo deve seguir `warlog-contract.md`
   e usar Mermaid para snapshots visuais.
9. `phase_budget` controla fases; nao e sinonimo de modelo.

## Phase Matrix

| Route | Default phase budget | Pending phase after taskgen |
|-------|----------------------|-----------------------------|
| `inbox_only` | `capture` | none |
| `inbox_prd` | `capture` | promote |
| `local_prd` | `standard` | route review |
| `prd_execute` | `lean` | execute |
| `prd_plan_execute` | `standard` | plan |
| `analyst_prd` | `deep` | analyst |
| `build_plan_execute` | `deep` | build |
| `investigate_first` | `forensic` | discovery |
