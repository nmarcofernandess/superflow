# Receita — tokens, anatomias e catálogo de dioramas

Copiar e adaptar. Os valores são ponto de partida calibrado, não camisa de força —
mas o espírito (borda dura, sombra sólida, mono nas labels, quadriculado no canvas)
é inegociável.

## Índice

1. Tokens — Direção A (manual de operação)
2. Tokens — Direção B (editorial serif)
3. Base comum (reset, reveal, print)
4. Anatomia A — peças de página
5. Anatomia B — peças de página
6. O canvas de diorama (`.vis`/`.fig`)
7. Catálogo de primitivos de diorama
8. Micro-delícias (animações)
9. Snippet de reveal por scroll
10. Anatomia C — Prova Final / Wireframe de Verificação
11. Anatomia D — Prancha de Decisão

---

## 1. Tokens — Direção A (manual de operação)

```css
:root {
  --paper: #f3efe6;        /* papel kraft claro */
  --paper-2: #ece7da;      /* papel sombreado */
  --ink: #191613;
  --ink-soft: #4f4a42;
  --ink-faint: #8a8377;
  --signal: #e84e0f;       /* laranja quente — trocar por 1 cor da marca */
  --signal-soft: #f9ddd0;
  --ok: #2c6e49;
  --rule: #d6cfc0;
  --display: 'Futura', 'Avenir Next', 'Century Gothic', 'Trebuchet MS', sans-serif;
  --mono: 'SF Mono', 'Menlo', 'Cascadia Code', 'Consolas', monospace;
}
body {
  font-family: var(--display);
  background: var(--paper);
  color: var(--ink);
  line-height: 1.5;
  /* textura de papel: scanlines + luz no topo */
  background-image:
    repeating-linear-gradient(0deg, transparent 0 2px, rgba(25,22,19,.012) 2px 4px),
    radial-gradient(ellipse 120% 90% at 50% -10%, rgba(255,255,255,.5), transparent 60%);
}
.page { max-width: 880px; margin: 0 auto; padding: 0 32px 96px; }
```

## 2. Tokens — Direção B (editorial serif)

```css
/* Google Fonts: Instrument Serif (ital) + Instrument Sans — ou Fraunces + Archivo */
:root {
  --paper: #FAF9F5;
  --paper-2: #F2F0E9;
  --ink: #161815;
  --ink-soft: #2E332F;
  --muted: #6E7A72;
  --hair: #E3E2DA;
  --accent: #0E9F6E;                        /* 1 cor de sinal */
  --accent-soft: rgba(14,159,110,.07);
  --alert: #C2493F;                         /* só para erro DENTRO de diorama */
  --serif: "Instrument Serif", Georgia, serif;
  --sans: "Instrument Sans", "Helvetica Neue", sans-serif;
  --mono: "SF Mono", ui-monospace, Menlo, monospace;
}
body { background: var(--paper); color: var(--ink); font-family: var(--sans);
       font-size: 17px; line-height: 1.55; -webkit-font-smoothing: antialiased; }
/* B usa página larga (6vw de margem) em vez de coluna central */
```

## 3. Base comum

```css
* { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; }

/* reveal no load (direção A usa classes de delay) */
@keyframes rise { from { opacity: 0; transform: translateY(18px); } to { opacity: 1; transform: none; } }
.r  { animation: rise .7s cubic-bezier(.2,.7,.2,1) both; }
.d1 { animation-delay: .05s } .d2 { animation-delay: .15s } .d3 { animation-delay: .25s }
.d4 { animation-delay: .35s } .d5 { animation-delay: .45s }

@media print {
  .r, .reveal, .stamp { animation: none !important; opacity: 1 !important; transform: none !important; }
  section { break-inside: avoid; }
  body { background: #fff; }
}
```

Todo destaque que aplica um fundo deve definir também a cor do texto. Fundo
claro usa tinta escura; fundo escuro usa tinta clara. Nunca dependa da cor
herdada do container:

```css
.inline-mark { background: var(--paper-2); color: var(--ink); padding: 2px 5px; }
```

## 4. Anatomia A — peças de página

**Doc-plate** (metadata de documento — o "carimbo de registro" no topo):

```html
<div class="doc-plate">
  <span>Manual de operação <b>EF-QS-001</b></span>
  <span>Rev. 1.10 · 2026</span>
</div>
```
```css
.doc-plate { display: flex; justify-content: space-between; font-family: var(--mono);
  font-size: 11px; letter-spacing: .12em; color: var(--ink-soft); text-transform: uppercase;
  border: 1px solid var(--ink); padding: 8px 14px; margin-bottom: 48px; }
.doc-plate b { color: var(--signal); }
```

**Título de capa** — display caps gigante + subtítulo fino:

```css
h1 { font-size: clamp(44px, 8vw, 76px); font-weight: 700; letter-spacing: -.02em;
     line-height: .95; text-transform: uppercase; }
h1 .thin { font-weight: 400; display: block; font-size: .42em; letter-spacing: .14em;
           margin-top: 14px; color: var(--ink-soft); }
header { padding: 56px 0 40px; border-bottom: 3px solid var(--ink); }
```

**Rail de navegação** (grid de âncoras, hover invertido):

```css
.rail { display: grid; grid-template-columns: repeat(6, 1fr); border: 1px solid var(--ink);
  border-top: none; font-family: var(--mono); font-size: 10px; letter-spacing: .08em;
  text-transform: uppercase; }
.rail a { color: var(--ink-soft); text-decoration: none; padding: 10px 6px 12px;
  text-align: center; border-right: 1px solid var(--rule); transition: .15s; }
.rail a b { display: block; font-size: 15px; color: var(--ink); }
.rail a:hover { background: var(--ink); color: var(--paper); }
.rail a:hover b { color: var(--signal); }
```

**Step alternado** (texto ⇄ diorama em zigue-zague):

```css
.step { display: grid; grid-template-columns: 1fr 1fr; gap: 48px; padding: 64px 0;
        border-bottom: 1px solid var(--rule); align-items: center; }
.step:nth-child(even) .step-text { order: 2; }
.step:nth-child(even) .step-vis  { order: 1; }
.step-num { font-size: 88px; font-weight: 700; line-height: 1; color: transparent;
            -webkit-text-stroke: 1.5px var(--ink); letter-spacing: -.03em; }
```

**Localizador "onde"** (ancora a instrução na UI real):

```html
<div class="where"><span>onde →</span> Menu lateral · topo · Empresa</div>
```
```css
.where { margin-top: 18px; font-family: var(--mono); font-size: 11.5px; color: var(--ink);
  background: var(--paper-2); border-left: 3px solid var(--signal); padding: 8px 12px;
  display: inline-block; }
.where span { color: var(--ink-faint); }
```

**Callout invertido** (bloco escuro de destaque, com quadriculado fantasma e
mensagens estilo terminal):

```css
.ia { margin: 72px 0; background: var(--ink); color: var(--paper); padding: 44px 40px;
      position: relative; overflow: hidden; }
.ia::before { content: ''; position: absolute; inset: 0;
  background: linear-gradient(rgba(243,239,230,.05) 1px, transparent 1px),
              linear-gradient(90deg, rgba(243,239,230,.05) 1px, transparent 1px);
  background-size: 22px 22px; }
.ia > * { position: relative; }
.ia .msg { font-family: var(--mono); font-size: 12px; background: rgba(243,239,230,.08);
  border: 1px solid rgba(243,239,230,.18); border-left: 3px solid var(--signal);
  padding: 10px 14px; }
.ia .msg::before { content: '> '; color: var(--signal); }
```

## 5. Anatomia B — peças de página

**Capa serif** com itálico colorido:

```css
.cover h1 { font-family: var(--serif); font-weight: 400;
  font-size: clamp(52px, 8.5vw, 108px); line-height: 1; max-width: 14ch; }
.cover h1 em { font-style: italic; color: var(--accent); }
```

**Numeral fantasma** (marca d'água da seção):

```css
.slice .num { position: absolute; top: 3vh; right: 3vw; font-family: var(--serif);
  font-size: clamp(140px, 20vw, 270px); line-height: 1; color: transparent;
  -webkit-text-stroke: 1px var(--hair); user-select: none; pointer-events: none; }
.slice:nth-of-type(even) .num { right: auto; left: 3vw; }
```

**Kicker + labels** (mono/uppercase é o esqueleto informacional):

```css
.kicker { font-size: 12px; font-weight: 600; letter-spacing: .22em;
          text-transform: uppercase; color: var(--accent); }
```

**Faixa "na prática"** (a âncora didática — serif itálico sobre fundo accent suave):

```css
.pratica { border-left: 2px solid var(--accent); background: var(--accent-soft);
           padding: 22px 28px; }
.pratica p { font-family: var(--serif); font-style: italic; font-size: 23px;
             line-height: 1.35; max-width: 58ch; }
```

## 6. O canvas de diorama

Todo diorama vive nisto. O quadriculado + a plaquinha Fig. são o que transformam
divs soltas em "figura de manual":

```css
.fig {
  position: relative;
  border: 1px solid var(--ink);
  background:
    linear-gradient(rgba(22,24,21,.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(22,24,21,.04) 1px, transparent 1px);
  background-size: 22px 22px;
  background-color: #FFFFFC;               /* papel mais claro que a página */
  padding: 30px 28px;
  display: flex; flex-direction: column; justify-content: center; gap: 14px;
  min-height: 240px;
}
.fig::after {
  content: attr(data-fig);                  /* <figure class="fig" data-fig="Fig. 1 — cadastro"> */
  position: absolute; bottom: -1px; right: -1px;
  font-family: var(--mono); font-size: 9.5px; letter-spacing: .1em;
  text-transform: uppercase;
  background: var(--ink); color: var(--paper); padding: 4px 12px;
}
```

## 7. Catálogo de primitivos de diorama

Sombra-assinatura de todos os elementos "vivos": `box-shadow: 4px 4px 0 rgba(ink, .1)`.
Elementos mortos/fantasma: borda `dashed`, sem sombra, cor muted.

**Card de UI genérico + input com caret piscando:**

```css
.ui-card { background: #fff; border: 1.5px solid var(--ink);
           box-shadow: 4px 4px 0 rgba(25,22,19,.12); padding: 14px 16px; }
.ui-label { font-family: var(--mono); font-size: 9.5px; letter-spacing: .14em;
            text-transform: uppercase; color: var(--ink-faint); margin-bottom: 6px; }
.ui-input { border-bottom: 2px solid var(--ink); font-size: 16px; font-weight: 600; }
.ui-input .caret { display: inline-block; width: 2px; height: 16px;
  background: var(--signal); vertical-align: -2px; animation: blink 1.1s steps(1) infinite; }
@keyframes blink { 50% { opacity: 0 } }
```

**Botão e pills de opção:**

```css
.ui-btn { display: inline-block; background: var(--ink); color: var(--paper);
  font-family: var(--mono); font-size: 11px; letter-spacing: .12em;
  text-transform: uppercase; padding: 9px 18px; }
.ui-btn.primary { background: var(--signal); color: #fff; }
.pill { font-family: var(--mono); font-size: 11px; border: 1.5px solid var(--ink);
        padding: 6px 14px; background: #fff; }
.pill.on { background: var(--signal); border-color: var(--signal); color: #fff; }
```

**Ficha de pessoa/registro (avatar + nome + tag de estado):**

```html
<div class="ficha">
  <div class="who">
    <div class="avatar">MS</div>
    <div><b>Maria Souza</b><small>CPF 111.222.333-44</small></div>
  </div>
  <span class="tag ok">ativa</span>
</div>
<div class="ficha ghost"><!-- mesma pessoa, excluída --></div>
```
```css
.ficha { background: #fff; border: 1.5px solid var(--ink);
  box-shadow: 4px 4px 0 rgba(22,24,21,.1); padding: 13px 16px;
  display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.ficha .who { display: flex; align-items: center; gap: 12px; }
.avatar { width: 34px; height: 34px; border-radius: 50%; border: 1.5px solid var(--ink);
  background: var(--paper-2); display: grid; place-items: center;
  font-size: 12px; font-weight: 700; }
.ficha b { font-size: 15px; display: block; line-height: 1.2; }
.ficha small { font-family: var(--mono); font-size: 10.5px; color: var(--muted); }
.ficha.ghost { border-style: dashed; box-shadow: none; background: transparent;
               color: var(--muted); }
.ficha.ghost .avatar { border-style: dashed; background: transparent; }
```

**Tags de estado:**

```css
.tag { font-family: var(--mono); font-size: 9.5px; letter-spacing: .06em;
  text-transform: uppercase; border: 1px solid var(--hair); background: var(--paper-2);
  padding: 4px 9px; white-space: nowrap; }
.tag.ok  { border-color: var(--accent); color: var(--accent); background: var(--accent-soft); }
.tag.err { border-color: var(--alert);  color: var(--alert);  background: #F9E5E2; }
.tag.off { border-color: var(--muted);  color: var(--muted);  background: transparent; }
```

**Toast de erro (usar a mensagem literal do sistema):**

```css
.toast { display: flex; align-items: center; gap: 10px; border: 1.5px solid var(--alert);
  background: #F9E5E2; padding: 11px 14px; font-family: var(--mono); font-size: 12px;
  color: var(--alert); box-shadow: 4px 4px 0 rgba(194,73,63,.12); }
.toast .x { width: 18px; height: 18px; border: 1.5px solid var(--alert);
  border-radius: 50%; display: grid; place-items: center; font-size: 11px; }
```

**Fluxo (nós + setas tracejadas):**

```html
<div class="fluxo">
  <span class="no">admin devolve</span><span class="seta"></span>
  <span class="no">arquivado</span><span class="seta"></span>
  <span class="no">você reativa</span>
</div>
```
```css
.fluxo { display: flex; align-items: center; gap: 8px; font-family: var(--mono); font-size: 11px; }
.fluxo .no { border: 1.5px solid var(--ink); background: #fff; padding: 7px 12px;
             letter-spacing: .06em; text-transform: uppercase; white-space: nowrap; }
.fluxo .seta { flex: 1; min-width: 20px; height: 1.5px;
  background: repeating-linear-gradient(90deg, var(--ink) 0 6px, transparent 6px 11px); }
```

**Mini-modal (título, corpo, botões):**

```css
.modal { background: #fff; border: 1.5px solid var(--ink);
         box-shadow: 6px 6px 0 rgba(22,24,21,.12); }
.modal .mhead { display: flex; align-items: center; gap: 8px;
  border-bottom: 1.5px solid var(--ink); padding: 9px 14px; font-family: var(--mono);
  font-size: 10.5px; letter-spacing: .1em; text-transform: uppercase; color: var(--muted); }
.modal .mhead i { width: 9px; height: 9px; border-radius: 50%; border: 1.5px solid var(--ink); }
.modal .mbody { padding: 16px; }
.modal .mfoot { display: flex; gap: 10px; justify-content: flex-end; padding: 0 16px 16px; }
.btn { font-family: var(--mono); font-size: 10.5px; letter-spacing: .1em;
  text-transform: uppercase; padding: 8px 14px; border: 1.5px solid var(--ink);
  background: #fff; }
.btn.primary { background: var(--accent); border-color: var(--accent); color: #fff; }
```

**Legenda de estados (dot + termo + significado):**

```css
.estado { display: flex; align-items: center; gap: 14px; background: #fff;
  border: 1.5px solid var(--ink); box-shadow: 4px 4px 0 rgba(22,24,21,.08);
  padding: 11px 16px; }
.estado .dot { width: 11px; height: 11px; border-radius: 50%; }
.estado b { font-family: var(--mono); font-size: 12px; letter-spacing: .1em; min-width: 96px; }
.estado span { font-size: 14px; color: var(--muted); }
```

**Toggle/switch ligado:**

```css
.switch { width: 40px; height: 22px; border: 1.5px solid var(--accent);
  background: var(--accent); border-radius: 99px; position: relative; }
.switch::after { content: ''; position: absolute; top: 2px; right: 2px;
  width: 14px; height: 14px; background: #fff; border-radius: 50%; }
```

**Barra de faixa (horário/progresso com hachura):**

```css
.hours-track { flex: 1; height: 14px; border: 1.5px solid var(--ink); background: #fff;
               position: relative; }
.hours-fill { position: absolute; left: 28%; right: 12%; top: 2px; bottom: 2px;
  background: repeating-linear-gradient(45deg, var(--ink) 0 4px, transparent 4px 8px); }
```

**Mini-gráfico de barras:**

```css
.bars { display: flex; align-items: flex-end; gap: 10px; height: 120px; }
.bar { flex: 1; display: flex; flex-direction: column; justify-content: flex-end;
       align-items: center; gap: 6px; height: 100%; }
.bar i { width: 100%; background: #fff; border: 1.5px solid var(--ink);
         border-bottom-width: 3px; display: block; }
.bar.hot i { background: var(--signal-soft); border-color: var(--signal); }
```

**Mini-calendário 7 colunas (célula marcada = folga/evento):**

```css
.grid7 { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; }
.cell { aspect-ratio: 1; border: 1.5px solid var(--ink); background: #fff;
  display: grid; place-items: center; font-family: var(--mono); font-size: 10.5px;
  font-weight: 700; }
.cell.f { background: var(--signal); border-color: var(--signal); color: #fff; }
```

**Conexão pessoa → destino (avatar + linha tracejada + caixinha):**

```css
.person { display: flex; align-items: center; gap: 12px; }
.person .link { flex: 1; height: 1.5px;
  background: repeating-linear-gradient(90deg, var(--ink) 0 6px, transparent 6px 11px); }
.person .dest { font-family: var(--mono); font-size: 10.5px; background: #fff;
                border: 1.5px solid var(--ink); padding: 5px 10px; }
```

**Item morto/oculto que some em loop (didática de "ocultou, sumiu"):**

```css
.morto { background: #fff; border: 1.5px dashed var(--muted); padding: 13px 16px;
         color: var(--muted); animation: sumiu 3.2s ease-in-out infinite; }
.morto b { text-decoration: line-through; text-decoration-color: var(--alert); }
@keyframes sumiu { 0%, 55% { opacity: 1 } 75%, 85% { opacity: .15 } 100% { opacity: 1 } }
```

## 8. Micro-delícias

**Carimbo circular** (fechamento do documento — estampa com overshoot):

```html
<div class="stamp" aria-label="Piloto B validado em julho de 2026">
  <span>piloto B</span><strong>validado</strong><small>jul 2026</small>
</div>
```
```css
.stamp { flex: 0 0 200px; width: 200px; aspect-ratio: 1; display: flex;
  flex-direction: column; align-items: center; justify-content: center; gap: 6px;
  border-radius: 50%; border: 3px double var(--accent); color: var(--accent);
  transform: rotate(-8deg); font-family: var(--mono); font-size: 11px;
  letter-spacing: .12em; text-transform: uppercase; text-align: center; }
.stamp strong { font-size: 16px; }
.stamp small { font: inherit; letter-spacing: .06em; }
@keyframes stampIn { from { opacity: 0; transform: rotate(-8deg) scale(1.7); }
                     to   { opacity: 1; transform: rotate(-8deg) scale(1); } }
/* disparar quando o container ganhar .in (reveal por scroll) */
.reveal.in .stamp { animation: stampIn .6s cubic-bezier(.2,1.6,.4,1) .35s both; }
```

## 9. Reveal por scroll (JS inteiro do documento)

```html
<script>
  const io = new IntersectionObserver(
    (entries) => entries.forEach((e) => e.isIntersecting && e.target.classList.add('in')),
    { threshold: 0.15 }
  );
  document.querySelectorAll('.reveal').forEach((el) => io.observe(el));
</script>
```

```css
.reveal { opacity: 0; transform: translateY(22px);
  transition: opacity .7s ease, transform .7s cubic-bezier(.16,1,.3,1); }
.reveal.in { opacity: 1; transform: none; }
```

## 10. Anatomia C — Prova Final / Wireframe de Verificação

Delta sobre a Anatomia A (§4) — reusa `.doc-plate`, `.rail`, `.step-num`, `.ia` e
os tokens da §1 sem alteração. O que é próprio do gênero:

**Doc-plate com convenção de revisão** (o rótulo de versão É o estado do
documento — Rev. 0 significa "vazio por desenho", não "rascunho qualquer"):

```html
<div class="doc-plate">
  <span>Prova final de operação <b>PF-054-001</b></span>
  <span>Rev. 0 · WIREFRAME · jul / 2026</span>
</div>
```

**Banner de wireframe** (declara o estado + a regra de validade do projeto —
adaptar o texto da regra pro projeto real, não deixar genérico):

```html
<div class="wire-banner">
  <b>isto é um wireframe.</b> Nenhum slot abaixo está preenchido — cada ▢ vira
  print real (PNG + JSON status=passed) quando a rodada de prova rodar. Regra
  de validade: print sem JSON não conta; falha não gera screenshot válido.
</div>
```
```css
.wire-banner { margin: 26px 0 0; border: 2px dashed var(--signal); background: var(--signal-soft);
  padding: 14px 18px; font-family: var(--mono); font-size: 12px; letter-spacing: .06em;
  color: var(--ink); text-transform: uppercase; }
.wire-banner b { color: var(--signal); }
```

**Card `.prova`** — o primitivo central do gênero. Cabeçalho com id curto e
status vazio, corpo em grid 2 colunas (texto+comando+aceite de um lado,
print-slot do outro):

```html
<div class="prova">
  <div class="prova-head">
    <span class="pid"><b>676-A</b> · pack visual completo re-capturado</span>
    <span class="status-slot">status ▢</span>
  </div>
  <div class="prova-body">
    <div class="prova-text">
      <p class="what">Re-rodar o proof de readiness/lifecycle inteiro contra o
      dev server — os três estados de Food, dirty-close inline, Flow A.</p>
      <div class="cmd">DIETFLOW_PROOF_BASE_URL=http://localhost:3020 \
npm run proof:readiness-lifecycle   <span># 14 shots + logs</span></div>
      <div class="where"><span>aceite →</span> 15/15 JSONs com status=passed</div>
    </div>
    <div class="print-slot">
      <div class="ph"><span><b>▢ 15 prints</b><br>grade-resumo do pack</span></div>
    </div>
  </div>
</div>
```
```css
.prova { border: 1.5px solid var(--ink); background: #fff;
  box-shadow: 4px 4px 0 rgba(25,22,19,.1); margin-bottom: 18px; }
.prova-head { display: flex; justify-content: space-between; align-items: center; gap: 10px;
  border-bottom: 1.5px solid var(--ink); padding: 10px 14px; flex-wrap: wrap; }
.prova-head .pid { font-family: var(--mono); font-size: 11px; letter-spacing: .1em;
  text-transform: uppercase; }
.prova-head .pid b { color: var(--signal); }
.status-slot { font-family: var(--mono); font-size: 9.5px; letter-spacing: .1em; text-transform: uppercase;
  border: 1.5px dashed var(--ink-faint); color: var(--ink-faint); padding: 4px 10px; }
.prova-body { display: grid; grid-template-columns: 1fr 220px; gap: 0; }
.prova-text { padding: 14px 16px; font-size: 14.5px; color: var(--ink-soft); }
.prova-text .what b { color: var(--ink); }
.cmd { margin-top: 10px; font-family: var(--mono); font-size: 11px; background: var(--paper-2);
  border-left: 3px solid var(--signal); padding: 8px 12px; color: var(--ink); overflow-x: auto; white-space: pre; }
.cmd span { color: var(--ink-faint); }
.print-slot { border-left: 1.5px dashed var(--ink-faint); display: grid; place-items: center;
  min-height: 130px; padding: 14px; }
.print-slot .ph { border: 2px dashed var(--ink-faint); color: var(--ink-faint); width: 100%;
  height: 100%; min-height: 100px; display: grid; place-items: center; text-align: center;
  font-family: var(--mono); font-size: 10px; letter-spacing: .1em; text-transform: uppercase;
  line-height: 1.9; padding: 10px; }
.print-slot .ph b { color: var(--signal); font-size: 13px; }
@media (max-width: 760px) {
  .prova-body { grid-template-columns: 1fr; }
  .print-slot { border-left: none; border-top: 1.5px dashed var(--ink-faint); }
}
```

**Preenchimento (Rev. 1)** — quando a prova real é capturada, o mesmo card muda
de estado no lugar: `.status-slot` recebe uma classe de resultado
(ex. `passed`/`failed`, reusando as cores de `.tag.ok`/`.tag.err` do catálogo
§7) e o `.print-slot` recebe a imagem real:

```html
<span class="status-slot passed">passed ✓</span>
...
<div class="print-slot">
  <img src="proofs/676-a-grid.png" alt="grade-resumo do pack 676-A" style="width:100%;height:100%;object-fit:contain">
</div>
```
```css
.status-slot.passed { border-style: solid; border-color: var(--ok); color: var(--ok); }
.status-slot.failed { border-style: solid; border-color: var(--alert, #C2493F); color: var(--alert, #C2493F); }
```

**Organização da página**: 1 seção `.step`-numerada (reusa `.step-num` de A)
por PR/merge, cada uma citando o pack de prova anterior antes de listar
`.prova`s novos; depois, uma seção "Gates transversais" para critérios do
branch/entrega inteira (não por PR); fechamento em `.ia` (mesmo primitivo de
A) listando literalmente os slots que faltam preencher pra virar Rev. 1.


---

## 11. Anatomia D — Prancha de Decisão

Gênero autônomo (não é delta de A). O mundo visual é **planta baixa**: papel
técnico, grafite, linha de construção fina, e a cor do marcador de revisão —
que é literalmente o que o leitor vai fazer no documento.

### 11.1 Tokens

```css
:root{
  --paper:#F7F7F5;      /* papel técnico, levemente quente */
  --ink:#23262B;        /* grafite azulado, não preto puro */
  --ink-soft:#5C626B;
  --rule:#C4C8CE;       /* linha de construção */
  --rule-hard:#9AA0A8;  /* contorno de peça */
  --ghost:#EAECEF;      /* preenchimento de caixa vazia */
  --ghost-2:#DFE2E6;    /* linha de texto simulada */
  --mark:#C2352B;       /* A cor. Só a região em disputa. */
  --mark-soft:rgba(194,53,43,.10);
  --mark-mid:rgba(194,53,43,.34);
  --mono:"IBM Plex Mono",ui-monospace,Menlo,monospace;
  --sans:"IBM Plex Sans",-apple-system,"Segoe UI",sans-serif;
}
```

**Tema escuro vira cianotipia** — não é inversão naive, é o que uma planta faz:
`--paper:#0E2137; --ink:#DCE7F3; --rule:#2E4E73; --ghost:#152D48;
--mark:#FF9585`. Redefina só os tokens, nos três estados (`:root`,
`@media (prefers-color-scheme:dark)` guardado com `:not([data-theme="light"])`,
e `:root[data-theme="dark"]`).

**Sem sombra, sem raio, sem gradiente decorativo.** Prancha que fica bonita
demais faz o leitor avaliar a estética em vez da estrutura.

### 11.2 A mini-tela (`.win`)

O primitivo central: o esqueleto do documento sendo decidido, em cinza.

```html
<div class="win">
  <div class="tabs">
    <div class="tab">1</div><div class="tab on">2 SPECS</div><div class="tab">3</div>
  </div>
  <div class="body-area">
    <div class="zone">
      <span class="zone-lbl">o que está em disputa</span>
      <div class="lane w85"></div><div class="lane w70"></div>
    </div>
    <div class="row w92"></div><div class="row w60"></div>
  </div>
</div>
```

```css
.win{ border:1px solid var(--rule-hard); background:var(--ghost); }
.tabs{ display:flex; border-bottom:1px solid var(--rule-hard); }
.tab{ flex:1; font-family:var(--mono); font-size:8.5px; text-align:center;
      padding:6px 2px; color:var(--ink-soft); border-right:1px solid var(--rule); }
.tab:last-child{ border-right:0 }
.tab.on{ background:var(--paper); color:var(--ink); font-weight:600 }
.body-area{ background:var(--paper); padding:10px; min-height:118px }
.row{ height:9px; background:var(--ghost-2); margin-bottom:6px }  /* texto simulado */
.w92{width:92%} .w80{width:80%} .w60{width:60%} .w45{width:45%}

/* a região em disputa — hachura de revisão */
.zone{
  border:1.5px solid var(--mark);
  background:repeating-linear-gradient(135deg,transparent 0 5px,var(--mark-soft) 5px 10px);
  padding:7px 8px; margin-bottom:8px;
}
.zone-lbl{ font-family:var(--mono); font-size:8.5px; letter-spacing:.1em;
           text-transform:uppercase; color:var(--mark); font-weight:600;
           display:block; margin-bottom:5px }
.lane{ height:7px; background:var(--mark); opacity:.34; margin-bottom:4px }
```

### 11.3 A prancha (`.plan`) — moldura, cota e custo

```html
<article class="plan rec">
  <div class="plan-cap"><span>FIG. 1B</span><span>★ FAIXA FIXA</span></div>
  <div class="draw"> <!-- a .win aqui --> </div>
  <div class="dim">acima das abas — visível de qualquer uma</div>
  <div class="verdict">
    Uma frase do que muda para quem usa.
    <span class="cost">custo · zero clique</span>
  </div>
</article>
```

```css
.plan{ border:1px solid var(--rule-hard); background:var(--paper);
       display:flex; flex-direction:column }
.plan.rec{ border-color:var(--mark); border-width:1.5px }   /* a recomendação, UMA só */
.plan-cap{ font-family:var(--mono); font-size:10px; letter-spacing:.14em;
           text-transform:uppercase; color:var(--ink-soft); padding:7px 10px;
           border-bottom:1px solid var(--rule); display:flex;
           justify-content:space-between; gap:10px }
.plan.rec .plan-cap{ color:var(--mark) }
.draw{ padding:14px 14px 4px; flex:1 }
.dim{ font-family:var(--mono); font-size:10px; color:var(--ink-soft);
      padding:0 14px 12px; display:flex; gap:6px; align-items:baseline }
.dim::before{ content:"↳"; color:var(--mark) }
.verdict{ border-top:1px solid var(--rule); padding:11px 14px 13px;
          font-size:13.5px; color:var(--ink-soft) }
.verdict .cost{ font-family:var(--mono); font-size:10.5px; letter-spacing:.06em;
                text-transform:uppercase; display:block; margin-top:7px; color:var(--mark) }
```

Grid: `.plan-grid{display:grid;gap:22px}` + `@media (min-width:820px){
.plan-grid.three{grid-template-columns:repeat(3,1fr)} }` (e `.two` em 720px).

### 11.4 O jeito errado, riscado

Quando existe um modo óbvio e ruim de fazer, desenhe-o. Vale mais que a regra.

```html
<div class="limit">
  <b>Teto: ~110 caracteres.</b> Passou disso vira parágrafo e ninguém lê.
  <div class="bad">
    <s>AGORA · 105/07 (28 commits, sem PR, teste RED não commitado) e 105/08…</s><br>
    ↑ isso é o detalhe da aba, não da faixa.
  </div>
</div>
```

```css
.limit{ border:1px dashed var(--rule-hard); padding:10px 12px;
        font-family:var(--mono); font-size:11px; color:var(--ink-soft) }
.bad{ margin-top:9px; padding:8px 10px; border-left:2px solid var(--rule-hard);
      font-size:10.5px; line-height:1.65 }
.bad s{ opacity:.65 }
```

### 11.5 Linha do tempo com retorno (`.line` + `.closing`)

Quando a decisão envolve **ordem** e a ordem de fechamento é inversa à de
criação — caso comum em campanha de specs, onde a mais nova destrava a mais
velha. A linha corre `▶`; a barra de fechamento corre `◀` embaixo.

```css
.line{ display:grid; grid-auto-flow:column; grid-auto-columns:1fr; align-items:stretch }
.node{ border:1px solid var(--rule-hard); border-right:0; background:var(--ghost);
       padding:8px 6px 9px; text-align:center }
.node:last-child{ border-right:1px solid var(--rule-hard) }
.node.now{ background:var(--mark-soft); border:1.5px solid var(--mark) }
.node.hold{ background:repeating-linear-gradient(135deg,transparent 0 4px,var(--ghost-2) 4px 8px) }
.node.dest{ border:1.5px solid var(--ink); background:var(--paper) }
.closing{ display:grid; grid-auto-flow:column; grid-auto-columns:1fr }
.cl{ height:26px; position:relative }
.cl-bar{ position:absolute; left:0; right:0; top:9px; height:2px; background:var(--mark-mid) }
.cl-bar.head::before{ content:"◀"; position:absolute; left:-2px; top:-6px;
                      color:var(--mark); font-size:11px }
```

Embrulhe em `.track-wrap{overflow-x:auto}` com `.track{min-width:900px}` — a
linha é larga por natureza e o body nunca deve rolar de lado.

### 11.6 O fechamento — a pergunta

```css
.ask{ border:1.5px solid var(--ink); padding:18px 20px }
.ask h3{ font-family:var(--mono); font-size:11px; letter-spacing:.16em;
         text-transform:uppercase; margin:0 0 12px; color:var(--mark) }
.ask ol{ margin:0; padding-left:20px; font-size:14.5px }
```

Conteúdo: um item por decisão pendente, com a recomendação dita na cara — e um
item final para **o que você não sabe desenhar**, com o motivo. Prancha honesta
declara o próprio limite.
