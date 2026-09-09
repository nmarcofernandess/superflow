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
    "review": "pending",
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
    "handbook": "HANDBOOK.md",
    "plan": null,
    "implementation_log": null,
    "review": null,
    "qa": null
  },
  "task_source": {
    "type": "none",
    "path": null,
    "progress": null
  },
  "campaign": "105-colisao-de-identidade",
  "depends_on": [],
  "children_source": null,
  "handbook": null,
  "updated_at": "YYYY-MM-DDTHH:mm:ssZ"
}
```

When `artifacts.plan` is set it must be `implementation_plan.json` and code
subtasks follow `tdd-contract.md`. When `artifacts.implementation_log` is set
it must be `implementation_log.json` with red/green evidence for completed
`tdd.required` tasks.


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
superseded
```

Vocabulario fechado, verificado por `validate_phase_vocabulary` em
`validate_superflow.py`. `superseded` entra como setimo valor porque
`skipped` nao cobre o caso real: "outro pacote fez isto" e diferente de
"decidiu-se nao fazer".

Mapa das grafias vivas que a migracao lazy resolve — nunca reescrever spec
antiga em massa, so ao tocar no arquivo:

| Grafia viva | Le-se como |
|---|---|
| `in_progress`, `in-progress` | `running` |
| `done`, `complete_*`, `complete — <prosa>` | `complete` (a prosa migra para `progress.md`) |
| `not_applicable`, `skipped_*` | `skipped` |
| `absorbed`, `complete_via_<outro pacote>` | `superseded` |
| `cancelled` | `superseded` quando outro pacote fez; `skipped` quando se decidiu nao fazer |

`blocked` exige `blocked_reason` com motivo assinado (campaign-contract C4).

O gate nasce em **ratchet**: `PHASE_VOCABULARY_FLOOR` congela, com data, os
pacotes que ja violavam no censo de 2026-09-09; entrada que nao viola mais
falha como stale. A lista so encolhe.

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

## `handbook` — o retrato operável da spec

O handbook responde, para quem chega sem contexto: **o que esta spec é, do que
ela depende e qual é o próximo trabalho útil**. Ele mora em `HANDBOOK.md` na
raiz do pacote — irmão de `PRD.md` —, com `artifacts.handbook` como ponteiro e o
bloco `handbook` do `status.json` carregando o veredito.

A fronteira é uma frase: **é campo o que ordena, filtra, bloqueia ou desmente; é
prosa o que argumenta.** O agregador nunca lê prosa, e a prosa nunca repete o
valor do campo como afirmação independente — foi exatamente essa duplicação que
fez um agregador por regex errar 33% dos vereditos em setembro de 2026. Por isso
o `HANDBOOK.md` **não tem seção de veredito**: selo e arquivabilidade são
renderizados do `status.json`.

### As sete seções de prosa (obrigatórias, nesta grafia)

```txt
## Intenção
## Estado real
## Rastro
## Dificuldade e impacto
## Testes
## O que a linha não comporta
## Relatório de leitura
```

`## Estado real` exige no mínimo **3 âncoras `arquivo:linha`** — backtick
sozinho não conta. É essa exigência que liga o retrato ao código; sem ela o
handbook vira prosa bonita sobre um sistema que ninguém abriu. Nenhuma seção
pode ser placeholder (`TBD`, corpo com menos de 24 caracteres, tabela vazia).

### O bloco

```json
"artifacts": { "handbook": "HANDBOOK.md" },
"handbook": {
  "read_at": "2026-09-09",
  "read_base": "dev@fed5faf18",
  "index_action": "confirm_pending",
  "selo": "in_flight",
  "archivable": "status_only",
  "archive_debts": ["migration 20260905012838 ainda não chegou a PROD"],
  "open_decisions": [
    { "id": "D1", "question": "O chip de dia persiste na URL?", "owner": "marco" }
  ],
  "next_useful": [
    { "id": "N1", "kind": "implementation", "blocked_by": [] },
    { "id": "N2", "kind": "human", "blocked_by": ["N1"] }
  ],
  "unanswered": ["não achei quem consome getExamesPorColeta fora do Care"],
  "children_rollup": null
}
```

### Vocabulários

```txt
selo:          closed  merged_dev  in_flight  pending_work
               needs_marco  stale_doc  dormant  superseded
index_action:  archive  new_line  confirm_pending  backlog
archivable:    no  status_only  yes
next_useful[].kind:
               investigation  preparation  plan  implementation  human
```

`read_at` é `YYYY-MM-DD`. `read_base` nomeia a base lida (`<ref>@<sha>`); quando
o sha não é ancestral do HEAD o validador emite **WARN**, não FAIL — retrato
velho é dívida visível, e travar PR garantiria que ninguém escreve o segundo
handbook.

### O que o bloco não aceita

- **Elegibilidade de execução gravada.** Ela é **derivada**:
  `kind != "human" && blocked_by == []`. Campos como `eligible`, `executable`,
  `runnable`, `ready` ou `actionable` dentro de `next_useful` são recusados —
  campo gravado envelhece calado e passa a mentir sobre o que está liberado.
- **`handbook.tasks`.** Task executável mora em `implementation_plan.json`
  (invariante 10).
- **Estado copiado do filho.** Ver `children_source` abaixo.
- **Qualquer campo cujo valor já exista como prosa em outro lugar.**

## `children_source` — pacote-mãe sem cópia de estado

Só o pacote-mãe declara. Ele não copia estado do filho: declara onde os filhos
estão, e `superflow_campaign.py` deriva `closed | actionable | waiting |
blocked` na hora, a partir de `depends_on` e `campaign`.

```json
"children_source": {
  "glob": "minispecs/*/status.json",
  "campaign": "105-colisao-de-identidade"
}
```

`children_source.campaign` tem de ser o **próprio `id`** do pacote-mãe, e todo
filho encontrado pelo glob precisa declarar esse mesmo `campaign` — filho órfão
derruba o pai. Glob que não encontra ninguém é válido: a mãe pode nascer antes
dos filhos virarem pacote.

Cache de rollup é opcional e vem com gate de frescor: se
`handbook.children_rollup` existir, seu `derived_at` não pode ser mais velho que
o `updated_at` do filho mais novo.

## `campaign` — obrigatório sob `minispecs/`

Pacote sob `minispecs/` é filho de campanha: `campaign` deixa de ser opcional e
tem de casar com o `id` do pacote-mãe quando este existe. Sem isso o filho fica
verde sozinho e invisível para a campanha que o encomendou.

`depends_on` não muda: continua sendo a lista de ids de que este pacote depende,
e o inverso ("o que depende dela") é derivado em tempo de leitura, nunca digitado.

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
15. `HANDBOOK.md` não é obrigatório por largada — é obrigatório por condição.
    Mas se o arquivo existir, `artifacts.handbook` tem de apontar para ele e o
    bloco `handbook` tem de existir: retrato sem ponteiro é invisível para o
    motor de campanha, e retrato sem bloco volta a exigir regex sobre prosa.
16. O veredito do handbook (`selo`, `index_action`, `archivable`) nasce campo.
    O `HANDBOOK.md` não tem seção de veredito.
17. Elegibilidade de execução é derivada (`kind != "human" && blocked_by == []`),
    nunca gravada. Rollup pai×filho também é derivado; cache só vale com
    `derived_at` mais novo que o filho mais novo.
18. Pacote sob `minispecs/` exige `campaign` igual ao `id` do pacote-mãe.

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
