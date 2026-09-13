# Contrato de estado

Cada pacote vive em specs/<id-ou-slug>/. status.md é seu cadastro e pode ter
corpo Markdown curto para contexto; o dado de estado fica no front matter.
PRD.md é a promessa. SPEC.md, analysis.md, plan.json e progress.md são
condicionais, conforme a necessidade do trabalho.

## Cadastro mínimo

    ---
    id: "014-importacao"
    title: "Importar despesas"
    phase: inbox
    state: pending
    prd: gathering
    updated_at: "2026-09-13T12:00:00Z"
    ---

Id é uma string única e estável no repositório; o path pode mudar. O leitor
descobre recursivamente os pacotes abaixo da raiz de specs, inclusive backlog,
archived e minispecs, sem seguir symlinks para fora dela.

Campos opcionais:

    depends_on: ["013-fundacao"]
    absorbed_by: "015-consolidacao"
    waiting_for: "Responsável validar o proof de importação"
    archived: false
    evidence:
      - "artifacts/proofs/importacao.json"

Use YAML simples e seguro: mapas, listas, strings, booleanos e datas no
subconjunto documentado. Não use tags, aliases, merge keys ou chaves
duplicadas.

## Fase, andamento e PRD

Phase é inbox, analyst, build, plan, execute, qa, done ou cancelled. Em fase
aberta, state é pending, in_progress ou paused. Fases done e cancelled não
carregam state.

Prd é gathering ou ready. Build, plan, execute, QA e done exigem ready; ready
exige PRD não vazio com problema, promessa, escopo e aceite verificável. Um
ticket legado em gathering pode ainda não ter PRD; não fabrique prosa para fazê-lo
parecer pronto.

Waiting_for descreve uma espera concreta e veda state in_progress e fases
terminais. Archived e absorbed_by também vedam in_progress. Arquivo muda
visibilidade, não prova entrega. Cancelamento registra a decisão de retirada de
escopo e não satisfaz uma dependência.

## Relações

A.depends_on contendo B significa que a entrega de B é necessária para A
concluir sua obrigação. B satisfaz somente em done, arquivada ou não. QA, pausa
e cancelamento não satisfazem.

A.absorbed_by igual a B significa que B assumiu todo o escopo restante de A. A
fica consultável, sem execução independente. B done não fecha A por cascata: a
receita de fechamento confere o aceite de A e o encerra separadamente. Para
transferência parcial, descreva o recorte, divida a unidade quando necessário e
use dependência apenas se o restante realmente espera o destino.

Mãe, filhos e complementos organizam navegação; não criam bloqueio. Uma mãe
done pode ter complementos abertos. Rejeite ID duplicado, auto-referência,
destino ausente e ciclo que misture depends_on e absorbed_by.

## Plano e evidência

Quando uma sequência precisa ser mantida, plan.json contém:

    {
      "tasks": [
        {
          "id": "T01",
          "behavior": "resultado observável",
          "files": ["caminho/alvo"],
          "depends_on": [],
          "acceptance": ["AC-01"],
          "status": "pending",
          "evidence": []
        }
      ]
    }

Tasks usam pending, in_progress, done ou skipped. Skipped requer skip_reason.
Dependências de task são locais, únicas e acíclicas. Uma task done precisa de
prova da unidade e das predecessoras; skipped não simula entrega. Task
in_progress só é válida quando a spec está em phase execute e state
in_progress.

Ao cancelar ou absorver todo o restante, converta tasks abertas em skipped com
motivo que aponta decisão, destino ou escopo. Em transferência parcial, divida
antes a task mista. Ao invalidar uma evidência, reabra a task done e as
dependentes afetadas, remova a referência inválida do estado atual e preserve a
história em progress.md ou no registro já adotado pelo projeto.

Uma spec chega a done somente com aceite próprio, dependências satisfeitas,
plano sem tasks abertas quando existente, nenhuma espera e evidência pertinente.

## Diagnósticos

Um status.md inválido é erro. PRD.md, SPEC.md ou HANDBOOK.md encontrados sem
status.md são candidatos não registrados: o leitor os lista como aviso
UNREGISTERED_DOCUMENTS, sem convertê-los automaticamente em tickets. O censo de
migração decide o destino de cada candidato.

Evidência local precisa existir; referência HTTPS é preservada, mas não é
consultada pelo check estrutural.
