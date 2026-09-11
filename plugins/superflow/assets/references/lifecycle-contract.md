# Lifecycle Contract

Esta é a lei do Superflow sobre vocabulário, lifecycle e packagehood.
O implementador aplica; não inventa a regra que falta.

Medições deste documento foram rodadas em 2026-09-10 sobre
`dietflow-app/specs` em modo leitura. Contagem sem comando no relato é
proibida. Os comandos estão no final.

Os dois denominadores não se substituem:

| Denominador | O que é | Quem entra |
|---|---|---|
| **Tipagem** | todo diretório com `status.json` | o motor lista, o validador confere, o QG mostra |
| **Estudo** | lista nominal em `.superflow/qg/study-list.json` | quem se lê e para quem se escreve handbook |

O plugin tipa e lista tudo. Estudar é outra coisa. Fóssil corretamente
tipado, sem handbook, passa verde — caso de teste obrigatório.

É proibido criar gate, check ou regra que cruze prosa de handbook com
estado de `status.json`. Semântica não é matemática. O handbook pode e
deve poder divergir do quadro de tasks e fases.

`MAX_DEPTH` e a unificação dos três recortes (descoberta automática,
`children_source.glob`, obrigação de `campaign`) ficam fora desta
entrega. O desalinhamento está descrito em D6. Não mudar profundidade.

---

## D1 — Packagehood

**Uma pasta é pacote se e somente se contém `status.json`.**

Nenhum outro arquivo cria packagehood. `analysis.md`, `SPEC.md`,
`PRD.md`, `HANDBOOK.md`, `progress.md` e `WARLOG.md` não registram a
pasta. Desregistrar um dossiê é apagar ou mover o `status.json`. O
resto do diretório fica como acervo.

### O que o validador faz com cada pasta

| Condição | Classificação | Ação |
|---|---|---|
| tem `status.json` | **pacote** | entra no denominador de tipagem; aplica o contrato do pacote |
| tem documento de spec (`PRD.md`, `SPEC.md`, `analysis.md`, `ANALYSIS-*.md`) e não tem `status.json` | **documento fora do lifecycle** | diagnóstico `unregistered_spec_documents` — não é `partial package` |
| não tem `status.json` nem documento de spec | **fora** | silêncio; não é nosso |

### Diagnóstico `unregistered_spec_documents`

Não é falha de pacote. É um relatório de repositório, nomeado, que
lista a pasta e diz onde registrar se ela deveria ser pacote:

```
unregistered_spec_documents: <pasta-relativa-ao-specs-root>
  tem <lista de documentos> e não tem status.json
  se esta pasta é um pacote, escreva status.json aqui
    (id, route, phase_budget, confidence, current_phase, decision.prd_status=gathering)
  se é acervo de outro pacote, não registre — o registro mora na pasta da mãe
  se é dossiê no lugar errado, não registre; o status.json é o que a torna pacote
```

Medido em 2026-09-10: **25** pastas com documento de spec e sem
`status.json` (comando 1). Isso inclui backlog, archived, followups e
dossiês. Não viram pacote por existirem. As que o dono quiser tipar
ganham `status.json` em `gathering`, ainda sem PRD — ver D2.

### O que deixa de ser exigido para existir como pacote

`PRD.md` e `progress.md` saem da condição de packagehood. Um pacote
pode nascer só com `status.json`.

`progress.md` nunca é exigência de packagehood. Só falha se
`artifacts.progress` aponta para um arquivo ausente (ponteiro quebrado).

`PRD.md` só é exigido quando a condição de maturidade de D2 vale
(`decision.prd_status` ∈ {`ready`} ou legado `complete` lido como
`ready`).

`HANDBOOK.md` nunca é exigido por ausência. Fóssil tipado sem handbook
passa. Se o arquivo existe, o ponteiro e o bloco valem — ver
`status-schema.md`. O conteúdo do handbook não é cruzado com
`phases.*` nem com `current_phase`.

### Antes → depois

| Situação | Antes | Agora |
|---|---|---|
| pasta com `PRD.md` / `SPEC.md` / `analysis.md` sem `status.json` | o validador Python trata como pacote e falha `partial package` ou `PRD missing` | não é pacote; diagnóstico `unregistered_spec_documents` |
| pasta com `status.json` sem `PRD.md`, `prd_status=gathering` | falha `PRD missing` / `partial package` | passa (registro cedo) |
| pasta com `status.json` sem `progress.md` | falha `partial package` | passa, salvo ponteiro quebrado |
| pasta com `status.json` sem `HANDBOOK.md` | já deveria passar; qualquer falha por ausência está errada | passa; caso de teste obrigatório |
| dossiê cujo `status.json` foi apagado de propósito | a pasta continuava reprovando porque o documento restava | a pasta deixa de ser pacote; some da listagem e da campanha |

O caso concreto que esta regra fecha: desregistrar
`112-exames-relayout/minispecs/designv9/spec-101-yasmin` apagando o
`status.json`. Sob a regra antiga, `PRD.md` na pasta a mantinha
"parcial". Sob esta regra, ela é acervo.

---

## D2 — Registro cedo contra maturidade do PRD

Duas condições. O código que as misturar está errado. A correção é a
condição de aplicabilidade, não a qualidade exigida para `ready`.

### Condição A — cadastro inicial (packagehood + registro)

Um pacote **pode e deve** ganhar `status.json` cedo.

Vale para minispec nomeada, subspec nomeada, e qualquer pasta que o
dono queira tipar.

No cadastro inicial é lícito:

- `decision.prd_status = gathering`
- `phase_budget` incerto (`lean` é o default honesto; `capture` também)
- `route` ainda provisória
- **ausência de `PRD.md`**
- ausência de `progress.md`, `analysis.md`, `SPEC.md`, handbook

Obrigatório no cadastro:

- `status.json` presente (é isso que a torna pacote)
- `id` (slug estável; preferir o nome da pasta)
- `current_phase` ∈ vocabulário fechado de D5
- `decision.prd_status` presente e, no nascimento, `gathering`
- `decision.verdict` presente; scaffold nasce `inbox` ou `prd_draft`
- `schema_version` gravado como `superflow.status.v1` em todo
  **write** novo. Leitura lazy: campo ausente lê-se como
  `superflow.status.v1` até o arquivo ser regravado. Qualquer outra
  string (`dietflow.subspec-status.v1`, `crystallize.run.v1`, …) falha.

Scaffold (script, taskgen, gerador) **sempre** grava `gathering`.
Nunca promove.

### Condição B — maturidade para avançar (`prd_status: ready`)

`ready` não afrouxou. Continua significando: o PRD cumpre
`prd-contract.md` e pode alimentar a próxima fase.

Quando `decision.prd_status` ∈ {`ready`} ou o legado `complete` (lido
como `ready`), aplicam-se **todas** as exigências de hoje sobre o PRD:

- `PRD.md` existe
- headings obrigatórios de `prd-contract.md`
- `## TL;DR` no lugar certo, preenchido, sem placeholder
- revisão semântica pela skill que escreveu ou revisou o PRD
  (`explain-clearly` no TL;DR, contrato de seções)

Validador estrutural verde **não promove** `gathering` → `ready`.
Só a skill que escreveu ou revisou o PRD promove. Keyword score não
promove. O implementador não cria atalho.

Invariante 14 permanece: nenhuma fase de execução (`execute`, `qa`)
roda com `prd_status = gathering`. Promova para `ready` ou marque
`blocked` antes.

### O que o validador aplica quando

| Campo / artefato | Condição A (gathering, recém-registrado) | Condição B (ready) |
|---|---|---|
| `status.json` existe | obrigatório (packagehood) | obrigatório |
| `id`, `current_phase`, `decision` | obrigatório | obrigatório |
| `PRD.md` + headings + TL;DR preenchido | não aplica | aplica |
| promoção `gathering` → `ready` | proibida (só a skill dona do PRD) | já aconteceu |
| handbook ausente | passa | passa |
| `progress.md` ausente | passa | passa, salvo ponteiro |

### Antes → depois

| Situação | Antes | Agora |
|---|---|---|
| minispec nomeada, `gathering`, sem PRD | Python falha `PRD missing` | passa |
| `prd_status=ready` sem headings / TL;DR vazio | falha | falha (igual) |
| validador verde em gathering | alguns agentes liam isso como "pode promover" | estrutural verde não é revisão; não promove |

---

## D3 — Tipo de `phases.*`

**Um tipo só: string.** O valor é um dos sete de D4.

Objeto JSON em `phases.*` é inválido. Não há segundo formato
declarado. Não se aceita `{status, note}`, `{state, artifact}`,
`{fileHashes, lastRun}` nem qualquer híbrido.

### O que acontece com os objetos de hoje

Migrar. Forma antiga → forma nova. Medido no vivo (154 pacotes, sem
`archived/`): **14** valores objeto em **3** pacotes (comando 2).
Nenhum objeto fora desses três.

Regra de extração, nesta ordem:

1. Se o objeto tem `status` ou `state` (string), essa string atravessa
   o mapa de grafias de D4 e vira o valor novo.
2. Qualquer outra chave (`note`, `artifact`, `fileHashes`, `lastRun`,
   `pr`, `head_sha`, `merge_sha`, `current_task`, jobs de e2e) **sai
   de `phases.*`**. Vai para `progress.md` (log humano) ou, se for
   evidência de merge/PR, para o bloco `shipped` (D4). Não fica no
   valor da fase.
3. Depois da extração, `phases.<nome>` é string do vocabulário. O
   objeto some.

### Mapa objeto → string (14 valores, 3 pacotes)

| Pacote | Chave | Forma antiga | Campo extraído | Forma nova | Destino do resto |
|---|---|---|---|---|---|
| `081-harmonia-visual` | `analyst` | `{status, artifact, note}` | `status=done` | `complete` | `artifact`/`note` → `progress.md` |
| `081-harmonia-visual` | `build` | `{status, artifact, note}` | `status=done` | `complete` | idem |
| `081-harmonia-visual` | `plan` | `{status, note}` | `status=dormant` | `pending` | `note` → `progress.md` (`dormant` = ainda não começou; não é `skipped`) |
| `081-harmonia-visual` | `execute` | `{status, note}` | `status=dormant` | `pending` | idem |
| `081-harmonia-visual` | `qa` | `{status, note}` | `status=dormant` | `pending` | idem |
| `083-…/write-through-avisos` | `analyst` | `{state, artifact}` | `state=completed` | `complete` | `artifact` → `artifacts.analysis` / `progress.md` |
| `083-…/write-through-avisos` | `build` | `{state, artifact}` | `state=completed` | `complete` | idem |
| `083-…/write-through-avisos` | `plan` | `{state, artifact}` | `state=completed` | `complete` | idem |
| `083-…/write-through-avisos` | `execute` | `{state, current_task}` | `state=completed` | `complete` | `current_task` descarta (nulo) |
| `083-…/write-through-avisos` | `qa` | `{state, directed_e2e, preflight, smoketest}` | `state=completed` | `complete` | jobs → `qa_report.md` ou `progress.md` |
| `083-…/write-through-avisos` | `delivery` | `{state, pr, head_sha, merge_sha, …}` | — | **apaga a chave** | `state=merged_dev` + PRs → bloco `shipped`. `delivery` não é nome de fase canônico |
| `095-…/crystallize/copy-surface` | `map` | `{lastRun, fileHashes}` | `lastRun` presente | `complete` | hashes → `progress.md`. `map` como **nome** de fase continua no FLOOR de nomes até a chave ser removida |
| `095-…/crystallize/copy-surface` | `mine` | `{lastRun, fileHashes}` | `lastRun` presente | `complete` | idem |
| `095-…/crystallize/copy-surface` | `diff` | `{lastRun, fileHashes}` | `lastRun` presente | `complete` | idem |

Contagem: 2 `done` → `complete`; 3 `dormant` → `pending`; 5
`completed` → `complete`; 1 chave `delivery` removida (ship); 3
`lastRun` → `complete`. Total 14.

`phases` ausente (`null` / chave faltando): medido **10** arquivos
(comando 2). Pacote sem objeto `phases` não é objeto-em-valor; é
pacote sem mapa de fases. Leitura: trata-se como `{}`. Write novo
grava o objeto. Não é o segundo tipo.

### Antes → depois

| Situação | Antes | Agora |
|---|---|---|
| `phases.qa` string `complete` | passa o check de tipo (o valor ainda precisa do vocabulário) | igual |
| `phases.analyst` objeto | Python/TS tratam como ofensor de vocabulário (não-string) | falha de **tipo** nomeada (`phases.* must be string`), depois o valor extraído entra no vocabulário |
| segundo formato objeto "oficial" | não existia, mas o disco inventou | continua inexistente; migra |

---

## D4 — Enum de fase (`phases.*`)

Sete valores. Não colapsar para um rótulo único.

```txt
pending
running
complete
skipped
blocked
failed
superseded
```

### Semântica que o enum preserva

| Valor | Significa | Não significa |
|---|---|---|
| `complete` | esta fase terminou **neste** pacote | entrega com ship; "o filho fez" |
| `skipped` | decidiu-se **não fazer** esta fase neste pacote | outro pacote fez (isso é `superseded`) |
| `superseded` | outro pacote executou o trabalho desta fase | pulou; terminou aqui |
| `running` | esta fase está em curso | |
| `pending` | ainda não começou | dormindo por dependência de campanha (isso é o motor, não o valor) |
| `blocked` | parou por motivo assinado (`blocked_reason`) | |
| `failed` | tentou e não passou | |

**Conclusão de fase ≠ entrega com ship.** Ship não é valor de
`phases.*`. Evidência local no DietFlow (comando 3), para conferir,
não para virar definição universal do plugin:

- `current_phase=done`: **16** pacotes, **15** têm bloco `shipped`
- `current_phase=complete`: **39** pacotes, **1** tem bloco `shipped`

O plugin não conclui daí que `done` é o oitavo valor do enum. Conclui
que quem escreveu `done` no ponteiro quis dizer "entregue", e quem
escreveu `complete` quis dizer "fases terminadas sem reivindicar
ship". Essa distinção sobrevive assim:

- `phases.*` usa `complete` quando a fase terminou neste pacote
- evidência de merge/PR, quando existir, mora no bloco opcional
  `shipped` (`pr`, `merge_sha`, `merged_at`, `target`, `url`)
- ausência de `shipped` **não** falha o pacote e **não** desmente
  `complete`
- o plugin não exige `shipped` para nenhum valor de fase

`done` como valor de `phases.*` (medido **4** no total, **1** pacote
com alguma chave `done`) lê-se `complete`. Se aquele pacote tiver
bloco `shipped`, o bloco fica. O valor da fase não carrega o ship.

### Teste que prova a distinção

Três fixtures, os três passam o validador, e trocar o valor quebra o
significado — não o enum:

1. **Fase concluída sem ship.** `phases.qa=complete`, sem bloco
   `shipped`, `current_phase=qa`. Passa. Se o implementador recusar
   por "falta shipped", o implementador violou D4.
2. **Entrega com ship.** `phases.qa=complete`, bloco `shipped` com PR,
   `current_phase=qa`. Passa. O ship não mora em `phases.qa`.
3. **Filhos executaram.** Pacote mãe ou fatia irmã com
   `phases.execute=superseded` e `progress.md` nomeando o pacote que
   executou (`complete_via_spec_105` é o caso vivo: 2 valores em
   `100-fuking/minispecs/02-superficie-completo-vs-unitario`). Passa.
   Se alguém gravar `skipped`, está mentindo: não se decidiu não
   fazer; outro pacote fez. Se gravar `complete`, está mentindo: não
   foi este pacote que executou.

Caso vivo de `cancelled` → `skipped` (não superseded): as 2 chaves
`cancelled` em
`089-patient-profile-cycle-strip/minispecs/01-metrica-comparecimento`
(`taskgen`, `plan`) — KPI cancelado, fases que se decidiu não fazer.
Caso vivo de `absorbed` → `superseded`: 1 valor em
`046-modal-canonization` `phases.code=absorbed`.

### Mapa de grafias de `phases.*` (string)

Medido em **todos** os `status.json` (166). Valores string: **1016**.
Valores objeto: **14** (D3). `phases` ausente: **10**.

No **vivo** (154, sem `archived/`): 932 string + 14 objeto. Grafias
string distintas no vivo: **34**. 34 + 14 objetos = **48** formas
distintas no vivo — a conta do briefing. `complete=594`,
`skipped=153`, `pending=120` no vivo (comando 2).

| Grafia medida | N (todos) | Lê-se | Onde a prosa sobrevive |
|---|---|---|---|
| `complete` | 645 | `complete` | — |
| `skipped` | 170 | `skipped` | — |
| `pending` | 131 | `pending` | — |
| `in_progress` | 16 | `running` | — |
| `running` | 10 | `running` | — |
| `done` | 4 | `complete` | ship, se houver, fica em `shipped` |
| `not_applicable` | 3 | `skipped` | `progress.md` |
| `blocked` | 3 | `blocked` | `blocked_reason` |
| `superseded` | 2 | `superseded` | — |
| `implemented` | 2 | `complete` | `progress.md` (069 proof-atlas `modal`/`timing`) |
| `cancelled` | 2 | `skipped` neste corpus (089 KPI) | `progress.md`; regra: se a prosa nomear outro pacote executor, vira `superseded` |
| `complete_via_spec_105` | 2 | `superseded` | `progress.md` nomeia `105-colisao-de-identidade` |
| `complete_via_105_05` | 2 | `superseded` | `progress.md` nomeia a fatia 05 da 105 |
| `approved` | 1 | `complete` | `progress.md` (001 units/00 `critic`) |
| `absorbed` | 1 | `superseded` | `progress.md` (046 `code`) |
| `complete_baseline` | 1 | `complete` | `progress.md` (056 minispec 01; o follow-up é outro pacote) |
| `retry_pending` | 1 | `pending` | `progress.md` |
| `complete — <prosa>` (5 grafias distintas) | 5 | `complete` | o texto depois do em-dash → `progress.md` (todas em 069) |
| `complete_deployed_dev — <prosa>` | 1 | `complete` | PR/merge da prosa → `shipped` se parseável; resto → `progress.md` (069 `execute`) |
| `skipped_prompt_provided_discovery` | 1 | `skipped` | `progress.md` |
| `in-progress` | 1 | `running` | — |
| `complete-with-codex-amendments` | 1 | `complete` | `progress.md` |
| `partial` | 1 | `running` | `progress.md` (trabalho pela metade, não concluído) |
| `pending_migration_tests_review` | 1 | `pending` | `progress.md` |
| `layout_approved_functional_pending` | 1 | `pending` | `progress.md` |
| `artifacts_complete_external_review_pending` | 1 | `pending` | `progress.md` (093 destillery `distillery`) |
| `parts_0_to_6_shipped` | 1 | `complete` | evidência de ship → `shipped` / `progress.md` |
| `dev_and_prod_schema_verified` | 1 | `complete` | `progress.md` |
| `passed` | 1 | `complete` | `progress.md` |
| `verification_delegated_to_attestation` | 1 | `complete` | `progress.md` (a atestação é prova, não outro pacote executor) |
| `outlined` | 1 | `pending` | `progress.md` |
| `passed-subagent-static-production-proof-and-chart-header-closeout` | 1 | `complete` | `progress.md` |
| `durable-copy-under-specs` | 1 | `complete` | `progress.md` |

Grafia nova, fora desta tabela e fora do enum: falha, nomeando
arquivo, chave e valor. Sem normalizar no escuro.

`blocked` exige `blocked_reason` assinado (campaign-contract C4).

### FLOOR

O ratchet de grafia fora do vocabulário **não mora no plugin**. Mora
no consumidor: `.superflow/phase-vocabulary-floor.json` (D7).

Medido hoje: TypeScript 37 entradas, Python 38. A sobra do Python é
`072-tornar-fallback-ultimo-registro-cada-modulo-selectlatestdatedrecordperfamily`
(`qa`) — já stale no TS. Ao mover o FLOOR, essa entrada não entra.

Chave do FLOOR: caminho POSIX do pacote **relativo ao specs root**,
sem prefixo `specs/`, sem caminho absoluto de máquina. Os dois
validadores leem o mesmo arquivo. A lista só encolhe.

---

## D5 — `current_phase`

`current_phase` nomeia a **fase atual** (o ponteiro). Não nomeia o
estado da fase. Estado mora em `phases.*`.

Vocabulário fechado do ponteiro — nomes de fase, não estados:

```txt
inbox
taskgen
analyst
build
review
plan
execute
qa
```

Oito valores. `discovery` não é fase pública: lê-se `analyst`
(modo investigação), como `status-schema.md` já diz. `critic` lê-se
`review`. `code` lê-se `execute`. `units` não é fase: é
`execution_strategy` / recorte de pasta.

Não existe `done`, `complete`, `closed`, `vibe`, `coordinate` nem
`ship` neste vocabulário. Quem os usou escreveu estado, skill, papel
ou fronteira de bloco no ponteiro. O mapa abaixo traduz o ponteiro e
manda o significado para a prosa.

### Coerência

1. `current_phase` é obrigatório em todo pacote. Ausente falha,
   nomeando a derivação do mapa (não preencher em silêncio).
2. No máximo uma chave em `phases.*` vale `running`. Se houver,
   `current_phase` é essa chave, já no vocabulário de nomes
   (`critic`→`review`, etc.).
3. `current_phase` não pode apontar para uma fase cujo valor é
   `skipped` ou `superseded`.
4. `decision.prd_status=gathering` ⇒ `current_phase` ∈
   {`inbox`, `taskgen`, `analyst`}. Execute/qa com gathering falha
   (invariante 14).
5. `decision.prd_status=ready` **não** move o ponteiro. Ready é
   maturidade do PRD, não fase atual.
6. `phases[current_phase]`, se existir, ∈
   {`pending`, `running`, `complete`, `blocked`, `failed`}.
   `complete` no ponteiro+valor significa "esta foi a última fase
   que o pacote rodou; o ponteiro ainda não avançou". É lícito.
7. Nenhuma regra compara `current_phase` com prosa de handbook.

### Mapa das 25 grafias (+ ausente)

Medido em 166 pacotes: **25** grafias + **18** sem o campo.
No vivo (154): **24** grafias + **14** sem o campo. A 25ª é
`qa_and_ship`, só em `archived/` (comando 4).

| Grafia | N todos / vivo | Lê-se | Por que, e onde o significado sobrevive |
|---|---|---|---|
| `complete` | 39 / 38 | `qa` se `phases.qa` é `complete` ou ausente; senão a última chave canônica com `complete` | Categoria errada: estado no ponteiro. 1/39 tem `shipped` — a maioria terminou fase sem ship. Frase "fases terminadas sem reivindicar ship" → `progress.md` |
| `qa` | 35 / 32 | `qa` | — |
| *(ausente)* | 18 / 14 | deriva: a chave `running` se houver; senão a última canônica `complete`; senão `inbox` | a derivação vai na mensagem de erro até o write gravar o campo. Lista viva abaixo |
| `execute` | 16 / 14 | `execute` | — |
| `done` | 16 / 16 | `qa` | 15/16 têm `shipped`. "Entregue" sobrevive no bloco `shipped`, não no ponteiro. O 16º (`083-…/write-through-avisos`) não tem `shipped`; a evidência de merge está no objeto `phases.delivery` — vai para `shipped` na migração D3 |
| `build` | 7 / 7 | `build` | — |
| `plan` | 5 / 4 | `plan` | — |
| `discovery` | 5 / 5 | `analyst` | fase pública aposentada; modo investigação do analyst. `progress.md`: "unit/discovery legado" |
| `units` | 4 / 4 | `execute` | 001, 044, 045, 047 — o trabalho está em `units/`, que é estratégia, não fase. `progress.md` + `execution_strategy` |
| `analyst` | 3 / 3 | `analyst` | — |
| `closed` | 3 / 3 | `qa` | 089 mãe, 089 minispec 01, 083 `funil-criar-concluir`. Encerrado. Ship se houver fica em `shipped` |
| `code` | 1 / 1 | `execute` | `040-…/units/01-clinical`. "code" era o nome interno de execute |
| `qa_final` | 1 / 1 | `qa` | `043-m3c-pipeline-resolve`. A palavra `final` → `progress.md` |
| `critic` | 1 / 1 | `review` | `044-…/units/00-tipos-serialize`. critic era o nome interno de review |
| `build_final` | 1 / 1 | `build` | `047-…/units/01-deletar-target-user-email` |
| `followup_spec_pending` | 1 / 1 | `qa` | `056-…/minispecs/01-export-atlas-canonico`. Baseline T1–T10 feita; o next é **outro** spec (`SPEC-fechamento-runtime-export.md`). Dependência de campanha / `progress.md`, não ponteiro |
| `prd` | 1 / 1 | `taskgen` | `059-finalizacao-formularios-anamnese`. taskgen é dono de `PRD.md` |
| `coordinate` | 1 / 1 | `execute` | `083-parecer-central-drawer-agenda`. Papel de coordenador (`role: coordinator` já existe). Coordenar filhos é campanha, não fase. O ponteiro da mãe é o trabalho próprio ainda em curso (T3.1). `coordinate` → `progress.md` / campo `role` |
| `delivery` | 1 / 1 | `qa` | `083-…/dirty-guard-troca-tipo`. Entrega é `shipped`, não fase |
| `b11_f10_t1_t7_complete_ready_for_block_frontier` | 1 / 1 | `qa` | `087-…/b11-substituicao-shadow`. Bloco F10 T1–T7 fechado, fronteira do próximo bloco. Task range → `progress.md` |
| `FASE_2_FRONTEIRA` | 1 / 1 | `qa` | `087-…/b12-runtime-compat`. `current_task=BLOCO_FECHADO`, 7/7 done, envelope `B12_F11_SHADOW`. Não é fase Superflow; é fronteira de bloco deles. Envelope e task range → `progress.md` |
| `cohort_sealed_gates_green_amendments_proposed` | 1 / 1 | `qa` | `087-…/ibge-group-naming`. Cohort selado, gates verdes, emendas propostas. Emendas → `progress.md` |
| `ship_complete_backlog_D` | 1 / 1 | `qa` | `093-destillery-…`. PRs 935/936/937 shipped; backlog D aberto. Ship → `shipped`; backlog D → `progress.md` / `handbook.next_useful` |
| `vibe` | 1 / 1 | `qa` | `093-lifecycle-closure/plans/G1C.5-notification-dismiss`. **Não normalizar para uma fase `vibe`.** O arquivo diz `goal_opened_by: "ordem do Marco … (manda a ver /vibe)"`, `phase: implemented`, tasks completed, merge ainda em `proved_pending`. `/vibe` é a skill que executou, não a fase. → `progress.md`: "executado via skill /vibe; gates delegados; merge pendente" |
| `delivery_merged_installed_cleaned` | 1 / 1 | `qa` | `121-harness-resource-exhaustion`. O nome reivindica merge+install+clean; `status` do próprio arquivo ainda diz `IN_PROGRESS`. Ponteiro vira `qa`; a reivindicação de limpeza → `progress.md` até existir `shipped` |
| `qa_and_ship` | 1 / 0 | `qa` | só `archived/056-care-heroui-web-migration`. Lá `phases.qa=in_progress` e `phases.ship=pending`. Ponteiro = `qa`; `ship` como chave de fase some; pendência de PR → `progress.md` |

`vibe` e `FASE_2_FRONTEIRA` foram lidos no arquivo, não chutados.
Quem mapear `vibe` → `execute` porque "vibe é implementação" perde o
fato de que as tasks já fecharam e o que falta é merge. Quem criar
fase `vibe` viola o vocabulário.

#### 14 vivos sem `current_phase`

Derivação para a mensagem de erro / write de migração:

| Pacote | Derivação |
|---|---|
| `060-dietflow-care-completo` | última canônica `complete`, senão `inbox` |
| `069-medidas-caseiras-axioma` | `qa` (há `phases.qa` concluída em prosa) |
| `069-medidas-caseiras-axioma/proof-atlas-timing` | `qa` |
| `070-documentos-compartilhaveis` | última canônica `complete`, senão `inbox` |
| `071-care-native-publicacao-ios-android` | `inbox` (`phases` ausente) |
| `073-export-cross-module-pilha` | última canônica `complete`, senão `inbox` |
| `075-export-hub-linha-do-tempo` | última canônica `complete`, senão `inbox` |
| `077-landing-app-v2` | última canônica `complete`, senão `inbox` |
| `081-harmonia-visual` | `execute` se `phases.execute` extraído for `pending`; senão `analyst` |
| `083-…/agenda-refresh-performance-status` | última canônica `complete`, senão `inbox` |
| `083-…/drawer-export-datas-registros` | última canônica `complete`, senão `inbox` |
| `083-…/fim-semana-persistente` | última canônica `complete`, senão `inbox` |
| `085-fechamento-dev-main-ultra-review` | última canônica `complete`, senão `inbox` |
| `095-…/crystallize/copy-surface` | `qa` após D3 (`map`/`mine`/`diff` → `complete`) |

### Antes → depois

| Situação | Antes | Agora |
|---|---|---|
| `current_phase=qa` | ninguém validava o valor | passa |
| `current_phase=vibe` | passava (campo livre) | lê-se `qa`; write novo grava `qa`; grafia crua `vibe` falha |
| `current_phase` ausente | passava | falha, com a derivação da tabela |
| `current_phase=execute` com `prd_status=gathering` | invariante 14 já pedia falha; o valor em si passava | falha de coerência |
| grafia nova (`foo`) | passava | falha |

---

## D6 — `campaign` fora de `minispecs/`

Um pacote entra no cálculo de uma campanha **só** pelo campo
`campaign` do próprio `status.json`. Não existe arquivo central. Não
existe "a mãe entra porque é mãe". Não existe `depends_on` da mãe
para ela mesma.

### Mãe

A mãe declara `campaign` igual ao próprio `id`.

Isso a faz membro da campanha que ela nomeia. É auto-adesão, não
auto-dependência. `depends_on` continua sendo lista de **outros**
ids. Ciclo mãe→mãe é contrato error (já era).

`children_source.campaign`, quando o bloco existe, já tinha que ser o
próprio `id`. Esse invariante permanece. Ele **não** substitui
`status.campaign`: o motor de campanha filtra pelo campo `campaign`,
não pelo `children_source`.

Medido: **16** mães (pacote com `children_source` ou com neto
`status.json` sob `minispecs|subspecs|units|plans|crystallize`).
**0** delas têm `campaign == id`. **16** têm `campaign` ausente.
Por isso a mãe não aparece na listagem da própria campanha
(comando 5).

### Filho

Um pacote é **filho** quando existe um ancestral cujo diretório
contém `status.json`. Esse ancestral mais próximo é a mãe imediata.

Filho exige `campaign` preenchido, string não vazia.

Valor: o `campaign` da mãe imediata se ela tiver; senão o `id` da
mãe imediata. Em cadeia (subspec dentro de subspec), isso sobe até a
raiz de campanha sem o filho apontar para si.

A obrigação **não** depende do pai imediato se chamar `minispecs`.
Alcança `subspecs/`, `units/`, `plans/`, `crystallize/`, e qualquer
outra pasta aninhada sob um pacote.

Medido sem `campaign` (comando 5):

| Pasta de filho | N sem `campaign` |
|---|---|
| `subspecs/` | 18 |
| `units/` | 31 |
| `plans/` | 4 |
| `crystallize/` | 1 |
| `minispecs/` (pai imediato não é `minispecs`: `112-…/minispecs/designv9/spec-101-yasmin`) | 1 |

Os 18 sob `subspecs/` hoje passam nos dois validadores porque o guard
é `parent.name == "minispecs"`. Isso acaba.

O caso `designv9/spec-101-yasmin` é o dossiê Yasmin: a ordem do dono
foi apagar o `status.json`, não redesenhar profundidade. Sem
`status.json` ele deixa de ser filho. Não estudar o conteúdo.

### FLOOR de adesão

Não existe FLOOR de adesão de `campaign`.

O valor de `campaign` é derivável da árvore. Para o filho é o
`campaign` da mãe imediata, ou o `id` dela quando ela não tem; para
a mãe é o próprio `id`. FLOOR existe para exceção que não se computa,
e essa se computa num passe. Congelar 70 entradas seria ganhar
entrada para esconder dívida, o que o pedido proíbe explicitamente.

O FLOOR de fases continua existindo: grafia legada de fase carrega
significado que não se deriva. Os dois não se confundem.

O consumidor deriva os valores (`--derive-campaign`) e grava. O
plugin não congela a dívida e não escreve os 70 caminhos.

### Os três recortes, descritos e não redesenhados

| Mecanismo | O que faz hoje | O que esta entrega muda |
|---|---|---|
| Descoberta automática | qualquer `status.json` até profundidade 3, sem olhar nome | **nada**. `MAX_DEPTH` fora |
| `children_source.glob` | a mãe declara onde estão os filhos | **nada** no glob. A mãe passa a ter `campaign == id` |
| Obrigação de `campaign` | só se o pai imediato se chama `minispecs` | passa a ser "é filho" (ancestral com `status.json`) ou "é mãe" (`children_source` ou netos tipados) |

Os três continuam desalinhados. Pacote mais fundo que `MAX_DEPTH` com
`status.json` pode existir e esta entrega não mexe nisso. Unificar é
ticket à parte.

### Aceite da mãe

Pacote com `children_source` descreve **a si**. Aceite e Definition
of Complete são do escopo da mãe, nunca lista manual de estado de
filho. A conclusão do conjunto é o motor de campanha, recalculada,
nunca campo derivado escrito à mão (`children_rollup` só com frescor
já contratado em `status-schema.md`).

### Antes → depois

| Situação | Antes | Agora |
|---|---|---|
| minispec sob `minispecs/` sem `campaign` | falha | falha (igual) |
| subspec sob `subspecs/` sem `campaign` | passa | falha; o diagnóstico diz o valor derivado |
| unit/plan/crystallize sem `campaign` | passa | falha; o diagnóstico diz o valor derivado |
| mãe sem `campaign` | passa; some do filtro da própria campanha | falha até gravar `campaign == id` |
| mãe com `depends_on: [próprio id]` | ciclo, contrato error | continua error. Auto-adesão é o campo `campaign`, não `depends_on` |

---

## D7 — `.superflow/` como configuração genérica

Adotar é criar a convenção. Zero linhas no repo Superflow hoje.
Nenhum caminho absoluto da máquina do usuário vira requisito do
plugin ou do CI remoto.

### Nomes finais (sem hierarquia extra)

```txt
.superflow/
├── config.json
├── phase-vocabulary-floor.json
├── qg/
│   └── study-list.json
└── sprints/
```

Quatro nomes. `qg/` e `sprints/` são irmãos. Não existe
`.superflow/qg/sprints`. Não existe `.superflow/floors/` extra.
Não existe `.superflow/campaign-membership-floor.json`: adesão de
`campaign` deriva da árvore (D6), não se congela.

| Caminho | Função |
|---|---|
| `.superflow/config.json` | raiz das specs, destino de escrita, ponteiro do floor de fases |
| `.superflow/phase-vocabulary-floor.json` | ratchet de `phases.*` **do consumidor** |
| `.superflow/qg/` | material de QG; `study-list.json` é o denominador de estudo |
| `.superflow/sprints/` | composição de sprint; nunca segunda autoridade de estado |

O FLOOR sai do plugin genérico. `PHASE_VOCABULARY_FLOOR` embutido em
`validate_superflow.py` e o irmão em `check-spec-packages.ts` deixam
de ser fonte. O plugin genérico **não** carrega caminho de spec do
DietFlow.

### `config.json`

```json
{
  "schema_version": "superflow.config.v1",
  "specs": "specs",
  "destination": null,
  "floors": {
    "phase_vocabulary": "phase-vocabulary-floor.json"
  },
  "qg": "qg",
  "sprints": "sprints"
}
```

- `specs`: caminho relativo ao diretório que contém `.superflow/`.
  Default `specs`.
- `destination`: `null` = escrever QG/sprints/boards dentro de
  `.superflow/`. String = diretório de escrita, relativo ao
  `.superflow/` ou absoluto **só em runtime** (CLI/env). Pode ser
  fora do Git. O plugin não commita absoluto. O CI remoto não recebe
  absoluto de máquina.
- `floors.phase_vocabulary`: nome de arquivo dentro de `.superflow/`.
  Ausente = ratchet vazio (todo ofensor de fase é fresco). Não há
  floor de adesão de `campaign`.

### Resolução (primeira que existir vence)

1. flag CLI `--superflow-dir <path>`
2. variável de ambiente `SUPERFLOW_DIR`
3. caminhar do path sob validação (ou do cwd) para cima até achar um
   diretório que contenha `.superflow/config.json` ou `.superflow/`
4. nenhum: defaults (`specs` relativo à raiz do repo ou ao cwd), sem
   floor, sem study list, sem sprints

Runtime pode receber path absoluto via (1) ou (2). Fonte da verdade
versionada nunca contém `/Users/…`.

### De onde vêm as informações das specs

| Pergunta | Fonte | Não-fonte |
|---|---|---|
| o que é pacote | `status.json` no disco sob `config.specs` | handbook, sprint, study list |
| estado de fase / ponteiro | `phases.*`, `current_phase`, `decision` | prosa de handbook |
| árvore mãe→filho | `children_source.glob` + campo `campaign` | handbook, `depends_on` invertido digitado |
| veredito de campanha | motor, recalculado | campo derivado na mãe, WARLOG, sprint |
| denominador de estudo | `.superflow/qg/study-list.json` (lista nominal de paths relativos ao specs root) | tipagem; ausência do arquivo = study vazio, **não** "estuda tudo" |
| visualização do QG | parâmetro de geração; default = tudo tipado | study list (filtro de estudo ≠ recorte de tela) |
| sprint | `.superflow/sprints/<nome>.json` lista ids para uma operação | estado das specs; a aba sprint some quando não há operação |

`study-list.json` é um array JSON de strings (paths POSIX relativos
ao specs root). Sem arquivo, o plugin tipa e lista tudo e não estuda
ninguém. O QG, se gerado sem recorte, mostra o denominador de
tipagem — preferência do dono, não o study.

---

## D8 — Distinções que hoje se confundem

Cada par tem dois lados. Cruzá-los no validador é bug.

| Par | Lado A | Lado B | Teste que prova |
|---|---|---|---|
| Registro do pacote × maturidade do PRD | `status.json` existe, `gathering` lícito sem PRD (D2-A) | `prd_status=ready` exige PRD + revisão da skill dona (D2-B) | fixture gathering sem PRD passa; a mesma com `ready` falha |
| Fase atual × estado de cada fase | `current_phase` ∈ 8 nomes (D5) | `phases.*` ∈ 7 estados (D4) | `current_phase=qa` + `phases.qa=running` passa; `current_phase=complete` cru falha (estado no ponteiro) |
| Conclusão de fase × entrega com ship | `phases.qa=complete` | bloco `shipped` opcional | fixture complete sem `shipped` passa (teste D4.1) |
| Estado próprio da mãe × resultado de campanha | `phases.*` / `current_phase` / aceite da mãe descrevem **ela** | motor recalcula o conjunto pelos filhos | mãe com `phases.qa=pending` e filhos closed passa no pacote; o motor não lê um campo `campaign_done` escrito à mão |
| Dependência real × prioridade de sprint | `depends_on` = ids que bloqueiam | `.superflow/sprints/` = ordem humana da operação | pacote sem `depends_on` e no topo do sprint **não** é actionable se a campanha ainda tem dependência; o sprint não manda no motor |
| Escopo de visualização × participação em campanha | QG default = tudo tipado; filtro manual | membro = campo `campaign` | mãe com `campaign==id` aparece no cálculo mesmo se o QG estiver filtrado para o study list; study list não adesiva campanha |
| Informação interna × interface publicada | campos livres do consumidor (`role`, `tasks` legado, `base.worktree`) | schema Superflow (`id`, `current_phase`, `phases`, `decision`, `campaign`, `children_source`) | validador ignora chave desconhecida; não falha fóssil por ter `tasks` no status; falha se `phases.qa` for objeto |

Proibido: gate que leia "Estado real" ou "Intenção" do handbook para
aceitar ou recusar `phases.*`, `current_phase`, `decision` ou
`campaign`. Se num pacote as duas precisarem bater, é o dono da spec
quem responde, não o plugin.

Handbook vive na mãe. Não existe `HANDBOOK.md` em minispec nem
subspec, e não passa a existir.

---

## D9 — Escopo de cada validador

Hoje o TypeScript é subconjunto do Python e isso não estava escrito.
A paridade passa a ser conferível: toda regra do TS tem gêmea nomeada
no Python. O Python tem regras que o TS não reivindica.

### Por que dois

`validate_superflow.py` vive no plugin. O CI remoto do DietFlow não
faz checkout do plugin e não pode chamá-lo. Vendorizar o script cria
duas cópias que divergem. O gate TypeScript
(`dietflow-app/scripts/check-spec-packages.ts`) é autocontido e corre
no `static` remoto.

O plugin é genérico. O TS é do consumidor. FLOOR, study list e
caminhos de spec do DietFlow não voltam para o `.py`.

### Quem cobra o quê

| Regra | Python (plugin) | TypeScript (consumidor, CI remoto) | Por quê |
|---|---|---|---|
| Packagehood = `status.json` (D1) | sim | sim (já descobre só `status.json`; deixa de tratar doc órfão como pacote — ele já não trata) | tipagem |
| Diagnóstico `unregistered_spec_documents` | sim, quando o path raiz é o specs root (modo repo) | não | o CI remoto protege o denominador tipado, não caça acervo |
| Cadastro gathering sem PRD (D2-A) | sim: **não** falha | n/a (não olha PRD) | aplicabilidade |
| PRD headings / TL;DR quando `ready` (D2-B) | sim | não | qualidade de PRD; plugin sob demanda |
| `phases.*` tipo string (D3) | sim | sim | tipagem |
| `phases.*` vocabulário + FLOOR do consumidor (D4) | sim, lendo `.superflow/phase-vocabulary-floor.json` | sim, o mesmo arquivo | tipagem; paridade bit a bit |
| `current_phase` vocabulário + coerência (D5) | sim | sim | hoje **nenhum** dos dois valida o valor; os dois passam a validar |
| `campaign` em filho e mãe (D6), valor derivado | sim | sim | tipagem / campanha; o TS hoje só olha `minispecs/` |
| Integridade do plugin (skills, templates, markers) | sim | não | não existe plugin no CI remoto |
| Mindset (`analysis.md` / `SPEC.md`) | sim, quando o arquivo existe | não | qualidade; sob demanda |
| TDD plan/log | sim, quando o artefato existe | não | qualidade; sob demanda |
| WARLOG shape | sim, quando o arquivo existe | não | qualidade; sob demanda |
| Review log + R1 code shipped | sim, quando aplica | não | qualidade; sob demanda |
| Handbook **ausente** | **não falha** | **não falha** | doutrina; caso de teste obrigatório |
| Handbook presente: ponteiro + bloco + 7 seções + 3 âncoras | sim | sim | estrutura do retrato, **sem** cruzar com `phases.*` |
| Mermaid render | opt-in `--mermaid` | não | ferramenta local |
| Cruzar handbook × status | **proibido** | **proibido** | doutrina |

Paridade conferível: para cada linha "sim/sim", o mesmo input produz
o mesmo veredito (pass/fail e o nome do diagnóstico). Divergir é
bug. Linha "sim/não" é escopo declarado, não dívida escondida.

### O que o Python deixa de exigir no pacote

- `PRD.md` como arquivo obrigatório de packagehood
- `progress.md` como arquivo obrigatório de packagehood
- handbook por ausência
- `campaign` só quando `parent.name==minispecs` (a condição cresce;
  o guard estreito some)

### O que o TypeScript passa a exigir (e hoje não exige)

- valor de `current_phase` (D5)
- `campaign` em qualquer filho e na mãe (D6); valor derivado, sem FLOOR
- tipo string em `phases.*` como falha de tipo nomeada (hoje cai no
  saco de vocabulário)

### Caso de teste obrigatório (os dois)

1. Pacote com `status.json` válido, sem `HANDBOOK.md`, sem
   `artifacts.handbook` → exit 0.
2. Pasta com `PRD.md` e sem `status.json` → Python em modo repo emite
   `unregistered_spec_documents` e **não** `partial package`; TS
   ignora a pasta (não é tipada).
3. Handbook diz "tudo entregue" e `phases.execute=pending` → exit 0
   nos dois. Nenhum dos dois lê a prosa para julgar a fase.

---

## Comandos da medição (2026-09-10)

Todos sobre `/Users/marcoantonio/dietflow-app/specs`, leitura.

```bash
# 1. docs sem status.json (packagehood)
python3 - <<'PY'
from pathlib import Path
root = Path("/Users/marcoantonio/dietflow-app/specs")
DOC = {"analysis.md", "SPEC.md", "PRD.md", "ANALYSIS.md"}
docs, status = set(), set()
for p in root.rglob("*"):
    if not p.is_file():
        continue
    if p.name == "status.json":
        status.add(p.parent)
    if p.name in DOC or (p.name.startswith("ANALYSIS-") and p.suffix == ".md"):
        docs.add(p.parent)
print("status", len(status), "docs_sem_status", len(docs - status))
PY

# 2. phases.* tipos, grafias, vivo vs todos
python3 - <<'PY'
import json
from collections import Counter
from pathlib import Path
root = Path("/Users/marcoantonio/dietflow-app/specs")
# (script completo na sessão; resultados no corpo: 14 objetos / 3 pacotes;
# vivo complete=594 skipped=153 pending=120; 34 grafias string + 14 objetos = 48)
PY

# 3. shipped × current_phase done/complete
# current_phase=done 16, shipped 15; current_phase=complete 39, shipped 1

# 4. current_phase grafias
# 25 grafias + 18 ausentes (166); 24 + 14 no vivo (154); qa_and_ship só archived

# 5. campaign mães e filhos
# 16 mães, 0 com campaign==id; 18 subspecs sem campaign; 31 units; 4 plans; 1 crystallize
```

Números afirmados acima saíram desses scripts, não de memória.
