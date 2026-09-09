---
name: rota
description: Use quando a saída vai ser um workflow multi-agente de verdade, quando o operador pede para ver ou aprovar o desenho antes ("me mostra em passos", "como tu ia orquestrar", /rota), ou para conferir uma run já executada contra o desenho aprovado. Delegar um ou dois subagentes numa tarefa comum não invoca esta skill. Transforma o pedido em plano aprovável — reconhecimento do material, um ou mais runs com POR QUÊ / EXTRAI / DoD, tabela de agentes com papel, modelo, effort e schema, pontes com critério de suficiência —, PARA para aprovação, compila para o runtime e confere a run executada contra o desenho.
---

# /rota — desenhar, aprovar, executar e conferir o mesmo percurso

Orquestração com mais de um subagente usa a ferramenta **Workflow**. Nunca Agent tool
em série a partir do chat, nem outra frota escondida dentro dos prompts. Se Workflow
não estiver disponível, relate antes de executar; não troque de motor por conta própria.

O plano aprovado É o script. Se o que rodou não foi ele, a primeira frase do relato é
**"não segui o desenho aprovado"**, seguida da diferença concreta.

**O número é declarado, não travado.** O pior caso vai no cabeçalho, o operador vê e
aprova. Acima de 15 o desenho justifica em uma frase — não é proibição, é ônus de
explicar. E o máximo aprovado é teto, nunca cota a preencher: parada antecipada
prevista usa menos e está conforme.

**Contrato (autoridade):** `../../assets/references/rota-contract.md` — mecânica do
runtime, modelo do plano e o que reprova. Esta skill é o resumo operacional.
Playbooks: `../../assets/playbooks/`. Assinaturas do Claude Code: skill `workflow-authoring`.

---

## 1 · Reconhecer o material antes de dividir o trabalho

```
reconhecer o material → dimensionar a leitura → escolher a divisão → desenhar o run
```

Dividir trabalho sobre um pedido mal lido custa mais caro que dividir errado. Antes de
qualquer agente, registre:

| campo | o que entra |
|---|---|
| resultado | o que tem que existir no fim, onde mora, para quem serve |
| escopo | um item por coisa pedida, com o trecho verbatim curto que o sustenta |
| descobertas | o que falta saber para escolher o trabalho seguinte |
| FORA | o que não será feito, lido, alterado ou decidido nesta rodada |

Identifique pedido por **significado**, não por pontuação: pedido sem `?` continua sendo
pedido, e frase com `?` pode ser exemplo ou histórico. Entrega e restrição têm citação;
meio necessário — localizar fonte, medir volume — é proposta sua, justificada pelo
resultado, não exigência atribuída ao Marco.

Reconhecer é localizar, filtrar e medir. Não é ler tudo, nem executar a tarefa seguinte
disfarçada de leitura. Se escolher a divisão exigir investigação de verdade, **essa
investigação é o primeiro run** — e a execução não entra escondida dentro dela.

---

## 2 · As sete leis

| # | lei | reprova quando |
|---|---|---|
| L1 | **O pior caso é contado antes e declarado** | o total não sai de uma soma que cabe numa linha; ou passa de 15 sem uma frase que justifique |
| L2 | **Loop só com pior caso multiplicado** | falta condição de parada, `maxRounds`, largura por rodada ou memória do que já foi refutado — ou `AGENTES` traz o caso feliz em vez de `rodadas × largura` |
| L3 | **Quem revisa corrige, onde a escrita está autorizada** | um `fixer` com permissão de escrita entrega achado sem corrigir. Auditoria somente leitura declara `somenteLeitura` e continua somente leitura — mas registra o julgamento |
| L4 | **Um agente escreve tudo que se conecta** | mais de 3 destinos distintos escritos por agentes diferentes na mesma fase, sem exceção mecânica declarada; ou dois no mesmo destino sem isolamento; ou dois isolados sem integração depois |
| L5 | **Afunilamento, não repetição** | a correção repete a fase inteira em vez de estreitar: por grupo → condicional → geral |
| L6 | **Toda entrega tem forma explícita de ser consumida** | o run termina em "achados" e sobra para o Marco ler dez arquivos e decidir |
| L7 | **Nada existe só no transcript** | julgamento ou correção que não virou `<pasta>/<papel>-v<N>.md` — `qa-v1.md`, `fix-v1.md`, `qa-v2.md`, sem sobrescrever |

**L4 tem exceção, declarada em uma frase:** trabalho mecânico sobre padrão já pronto e
provado — a mesma correção em N itens que já existem, sem referência cruzada entre eles.
Escreva por que é mecânico no campo `excecaoMecanica`.

**L6 não pede um agente a mais.** Às vezes o script combina saídas estruturadas; às vezes
um participante existente sintetiza; às vezes é preciso um integrador. O que não pode é o
run acabar sem forma de consumo. Não crie integrador por receita, e não obrigue um agente
a "ler tudo" quando isso recria o gargalo de contexto que a orquestração evitava.

**L6 também não é gosto:** o runtime não aceita input humano no meio de um run.
Assinatura entre etapas = etapas em runs separados.

---

## 3 · A saída: o plano

**O desenho não se escreve à mão.** Escreva o plano em JSON e gere:

```bash
python3 ../../scripts/superflow_rota.py desenhar plano.json
```

Ele desenha e **confere as leis no mesmo passo**, saindo com código 1 quando reprova.
Molde completo no contrato; exemplo válido em `../../assets/templates/plano.json`. Enquanto sair 1, não existe plano para aprovar.

A saída tem esta forma:

```
╔══════════════════════════════════════════════════╗
║ PLANO · <nome>                    para aprovação ║
║ intenção   <o que tem que existir no fim>        ║
║ forma      <n> runs · máximo <n> agentes         ║
╚══════════════════════════════════════════════════╝
   RUN 1 ──■──► RUN 2        ■ = ponte: o Marco lê, ajusta, libera
╔══════════════════════════════════════════════════╗
║ RUN 1 · <nome>                 máximo <n> agentes║
║ POR QUÊ   por que este run existe, e por que agora║
║ EXTRAI    o que sai daqui e vai ser usado depois ║
║ DoD       o que torna este run terminado         ║
╚══════════════════════════════════════════════════╝
┌─ FASE · <nome> ────── ‖ PARALLEL · espera <n> ───┐
│   agente  agentType modelo effort schema escreve │
└──────────────────────────────────────────────────┘
■ PONTE     return { … }
            suficiência: <o que o próximo precisa ter recebido>
```

**Uma linha por agente. Nunca `… mais N iguais`.** Agente escondido é agente que ninguém
conta, e contar agente é a razão de o desenho existir. Respeitado o teto, ele não passa
de ~35 linhas; se ficou longo, o alarme é o tamanho.

**Vocabulário fechado — o gerador reprova o que estiver fora:**

| campo | valores |
|---|---|
| `padrao` | `parallel` `‖` barreira, espera o conjunto · `pipeline` `→` sem barreira, item A pode estar no estágio 3 com B ainda no 1 · `serial` `·` |
| `papel` | `reader` · `writer` · `fixer` · `integrador`. É rótulo do desenho e instrução no prompt. Onde o runtime tiver registro de subagente (Claude `agents/`, Codex `~/.codex/agents/` via `agent_type`), ele resolve por lá — mas o plano não depende disso |
| `modelo` | `sonnet` trabalho guiado · `opus` julgamento e síntese. **Declare em toda chamada** |
| `effort` | `low` mecânico · `medium` padrão · `high` · `xhigh` · `max` |
| `schema` | `{"nome": …, "campos": [...]}` com os campos escritos. Nome sozinho não é contrato. Sem schema exige `semSchemaPorque` |
| `corrige` | o artefato que o agente altera, ou `—` |
| `registra` | o julgamento versionado, `qa-v1.md`/`fix-v1.md`, ou `—` |
| `isolamento` | `worktree`, só quando dois agentes mutariam o mesmo arquivo em paralelo — custa 200–500ms e disco, e exige integração depois |

Cada schema carrega o que o consumidor seguinte precisa: resultado, razões, referências
de artefato, lacunas, e a ação que agora se torna possível. A lógica nunca depende de
interpretar prosa livre.

**A conta, por extenso:** `máximo = 2 fixos + 3 rodadas × 2 = 8 · teto 15`. Inclua ramos,
repetições e subworkflows. Se falta dado para limitar o fan-out, termine a descoberta
antes de desenhar a expansão. Não corte itens em silêncio para caber.

**Depois disso: parar.** Nenhum agente antes do "ok". Registre qual versão foi aprovada.
Permissão do runtime não substitui essa aprovação.

---

## 4 · Onde cortar em mais de um run

Um run entrega **um resultado coerente** — pode responder a várias perguntas
relacionadas. Corte quando a resposta muda o desenho do trabalho seguinte:

- não dá para escrever a lista nominal do fan-out → levantá-la é o run anterior;
- a quantidade de agentes do próximo depende de um número que ainda não existe;
- há decisão que é do Marco, e o runtime não aceita input no meio de um run;
- o pior caso somado passa de 15.

**Não** justifica cortar: "são etapas conceitualmente diferentes". Isso é fase, não run.

Cada ponte declara o **critério de suficiência**: o que o run anterior precisa ter
devolvido para o seguinte poder ser desenhado. Não satisfeito, a ponte não atravessa —
ajusta-se e roda o anterior de novo. É este o loop controlado: explícito, entre runs,
com o Marco no meio. Nunca um loop escondido dentro do script.

---

## 5 · Depois do "ok"

1. Gerar o script com a mesma estrutura, escopos, modelos, `effort`, schemas e condições
   aprovados. Nenhuma chamada a mais.
2. Cabeçalho. No Claude Code o hook `guard-agent-model` (local, não versionado aqui)
   roda em `PreToolUse` e nega sem ele; nos outros runtimes vale como declaração:
   ```js
   // ROTA: aprovada pelo Marco em <data> | versão <N>
   // AGENTES: <máximo aprovado>   ← o pior caso, não o caso feliz
   ```
3. `export const meta = { … }` é a primeira instrução, literal pura. Títulos de fase
   iguais aos do plano. `label` estável em toda chamada, e `phase` explícito dentro de
   `parallel`/`pipeline`.
4. **Repetição se escreve com `for` contado**, com o limite literal no código. O hook
   nega `while` em script com `agent(` — a largura de um `while` não é conhecível antes,
   e o `for` contado só passa com `// AGENTES:` declarado e dentro do teto.
5. Prompt longo vive em arquivo e chega por `args` (o caminho). **Preserve a versão do
   conteúdo usado** — caminho estável não prova instrução inalterada.
6. Rodar com Workflow. Anotar `runId`, `scriptPath` e os args.
7. Saída antecipada já prevista é execução do desenho, não desvio. Mudança de escopo,
   participante, modelo, limite ou dependência: **parar e mostrar o plano novo.** Não
   mandar compensação por Agent tool depois.

---

## 6 · Depois do run: conferir

Sem esta etapa a rota não fecha. A conferência é sua; não lance agente por rotina.

```bash
python3 ../../scripts/superflow_rota.py conferir wf_<runId>.json plano.json
```

Redesenha a run executada no mesmo layout do plano, compara a identidade das chamadas
contra ele, e sai com código 1 em caso de desvio. Localize o JSON pela **`runId` que a
ferramenta devolveu** — nunca pelo arquivo mais recente. Sem o `plano.json`, a identidade
das chamadas fica marcada como **não verificada**, e é assim que ela deve ser relatada.

| aspecto | critério |
|---|---|
| motor e entradas | veio de Workflow, com a versão aprovada do script, dos prompts e dos args |
| chamadas | label, item, modelo e papel realizados pertencem ao caminho aprovado. **Mesma contagem não prova o mesmo trabalho** |
| contagem | realizado **≤ máximo**. Parada antecipada prevista usa menos e está conforme. Falha, pausa e cancelamento são situações distintas de sucesso |
| relações | barreiras e dependências correspondem ao script. Em `pipeline`, fases intercaladas são normais. Sobreposição de horários observa, não prova topologia |
| cobertura | o pedido está entregue ou explicitamente pendente, com os arquivos acessíveis |
| consumo | tokens contra a estimativa, na mesma métrica |

**`defaultModel` não prova o modelo das chamadas** — confira agente a agente. Campo
ausente não vale zero nem conformidade: sai como `n/v`, e se relata como não verificável.

**O JSON cobre aquela run, não a sessão.** Ele não prova que o chat deixou de usar Agent
tool por fora. Quando o registro da sessão não estiver acessível, declare esse limite em
vez de presumir conformidade.

O relato começa pela aderência, depois o resultado. São avaliações diferentes: a rota
pode ter sido seguida e o trabalho ter ficado ruim, e o contrário também.

---

## 7 · Reprovado antes de rodar

O gerador pega o que é verificável. Estes são os que dependem de você, e cada um reprova
o desenho — em itálico, o nome do catálogo público de anti-patterns:

- Loop cujo pior caso não é uma multiplicação escrita (*Unbounded Loop*).
- Um agente por arquivo numa superfície que se conecta.
- Barreira onde bastava `pipeline` — `parallel` que só existe para esperar (*Barrier Abuse*).
- Desenho que espera o Marco responder no meio do run (*Mid-Run Conversation*).
- Campo necessário depois, lido de prosa em vez de `schema` (*Free-Text Parsing*).
- `return` que despeja o texto dos agentes em vez de reduzir (*Context Flood*).
- `.filter(Boolean)` sem contabilizar antes a identidade de quem falhou.
- Run que acaba sem forma explícita de ser consumido.
- `…mais N` escondendo agentes no desenho.
- Agent tool em série do chat quando há mais de um subagente.
- Rodar antes do "ok", ou rodar algo diferente do plano aprovado.
- Tratar o máximo aprovado como cota a preencher.
- Fechar o relato sem conferir a run executada contra o plano.
