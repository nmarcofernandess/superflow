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
  "current_phase": "execute",
  "decision": {
    "verdict": "prd_ready",
    "prd_status": "ready",
    "reason": "Promoted by the PRD-owning skill after review against the PRD contract.",
    "prd_path": "PRD.md",
    "discard_path": null
  },
  "phases": {
    "inbox": "skipped",
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
    "implementation_log": null,
    "qa": null
  },
  "task_source": {
    "type": "none",
    "path": null,
    "progress": null
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

### `decision.verdict`

```txt
inbox
prd_draft
prd_ready
needs_analysis
needs_product_decision
discarded
```

Legado: specs antigas podem conter `needs_discovery` e uma fase `discovery` no
`phases`. Discovery não é mais fase pública — investigação de bug/comportamento
desconhecido é modo do Analyst (migração lazy; não reescrever specs antigas).

### `decision.prd_status`

```txt
gathering
ready
blocked
superseded
```

`gathering` = ainda reúne decisões/evidências (todo scaffold nasce aqui).
`ready` = cumpre o prd-contract e pode alimentar a próxima fase.
`blocked` = depende de decisão/evidência externa.
`superseded` = outra versão/artefato é canônico.

Legado: specs antigas podem conter `draft`/`complete`/`discarded` — leia como
`gathering`/`ready`/`superseded` (migração lazy; não reescrever specs antigas).

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
10. `status.json` nao armazena a lista detalhada de tasks. Tasks executaveis
    vivem em `implementation_plan.json`; progresso de execucao vive em
    `implementation_log.json`.
11. Quem executa a fase atualiza o status da fase. O roteador/orquestrador pode
    inicializar e retomar, mas nao deve marcar `complete` no lugar do executor
    que possui a evidencia.
12. `decision.prd_status = ready` significa PRD pronto para a proxima fase,
    nao implementacao pronta. So a skill que produziu/revisou o conteudo do
    PRD promove `gathering -> ready`; scaffold (script) sempre grava
    `gathering`, e `ready` nunca deriva de score de keywords.
13. Se `artifacts.plan = "implementation_plan.json"`, `task_source.path` deve
    apontar para o mesmo arquivo.
14. Nenhuma fase de execucao roda com `prd_status = gathering`. Promova para
    `ready` ou marque `blocked` antes de executar.

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
| `investigate_first` | `forensic` | analyst (investigation mode) |

## Phase Ownership

| Phase | Reads first | Main output | Status owner |
|---|---|---|---|
| taskgen | source input | `PRD.md`, `status.json`, `progress.md` | taskgen |
| analyst | `PRD.md` or issue body | `analysis.md` | analyst |
| build | `PRD.md` and analyses when present | `SPEC.md` (legacy `technical_blueprint.md`) | build |
| plan | `PRD.md` and optional blueprint | `implementation_plan.json` | plan |
| execute | `PRD.md`, plan when present | `implementation_log.json` and code | execute |
| qa | `PRD.md`, plan/log when present | `qa_report.md` | qa |
