# Reuse Guard Protocol

Anti-fork check for **one** intent: “o que estou prestes a criar ou corrigir
já tem forma canônica no repo?”

Portado do **crystallize-guard** (plugin Crystallize): só a parte de
**consulta read-only**. Não roda map/mine/diff, não unifica módulos, não
escreve `.context/`. Campanhas de consolidação continuam no `/crystallize`.

## Quando rodar (ponto ideal)

**Obrigatório** em Analyst (e revalidar em Build se a análise for fraca) **antes** de:

- decidir `new` em shell, primitivo, modal, card, filtro, helper, action,
  service ou pattern de composição;
- fechar a **Faceta — Frontend** ou **Backend** com “criar do zero”.

Roda **depois** da promessa de Produto estar clara o suficiente para nomear o
*need* (“modal de pick de categoria”, “filtro de paciente no drawer”), e
**antes** da Síntese final — para a decisão de reuso alimentar o class number.

Não roda em docs-only sem UI/código.

## Passo 1 — staleness (se houver grafo)

Se o repo tem `.context/` (Tier-2 curado):

1. Leia `.context/status.json` se existir.
2. Se existir `.context/_crystallize/tools/validate-context.py`, rode (read-only):

```bash
python3 .context/_crystallize/tools/validate-context.py --context .context --repo .
```

3. Se o grafo estiver **stale**, o validator faltar, ou PyYAML faltar:

```text
⚠ .context stale ou incompleto — treat guard as HINT only; fall back to grep;
  re-run /crystallize <scope> when trust is needed.
```

Nunca fale com confiança de canônico apodrecido.

Se **não** houver `.context/`, pule para o Passo 3 (grep).

## Passo 2 — consulte só Tier-2 (curado)

Leia, nesta ordem, o que existir:

1. `trees/need-*.yaml` — árvore “preciso de X → use Y” mais próxima do need.
2. `patterns/<name>.yaml` — `extends`, consumers, rules, `anti_patterns` /
   `forbidden`.
3. `index/components.yaml` (curado, **não** só `components.generated.yaml`).

Nós `status: draft` / `proposed` = sugestão, não canônico fechado.

## Passo 3 — fallback grep (sempre se não há grafo ou está stale)

`rg` por famílias do *need* no repo (ex.: `FilterPopover|BaseSearchModal`,
`BaseModal`, `MainGenericEditor`, actions do domínio). Cite paths.

O plugin **não** prescreve “use CRUDForDashboard em todo mundo” — manda
**procurar** o equivalente **neste** repo.

## Passo 4 — resposta canônica (cole na Faceta Frontend/Backend)

**Se existe forma canônica:**

```text
✋ Reuse, don't fork.
- Canonical: <name> (`path`) — ~N consumers se souber.
- Extend / mode: <como cobrir o caso sem fork>.
- Forbidden: <paralelo banido pelo pattern, se houver>.
Para fork: justificar qual branch do canônico NÃO serve e por que não estende.
```

**Se nada casa (conceito genuinamente novo):**

```text
✅ No canonical form found for "<need>".
- Nearest: <path ou none>.
- Se criar: depois rodar /crystallize <scope> no repo (fora do Superflow)
  para o próximo guard achar.
```

**Decisão Superflow (obrigatória na analysis):**

| Need | Guard source (graph\|grep\|both) | Decision `reuse` \| `mode` \| `new` | Evidence path |
|---|---|---|---|
| … | … | … | … |

`new` **sem** linha de guard (graph ou grep) = Analyst/Build **não ready**.

## O que isto NÃO é

- Não é `/crystallize` (map/mine/diff/referee/brief/apply).
- Não reescreve código nem `.context/`.
- Não substitui path:line de Backend nem strings-safadas.
- Não isenta TDD no Plan/Execute.

## Relação com feature-mindset

| Id | Como o guard cobre |
|---|---|
| T4 | Scan antes de `new` |
| T5 | reuse\|mode\|new + evidence path |
| T6 | Procura; não dogma de shell |
| T7 | Graph se `.context/`; senão recon genérico |
