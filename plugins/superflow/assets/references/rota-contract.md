# Rota — contrato de orquestração

Autoridade sobre a skill `rota`. A SKILL.md é o resumo operacional; este arquivo decide.

O desenho é **preenchimento de modelo**: você descreve o plano num JSON e o gerador
desenha, com as bordas fechando e as leis conferidas no mesmo passo. ASCII torto e lei
que só vive em prosa morrem juntos aqui.

```bash
python3 ../../scripts/superflow_rota.py desenhar plano.json
python3 ../../scripts/superflow_rota.py conferir wf_<runId>.json [plano.json]
python3 ../../scripts/test_rota_contract.py   # os mutantes
```

Os dois modos saem com código **1** quando reprovam: `desenhar` quando alguma lei falha,
`conferir` quando a run desviou do máximo aprovado ou trouxe rótulo fora do plano.

## O modelo a preencher

```jsonc
{
  "nome": "...", "intencao": "o que tem que existir no fim, numa frase",
  "runs": [{
    "nome": "...", "verbo": "reconhecer",       // verbo curto, vai no fluxo do topo
    "porque": "por que este run existe, e por que agora",
    "extrai": "o que sai daqui e vai ser usado depois",
    "dod":    "o que torna este run terminado, de forma conferível",
    "retorno": "{ campo[], campo{} }",           // o schema do return
    "ponte":   "o que o Marco decide aqui",      // ausente só no último run
    "suficiencia": "o que o próximo run precisa ter recebido",  // exigido junto da ponte
    "multiplicador": 1,                          // >1 = loop; exige os três campos abaixo
    "condicaoParada": "...", "maxRounds": 3, "memoria": "o que já foi refutado",
    "piorCaso": 9,                               // default: agentes × multiplicador
    "excecaoMecanica": "por que N destinos distintos são aceitáveis aqui",
    "fases": [{
      "nome": "...", "padrao": "parallel|pipeline|serial",
      "agentes": [{
        "nome": "...", "agentType": "reader|writer|fixer|integrador",
        "modelo": "sonnet|opus", "effort": "low|medium|high|xhigh|max",
        "schema": {"nome": "SHARD", "campos": ["alvo", "afirmacoes[]", "fonte", "faltou[]"]},
        "semSchemaPorque": "...",                // só quando schema é "—"
        "corrige":  "caminho do artefato, ou —", // o que ele altera
        "registra": "qa-v1.md, ou —",            // o julgamento versionado (L7)
        "somenteLeitura": true,                  // fixer de auditoria: registra, não corrige
        "isolamento": "worktree"                 // exige integrador em fase posterior
      }]
    }]
  }]
}
```

`corrige` e `registra` são campos separados de propósito: um `fixer` que corrige o
artefato **e** versiona o julgamento precisa dos dois, e um único campo tornaria isso
indesenhável. Na coluna `escreve` do desenho eles aparecem como `artefato +registro`.

## O que o gerador reprova

| reprova | lei |
|---|---|
| pior caso acima de 15 **sem `justificativaTeto`** | L1 |
| `piorCaso` que contradiz `agentes × multiplicador` | L1 |
| `maxRounds` que discorda de `multiplicador` | L2 |
| plano sem run nenhum, ou sem `intencao` | §3 |
| `multiplicador > 1` sem `condicaoParada`, `maxRounds` ou `memoria` | L2 |
| `piorCaso` diferente de `agentes × multiplicador` (aviso) | L2 |
| `fixer` sem `corrige` e sem `somenteLeitura` | L3 |
| `fixer` somente-leitura sem `registra` | L3 + L7 |
| `fixer` que corrige e não registra (aviso) | L7 |
| `reader` com `corrige` | L3 |
| mais de 3 destinos distintos escritos na mesma fase, sem `excecaoMecanica` | L4 |
| dois ou mais no mesmo destino de `corrige` **ou de `registra`**, em `parallel`/`pipeline`, sem `isolamento` | L4 |
| dois isolados no mesmo destino sem `integrador` em fase posterior | L4 + L6 |
| `schema` que é só um nome, ou objeto sem `campos` | §3 |
| sem `schema` e sem `semSchemaPorque` | *Free-Text Parsing* |
| run sem `porque`, `extrai` ou `dod` | §3 |
| run sem `retorno` | L6 |
| run que não é o último e não tem `ponte` | §4 |
| `ponte` sem `suficiencia` | §4 |
| `agentType`, `modelo`, `effort` ou `padrao` ausente ou fora do vocabulário | §3 |

Em `serial` não existe colisão de destino: um escreve depois do outro. A checagem de
`isolamento` só vale onde os agentes correm juntos.

## A regra do desenho

**Uma linha por agente. Nunca `… mais N iguais`.** Agente escondido é agente que ninguém
conta, e contar agente é a razão de o desenho existir. Resumir também mente sobre o
custo: numa barreira real de oito builders, o mais lento levou 42m40s e o mais rápido
8m58s — a leva custa o pior, não a média, e isso só aparece com as oito linhas à mostra.

Um plano dentro de 15 não passa de ~35 linhas. Se ficou longo, o alarme é o tamanho:
o plano deve uma justificativa, e quem aprova decide olhando o número.

A moldura tem 96 colunas e um `assert` garante que as seis colunas cabem dentro dela.
Conteúdo maior que a coluna é truncado com `…`, nunca estoura a borda. `testar.sh`
confere isso a cada execução, medindo o desenho canônico linha a linha.

## As colunas que mudam entre os dois modos

| | `desenhar` | `conferir` |
|---|---|---|
| 2ª | `agentType` | `estado` |
| 4ª | `effort` | `tokens` |
| 5ª | `schema` | `tempo` |
| 6ª | `escreve` | chamadas de ferramenta |

`agente` e `modelo` ficam nas mesmas colunas nos dois — é onde a diferença salta sozinha.

## O que `conferir` acrescenta

- **Contagem:** compara `agentCount` com o `// AGENTES:` do script. Realizado **≤** máximo
  está conforme; parada antecipada prevista usa menos e não é desvio.
- **Identidade:** com o `plano.json`, lista os rótulos que não correspondem a agente
  nenhum do plano — porque mesma contagem não prova mesmo trabalho. Sem o plano, imprime
  que a identidade ficou **não verificada**.
- **Modelo:** quando as chamadas rodaram em modelos diferentes do `defaultModel`, ele
  diz. `defaultModel` não prova o modelo de nenhuma chamada.
- **Campo ausente:** sai como `n/v`, nunca como zero.
- **Limite:** imprime, sempre, que o JSON cobre aquela run e não prova que o chat deixou
  de usar Agent tool por fora dela.

---


Conferido em 09/09/2026 contra a documentação oficial (`code.claude.com/docs/en/workflows`)
e a skill `workflow-authoring` instalada. Quando esta página divergir da skill instalada,
a skill vence — ela acompanha a versão do runtime.

## Assinaturas

```js
agent(prompt, opts?): Promise<any>
  opts = { label?, phase?, schema?, model?, effort?, isolation?: 'worktree', agentType? }

pipeline(items, stage1, stage2, ...): Promise<any[]>   // sem barreira entre estágios
parallel(thunks): Promise<any[]>                       // barreira: espera o conjunto
workflow(nomeOuRef, args?): Promise<any>               // sub-workflow, um nível só
phase(titulo): void
log(mensagem): void
args                                                   // o input do run, verbatim
budget = { total: number|null, spent(): number, remaining(): number }
```

- **`schema`** força saída estruturada: o subagente chama uma ferramenta de saída e
  `agent()` devolve o objeto validado. Raiz precisa ser `{type:'object', properties:{…}}`
  e `required ⊆ properties`. Schema insatisfazível falha **antes** de o agente subir.
- **`agentType`** resolve no mesmo registro do Agent tool. Este plugin declara `reader`,
  `writer`, `fixer` e `integrador`. Compõe com `schema`.
- **`effort`**: `low | medium | high | xhigh | max`. Omitir herda o da sessão.
- **`model`**: a documentação recomenda omitir para herdar o modelo da sessão. **Nossa
  política é declarar sempre.** Motivo medido: numa run de 09/09/2026 com
  `defaultModel: claude-opus-5`, duas chamadas sem `model` rodaram em `claude-sonnet-5`
  — inclusive o agente de integração. Omitir não é neutro.
- **`isolation: 'worktree'`**: 200–500ms e disco por agente. Só quando agentes mutam
  arquivos em paralelo e conflitariam. A worktree é removida se nada mudou. Um agente
  posterior em worktree nova **não** recebe as alterações do anterior de graça: a
  entrada precisa nomear branch, commit ou artefato a consumir.
- **`budget`** vem da diretiva `+500k` do usuário. É **teto duro**: quando `spent()`
  atinge `total`, as próximas chamadas `agent()` lançam. `spent()` conta tokens de
  saída do turno inteiro — o pool é compartilhado entre o loop principal e todos os
  workflows, não é por workflow. `total` é `null` quando não houve diretiva, e aí
  `remaining()` é `Infinity` — um loop guardado só por `remaining()` corre até o teto
  de 1.000 agentes. Ausência de orçamento nunca autoriza loop sem término.

## Limites

| limite | valor |
|---|---|
| recomendação de tamanho | `workflowSizeGuideline`: `small` <5 · `medium` <15 (default) · `large` <50 · `unrestricted` |
| aviso "Large workflow" | acima de 25 agentes ou 1,5M tokens projetados — é advisory, não bloqueia |
| teto duro por run | 1.000 chamadas `agent()` |
| concorrência | `min(16, CPUs − 2)`; o excesso enfileira |
| itens por `parallel`/`pipeline` | 4.096 — passar mais é erro explícito, não truncamento silencioso |

O 15 desta skill não trava: acima dele o plano precisa de `justificativaTeto`, uma
frase que explique o número, e passa. É ônus de explicar, não proibição — quem aprova
vê a conta por extenso e decide. `medium` é recomendação de tamanho ao escrever o
script; também não bloqueia execução.

## O que o script NÃO pode

- **Input humano no meio do run.** Só prompts de permissão pausam. Assinatura entre
  etapas = etapas em runs separados.
- **Filesystem e shell.** Quem lê, escreve e executa é o agente; o script coordena.
- **`import()`** — o script falha antes de rodar.
- **`Date.now()`, `Math.random()`, `new Date()` sem argumento** — lançam, porque
  quebrariam o replay do resume. Passe tempo por `args`; carimbe depois do retorno;
  para variar, use o índice do item.
- **TypeScript.** É JavaScript puro: anotação de tipo, interface e genérico não parseiam.
- **`meta` computado.** `export const meta` é a primeira instrução e um literal puro —
  variável, chamada, spread ou interpolação derrubam o comando do autocomplete.

## `null` não é resultado negativo

`agent()` devolve `null` quando o usuário pula o agente ou o subagente morre em erro
terminal de API depois das tentativas. Em `pipeline`, um estágio que lança derruba
aquele item para `null` e pula os estágios restantes dele. Em `parallel`, um thunk que
lança vira `null` no array — a chamada nunca rejeita.

**Contabilize antes de filtrar.** Três itens pedidos e duas saídas válidas não autorizam
declarar cobertura dos três: o item ausente permanece identificado no resultado, como
falho ou não obtido. `.filter(Boolean)` é o último passo, nunca o primeiro, e o que ele
tirou já está registrado.

## Retomada

O resultado traz `runId`. Retomar: `Workflow({ scriptPath, resumeFromRunId })`. O prefixo
inalterado de chamadas devolve resultado do cache; a primeira chamada editada ou nova, e
tudo depois dela, roda ao vivo. Falha no meio de um fan-out reexecuta o que já tinha
terminado depois dela. Não use `resume` para esconder rota nova nem para reiniciar
orçamento.

## Onde a evidência mora

```
~/.claude/projects/<projeto>/<sessão>/
├── workflows/wf_<runId>.json          ← status, fases, agentes, totais, script
├── workflows/scripts/<nome>-wf_<id>.js
└── subagents/workflows/wf_<runId>/
    ├── journal.jsonl                  ← retorno real de cada agente
    └── agent-<id>.jsonl
```

A raiz muda com `CLAUDE_CONFIG_DIR`. Use o caminho que a ferramenta devolveu; escolher
o arquivo mais recente não identifica a run que acabou de rodar.

Campos observados em `wf_<runId>.json`: `runId`, `status`, `agentCount`, `totalTokens`,
`totalToolCalls`, `durationMs`, `defaultModel`, `script`, `scriptPath`, `phases[]`,
`workflowProgress[]` — este último com um registro por agente trazendo `label`,
`phaseIndex`, `model`, `state`, `startedAt`, `durationMs`, `tokens`, `toolCalls`,
`resultPreview`. Inspecione com `jq 'keys'` antes de escrever consulta: o formato é de
research preview e pode mudar.

Barreira e concorrência se **observam** por sobreposição das janelas de tempo. Isso
descreve a execução; dependência lógica se confere no script. Duas tarefas podem acabar
serializadas por falta de slot mesmo sem barreira nenhuma.

## Fontes

| # | fonte | o que sustenta |
|---|---|---|
| 1 | `code.claude.com/docs/en/workflows` | mecânica, limites, permissões, retomada |
| 2 | skill `workflow-authoring` | assinaturas exatas, `budget`, `effort`, `agentType`, patterns de qualidade |
| 3 | `github.com/zircote/workflows-plugin` | vocabulário dos anti-patterns citados na SKILL |
| 4 | `github.com/democra-ai/claude-workflow-viz` | onde a evidência mora e o que é inferido por tempo |
| 5–6 | `xz1220/open-dynamic-workflows`, `six-ddc/codex-dynamic-workflows` | só contexto. Primitiva de mesmo nome em outro runtime não garante o mesmo comportamento; nada daqui é implementado |
