---
name: html-didatico
description: Cria documentos HTML visuais e didáticos — manuais, quickstarts, one-pagers, murais de status, explicações de feature ou de projeto para sócio, cliente, equipe ou família — no estilo editorial impresso com "dioramas" — mini-interfaces falsas desenhadas em CSS puro (fichas, modais, toggles, toasts, fluxos, carimbos) que tornam o documento fofo e fácil de entender. Use sempre que o usuário pedir um HTML bonito/fofo/didático, um manual visual, um quickstart, um documento para leigo entender algo técnico, um resumo de sprint/feature em página única, ou mencionar "aquele estilo de HTML com figurinhas/dioramas". Também quando pedir para transformar uma explicação técnica em algo apresentável. Inclui também a Direção C — um wireframe de "prova final" (checklist de verificação pós-merge que vira o próprio relatório de prova quando preenchido) — use quando o pedido for "monta um checklist de verificação dos PRs", "wireframe de prova final", "documento pra provar que os merges funcionam de verdade", ou qualquer variação de organizar a re-verificação de trabalho já mergeado antes de fechar decisões.
---

# HTML Didático — documentos editoriais com dioramas de CSS

Um documento desse estilo tem duas metades inseparáveis: **layout de impresso** (papel,
tinta, tipografia com caráter, hairlines, numerais gigantes) e **dioramas** — pequenas
cenas de interface desenhadas só com HTML+CSS, que mostram o conceito em vez de
descrevê-lo. O resultado parece um manual de operação bem diagramado, não um site.

O leitor-alvo quase sempre é um **não-técnico** (sócio, cliente, família). O documento
falha se precisar de tradutor do lado.

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

### 2. Escolher direção estética e COMPROMETER

Três anatomias prontas em `references/receita.md` (ler antes de codar):

| Direção | Vibe | Quando |
|---|---|---|
| **A — Manual de operação** | Brutalista impresso: display geométrica caps, plaquinha de documento (`EF-QS-001 · Rev 1.10`), rail de navegação, bordas 1.5px pretas, sombra offset sólida, 1 cor de sinal quente | Passo-a-passo, quickstart, onboarding, runbook |
| **B — Editorial serif** | Revista calma: serif com caráter em títulos grandes, numerais fantasma vazados, hairlines, faixa "na prática" em itálico, carimbo no fechamento | Narrativa (problema→solução), relato de sprint, pitch, explicação de decisão |
| **C — Prova final / Wireframe de verificação** | Delta sobre a Direção A: mesmos tokens/rail/callout, mas o documento nasce VAZIO (slots `▢`) organizado por PR/merge real, e o MESMO arquivo vira a prova preenchida depois — ver §2.1 | Checklist de re-verificação de trabalho já mergeado, antes de ratificar decisões ou fechar uma rodada |

Misturar A e B é permitido; ficar em cima do muro não. Escolher UMA dominante. A
Direção C é sempre um delta explícito sobre a A (não escolher "C pura" do zero —
ela importa os tokens/primitivos de A e adiciona só o que é próprio do gênero).

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

### 3. Montar o esqueleto

Anatomia comum às duas direções principais (A e B; C é delta sobre A, ver §2.1):

```
header/doc-plate (metadata mono)  →  capa (título gigante + 1 parágrafo)
→ [nav rail, se passo-a-passo]
→ seções alternadas (texto ⇄ diorama, zigue-zague esquerda/direita)
→ [callout invertido escuro, se houver 1 destaque]
→ fechamento (frase-épico + carimbo ou checklist)  →  footer mono
```

### 4. Desenhar 1 diorama por seção

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
- A plaquinha Fig. está em todos os dioramas? Numeração sequencial?
- O leitor não-técnico entende cada seção sem glossário?
- Na Direção C: todo `.prova` tem comando real + critério de aceite real? Nenhum
  slot foi preenchido com dado inventado?

## As leis do estilo

1. **Tipografia com caráter.** Nunca Inter/Roboto/Arial/system genérica. Direção A:
   display geométrica (Futura, Avenir Next) + mono de verdade. Direção B: serif
   editorial (Instrument Serif, Fraunces) + grotesk limpa + mono para metadata.
   Direção C herda a tipografia de A. Google Fonts ou fontes de sistema com
   personalidade.
2. **Papel + tinta + UMA cor de sinal.** Papel quente (`#FAF9F5`/`#F3EFE6`), tinta
   quase-preta, um sinal (laranja quente, verde). Cores extras só quando SÃO dado
   (4 estados = 4 pontinhos coloridos) — nunca decoração.
3. **Labels e metadata sempre mono, uppercase, letter-spacing largo.** É o que dá
   cheiro de documento técnico impresso.
4. **Bordas duras, sombras sólidas.** 1–1.5px na tinta; sombra `Npx Npx 0` sem blur.
   Zero border-radius grande, zero gradiente decorativo, zero glassmorphism.
5. **Numerais gigantes vazados** (`-webkit-text-stroke` + fill transparente) como
   âncora visual de cada seção.
6. **Um arquivo só.** HTML autocontido: CSS inline no `<head>`, JS mínimo inline,
   sem build, sem CDN além de fontes. Abre com dois cliques pra sempre.

## Anti-patterns

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

Antes de escrever o CSS, ler **`references/receita.md`** — contém os tokens das
três direções, o CSS completo do canvas de diorama, o catálogo de primitivos
prontos para copiar (incluindo o card `.prova` da Direção C) e a anatomia de
página de cada uma.
