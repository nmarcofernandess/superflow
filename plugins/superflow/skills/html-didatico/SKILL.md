---
name: html-didatico
description: Cria documentos HTML visuais e didáticos — manuais, quickstarts, one-pagers, murais de status, explicações de feature ou de projeto para sócio, cliente, equipe ou família — no estilo editorial impresso com "dioramas" — mini-interfaces falsas desenhadas em CSS puro (fichas, modais, toggles, toasts, fluxos, carimbos) que tornam o documento fofo e fácil de entender. Use sempre que o usuário pedir um HTML bonito/fofo/didático, um manual visual, um quickstart, um documento para leigo entender algo técnico, um resumo de sprint/feature em página única, ou mencionar "aquele estilo de HTML com figurinhas/dioramas". Também quando pedir para transformar uma explicação técnica em algo apresentável. Inclui também a Direção C — um wireframe de "prova final" (checklist de verificação pós-merge que vira o próprio relatório de prova quando preenchido) — use quando o pedido for "monta um checklist de verificação dos PRs", "wireframe de prova final", "documento pra provar que os merges funcionam de verdade", ou qualquer variação de organizar a re-verificação de trabalho já mergeado antes de fechar decisões. Inclui também a Direção D — a "prancha de decisão", um wireframe que desenha N formas da MESMA estrutura lado a lado para o leitor escolher — use quando o pedido for "faz um wireframe disso", "me mostra as opções", "onde isso deveria ficar", "qual layout faz mais sentido", ou quando a conversa travou porque as partes não estão vendo a mesma estrutura na cabeça.
---

# HTML Didático — documentos editoriais com dioramas de CSS

Um documento desse estilo tem duas metades inseparáveis: **layout de impresso** (papel,
tinta, tipografia com caráter, hairlines, numerais gigantes) e **dioramas** — pequenas
cenas de interface desenhadas só com HTML+CSS, que mostram o conceito em vez de
descrevê-lo. O resultado parece um manual de operação bem diagramado, não um site.

O leitor-alvo quase sempre é um **não-técnico** (sócio, cliente, família). O documento
falha se precisar de tradutor do lado.

**REQUIRED SUB-SKILL:** Use `writing-clearly-and-concisely` for every headline,
paragraph, label, status, and caption before finalizing the HTML.

## Processo

### 1. Conteúdo antes de estética

Didático = concreto. Antes de abrir uma tag:

- Ler a fonte real (código, docs, conversa) — mensagens de erro literais, nomes de
  campos, números reais valem ouro num diorama.
- Dar personagem aos exemplos ("a paciente Maria", "o Mercado Central") — cenário
  abstrato não gruda.
- Definir a espinha: 3–6 seções, cada uma com UMA ideia. Se a seção tem duas ideias,
  são duas seções.
- Cada seção termina ancorada no uso prático: o que muda na vida de quem usa.

#### 1.1 Clareza sem burocracia

Escreva cada seção nesta ordem:

1. o título declara o estado, a decisão, ou o problema;
2. o parágrafo explica a causa ou a evidência concreta;
3. o fechamento informa o efeito prático ou a próxima ação.

Use voz ativa, afirmações positivas, termos específicos, e apenas as palavras
necessárias. Preserve o português natural: clareza não significa formalidade
corporativa. A personalidade vem dos exemplos e do ritmo, não de frases de
efeito, provocações ao leitor, ou comentários sobre a própria honestidade.

```text
Evite: Onde estamos, sem teatro de “quase pronto”.
Use:  O motor funciona em pequena escala; a execução completa continua bloqueada.
```

### 2. Escolher direção estética e COMPROMETER

Três anatomias prontas em `references/receita.md` (ler antes de codar):

| Direção | Vibe | Quando |
|---|---|---|
| **A — Manual de operação** | Brutalista impresso: display geométrica caps, plaquinha de documento (`EF-QS-001 · Rev 1.10`), rail de navegação, bordas 1.5px pretas, sombra offset sólida, 1 cor de sinal quente | Passo-a-passo, quickstart, onboarding, runbook |
| **B — Editorial serif** | Revista calma: serif com caráter em títulos grandes, numerais fantasma vazados, hairlines, faixa "na prática" em itálico, carimbo no fechamento | Narrativa (problema→solução), relato de sprint, pitch, explicação de decisão |
| **C — Prova final / Wireframe de verificação** | Delta sobre a Direção A: mesmos tokens/rail/callout, mas o documento nasce VAZIO (slots `▢`) organizado por PR/merge real, e o MESMO arquivo vira a prova preenchida depois — ver §2.1 | Checklist de re-verificação de trabalho já mergeado, antes de ratificar decisões ou fechar uma rodada |
| **D — Prancha de decisão** | Planta baixa, não impresso: papel técnico, linha de construção 1px, UMA cor de revisão. N opções da MESMA estrutura desenhadas lado a lado em caixas cinzas, com a região em disputa hachurada e o custo de cada uma embaixo — ver §2.2 | Escolher entre formas de organizar algo que ainda não existe: onde mora uma informação, o que uma aba promete, qual layout uma feature ganha |

Misturar A e B é permitido; ficar em cima do muro não. Escolher UMA dominante. A
Direção C é sempre um delta explícito sobre a A (não escolher "C pura" do zero —
ela importa os tokens/primitivos de A e adiciona só o que é próprio do gênero).

**A Direção D não é delta de ninguém** — ela tem tokens próprios, porque o
assunto dela é outro. A, B e C descrevem coisas que existem; D existe justamente
quando o conteúdo AINDA NÃO existe e o que está em jogo é a estrutura. Um
documento não deve nascer em D e virar A depois: quando a decisão é tomada, o
que se escreve é um documento novo, do gênero certo.

#### 2.1 Direção C em detalhe — o gênero "prova final"

Diferença fundamental das outras duas: A e B descrevem algo que já existe pra um
leitor entender. C é um **artefato de trabalho de duas fases**: nasce como
wireframe vazio (Rev. 0) ANTES da rodada de captura de prova, e o MESMO arquivo é
editado depois pra virar o relatório de prova real (Rev. 1) — não se cria um
segundo documento.

Regras do gênero:

- **Fonte do conteúdo é sempre real, nunca inventada.** Cada seção do documento
  corresponde a 1 PR/merge real já integrado. O "o quê" de cada prova vem do
  corpo do PR ou do commit, o comando de reprodução é um comando real do
  projeto (`npm test -- ...`, `npm run ci:queue -- e2e -- ...`, etc.), o
  critério de aceite é extraído do que o PR/issue prometeu — nunca redigido do
  zero por estética.
- **Organização por fonte de verdade**: 1 seção por PR (numerada `step-num`
  tipo "01", "02", "03" — reusa o mesmo primitivo da Direção A), cada uma
  citando o "pack existente" (caminho de prova anterior, se houver) antes de
  listar as re-execuções novas. Depois das seções por PR, uma seção
  **"Gates transversais"** para critérios que valem pro branch/entrega inteira,
  não por PR individual (ex.: CI completo local, deploy publicado, decisões
  pendentes respondidas).
- **Card `.prova`** é o primitivo central do gênero (ver `references/receita.md`
  §10 pro CSS/HTML completo): id curto (`676-A`), `.status-slot` que começa
  vazio (`▢`) e vira `passed`/`failed` depois, corpo em grid 2 colunas — texto
  do "o quê" + comando real + critério de aceite (`.where`, mesmo primitivo já
  documentado em A) de um lado, `.print-slot` (caixa tracejada vazia, com texto
  tipo "▢ N prints — descrição do que vai entrar") do outro.
- **`.wire-banner`** logo no topo (borda tracejada na cor de sinal) declara
  explicitamente "isto é um wireframe" e a regra de validade do projeto (ex.:
  print sem JSON de status não conta; falha não gera screenshot válido) — isso
  não é genérico, é a doutrina de prova real do projeto sendo documentada, não
  uma frase decorativa.
- **Convenção de versão no `doc-plate`**: `Rev. 0 · WIREFRAME` no nascimento,
  vira `Rev. 1` (ou seguinte) quando os slots forem preenchidos com prova real.
  O fechamento do documento (bloco `.ia` invertido, mesmo primitivo de A) lista
  explicitamente "o que falta para a Rev. 1" — não é um "próximos passos"
  genérico, é o checklist literal de slots ainda vazios.
- **Exceção deliberada à Lei do Estilo #1** (ver "Anti-patterns" abaixo): a
  Direção A/B proíbem screenshot real no lugar de diorama. A Direção C
  inverte isso de propósito no `.print-slot` — quando a Rev. 1 é preenchida, o
  que entra ali É um screenshot real (a prova em si), não um diorama. O
  wireframe (Rev. 0) continua com o placeholder tracejado; só a versão
  preenchida quebra a regra geral, e só nesse slot específico.

#### 2.2 Direção D em detalhe — o gênero "prancha de decisão"

**A pergunta que define o gênero:** o conteúdo já existe?

- **Existe** → diorama (A/B). Você mostra a cena real, com o texto real dentro.
- **Não existe ainda, e o que está em jogo é onde as coisas ficam** → prancha (D).

Essa distinção não é estilística, é de honestidade. O diorama vive de conteúdo
literal — a mensagem de erro do sistema, o nome do botão. Se você desenhar um
diorama de algo que ainda não foi decidido, é obrigado a **inventar o conteúdo
para ilustrar**, e o leitor passa a debater o texto inventado em vez da
estrutura. A caixa cinza da prancha diz o que precisa ser dito: *aqui vai
conteúdo, e não é isso que estamos decidindo agora.*

Regras do gênero:

- **N opções da MESMA estrutura, nunca N coisas diferentes.** Se as opções não
  são comparáveis lado a lado, não é prancha — é um documento comum com seções.
  As mini-telas têm que ter o mesmo esqueleto (as mesmas abas, o mesmo corpo)
  para o olho pegar só a diferença.
- **Uma só cor, e ela marca a região em disputa.** Todo o resto é papel, tinta e
  cinza. Use hachura diagonal (`repeating-linear-gradient`) na área que está
  sendo decidida — é o vocabulário de revisão de planta. Se duas coisas estão
  coloridas, o leitor não sabe onde olhar.
- **Cada opção termina com o CUSTO, não com a opinião.** O que muda para quem
  usa: quantos cliques, o que quebra, o que precisa ser refeito. A recomendação
  entra como borda destacada + rótulo `★`, e ela é **uma** — recomendar duas é
  não recomendar.
- **A opção errada aparece riscada quando ajuda.** Se existe um jeito óbvio e
  ruim de fazer (a faixa de status que vira parágrafo, a tabela que estoura),
  desenhe-o em `<s>` com uma linha dizendo por que falha. Vale mais que
  descrever a regra.
- **Cotas em vez de legendas.** Sob cada prancha, uma linha mono curta com o que
  o desenho tem de medida real ("bloco de topo, dentro da aba" · "90 entradas,
  35 destacadas"). É o que separa prancha de mockup bonito.
- **Fecha com a pergunta, numerada.** O documento existe para o leitor
  responder. O último bloco é o que você precisa dele, item a item — incluindo
  o que **você não sabe desenhar** e por quê. Prancha que não pergunta nada é
  apresentação.
- **Cabeçalho declara revisão.** `WIREFRAME · REV 1`, e a revisão sobe quando o
  leitor corrige o entendimento. A segunda revisão abre com um bloco curto
  **"o que mudou nesta revisão"** — porque a prancha é conversa, não entrega.
- **Nunca é código vivo.** Prancha aprovada é intenção de produto: o que existe,
  onde fica. O idioma visual da implementação vem dos componentes reais do
  sistema, sempre. Copiar o desenho da prancha para dentro do produto gera
  botão que não existe e layout que ninguém tem — mesma armadilha do mockup.

### 3. Montar o esqueleto

Anatomia comum às duas direções principais (A e B; C é delta sobre A, ver §2.1;
**D tem anatomia própria — ver §2.2 e `receita.md` §11**):

```
header/doc-plate (metadata mono)  →  capa (título gigante + 1 parágrafo)
→ [nav rail, se passo-a-passo]
→ seções alternadas (texto ⇄ diorama, zigue-zague esquerda/direita)
→ [callout invertido escuro, se houver 1 destaque]
→ fechamento (frase-épico + carimbo ou checklist)  →  footer mono
```

### 4. Desenhar 1 diorama por seção

> **Antes: é diorama ou é prancha?** Diorama conta UMA cena de algo que existe,
> com texto real dentro. Se o que você precisa mostrar são **opções comparáveis
> de uma estrutura ainda não decidida**, o gênero é a Direção D (§2.2) — e
> insistir no diorama te obriga a inventar conteúdo para ilustrar.

O diorama é a alma. Regras que fazem ele funcionar:

- **Conta UMA cena**, não decora. "Toggle ligado → template riscado sumindo" é cena;
  quatro caixas genéricas é decoração.
- **3 a 6 elementos**, nunca mais. Diorama lotado vira screenshot ruim.
- Vive num **canvas quadriculado** (grid 22px) com **plaquinha `Fig. N — nome`**
  no canto (via `data-fig` + `::after`). A plaquinha é o que faz parecer manual.
- Elementos com **borda dura 1.5px na cor da tinta + sombra offset sólida**
  (`4px 4px 0`), sem blur. Fantasmas/excluídos: borda dashed, sem sombra.
- **Texto real dentro**: a mensagem de erro literal do sistema, o nome do botão real.
- Catálogo completo de primitivos (ficha, modal, toast, toggle, fluxo, legenda de
  estados, mini-gráfico, calendário, carimbo, card de prova…) em
  `references/receita.md` — copiar e adaptar, não reinventar.

### 5. Motion — pouco e delicioso

- Entrada: `rise` com stagger (`animation-delay` escalonado) no load, ou
  IntersectionObserver de 6 linhas para revelar no scroll.
- **Uma** micro-delícia por documento: caret piscando num input, carimbo que estampa
  com overshoot (`cubic-bezier(.2,1.6,.4,1)`), item oculto que some e volta em loop.
  Mais de uma vira parque de diversões.
- `@media print`: matar animações, garantir `break-inside: avoid`.

### 6. Verificar antes de entregar

- Abrir mentalmente em 390px: grid vira coluna? zigue-zague reordena?
- Todo texto sobre papel tem contraste real? (muted ≠ ilegível)
- Todo destaque que mudou o fundo definiu também uma cor de texto legível?
- O texto declara estado, evidência, e ação sem soar burocrático ou performático?
- A plaquinha Fig. está em todos os dioramas? Numeração sequencial?
- O leitor não-técnico entende cada seção sem glossário?
- Na Direção D: as opções têm o MESMO esqueleto (dá para comparar de olho)? Só
  UMA região está colorida? Cada uma termina em custo, não em opinião? Existe
  exatamente uma recomendação? O documento fecha com a pergunta numerada?
- Na Direção C: todo `.prova` tem comando real + critério de aceite real? Nenhum
  slot foi preenchido com dado inventado?

## As leis do estilo

1. **Tipografia com caráter.** Nunca Inter/Roboto/Arial/system genérica. Direção A:
   display geométrica (Futura, Avenir Next) + mono de verdade. Direção B: serif
   editorial (Instrument Serif, Fraunces) + grotesk limpa + mono para metadata.
   Direção C herda a tipografia de A. Direção D usa **uma família técnica só, em
   dois cortes** (mono para cota e label, sans irmã para o corpo — IBM Plex é o
   par de referência): planta baixa não mistura vozes. Google Fonts ou fontes de
   sistema com personalidade.
2. **Papel + tinta + UMA cor de sinal.** Papel quente (`#FAF9F5`/`#F3EFE6`), tinta
   quase-preta, um sinal (laranja quente, verde). Cores extras só quando SÃO dado
   (4 estados = 4 pontinhos coloridos) — nunca decoração.
3. **Labels e metadata sempre mono, uppercase, letter-spacing largo.** É o que dá
   cheiro de documento técnico impresso.
4. **Bordas duras, sombras sólidas.** 1–1.5px na tinta; sombra `Npx Npx 0` sem blur.
   Zero border-radius grande, zero gradiente decorativo, zero glassmorphism.
5. **Numerais gigantes vazados** (`-webkit-text-stroke` + fill transparente) como
   âncora visual de cada seção. **Na Direção D, não** — a âncora ali é a legenda
   de prancha (`FIG. 1B`), e numeral gigante rouba o olho da região hachurada.
6. **Um arquivo só.** HTML autocontido: CSS inline no `<head>`, JS mínimo inline,
   sem build, sem CDN além de fontes. Abre com dois cliques pra sempre.

## Anti-patterns

- **Prancha (D) que vira apresentação:** N opções e nenhuma pergunta no fim, ou
  duas recomendações — que é o mesmo que nenhuma.
- **Diorama de coisa não decidida:** conteúdo inventado para preencher a cena. O
  leitor debate o texto falso em vez da estrutura. Use a Direção D.
- Screenshot real no lugar de diorama — pesa, envelhece, quebra o estilo. **Exceção
  deliberada:** o `.print-slot` da Direção C, na Rev. 1 preenchida — ali o
  screenshot real É o conteúdo, não um substituto de diorama (ver §2.1).
- Diorama que não conta cena (caixas com lorem ipsum conceitual).
- Card dentro de card, 5 cores competindo, gradiente roxo sobre branco.
- Tom de manual corporativo. Didático fala como gente: "uma vez só — nunca mais
  volta aqui".
- Parágrafos longos. O texto acompanha o diorama, não compete com ele.
- Na Direção C: preencher um `.prova` com resultado inventado, comando genérico
  ou critério de aceite vago — se a claim não vem de um PR/commit real, não
  entra no documento. Um slot `▢` vazio é honesto; um slot preenchido com
  ficção não é.

## Referência obrigatória

Antes de escrever o CSS, ler **`references/receita.md`** (Direção D: §11) — contém os tokens das
três direções, o CSS completo do canvas de diorama, o catálogo de primitivos
prontos para copiar (incluindo o card `.prova` da Direção C) e a anatomia de
página de cada uma.
