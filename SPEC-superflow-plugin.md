# SPEC: plugin Superflow enxuto

## Status desta especificação

Este é o contrato técnico atual do plugin. Materiais que descrevem o Superflow
0.8 ou anteriores, seus campos de fase, status.json, HANDBOOK, board, campanha, WARLOG
ou skills removidas são históricos e não instruções de operação.

## Intenção

Superflow mantém um fluxo proporcional e uma fonte factual de trabalho. PRD
descreve a promessa; status.md descreve o estado; plan.json existe somente
quando a ordem das unidades precisa persistir. Feed e QG projetam essas fontes
sem se tornar outra fonte de verdade.

## Superfícies públicas

O pacote exporta exatamente sete skills:

    superflow, prd, analyst, build, plan, review, status

Ele oferece cinco receitas:

    capture, feature, retomar, fechar, reconciliar

E três contratos:

    state-contract, commands-contract, quality-contract

Execute e QA são passos operacionais nas receitas. Rota é um plugin separado.
Graph, campanhas e WARLOG não pertencem ao escopo deste plugin.

## Estado e relações

Status.md usa front matter com `id`, `title`, `status`, `depends_on` opcional e
`waiting_for` opcional. O corpo Markdown é o retrato completo e pode ser vazio.
`status` aceita somente `pending` ou `done`; `depends_on` exige `id` e `reason`.
A hierarquia de mãe e minispecs deriva do path e não bloqueia nem reabre a mãe.

Plan.json contém tasks com exatamente `id`, `task`, `status`, `depends_on` e
`acceptance`. O status local também aceita somente `pending` ou `done`. Não é
board, scheduler, log de agentes nem artefato de campanha.

## Runtime

O runtime Python 3.9 ou superior expõe `new`, `check status`, `check ready`,
`feed` e `qg` com raiz explícita e modo isolado. New cria somente status.md e
PRD.md; os checks são somente leitura. Feed e QG abrem exclusivamente arquivos
exatamente chamados status.md e não executam comandos do consumidor.

O parser usa YAML seguro. `check ready` abre somente PRD.md, status.md, SPEC.md
e plan.json da spec indicada. A migração incorpora o conteúdo útil e completo
do handbook no corpo do status, valida a projeção e então apaga a fonte antiga;
não há fallback.

## Qualidade

Analyst e build preservam recon, facetas relevantes e reuso antes de criação,
sem seis relatórios compulsórios. Alteração de comportamento pede falha
observada e prova verde útil; documentos e mudanças sem teste útil usam
verificação alternativa concreta. Review resolve achados com evidência e QA
confronta os aceites com provas do projeto.

## Distribuição

Os manifests Codex e Claude descobrem o diretório de skills do pacote. O gate
de distribuição deve conferir o conjunto nominal das sete pastas, links
internos, assets necessários e instalação limpa. O canal Node opcional
distribui somente runtime, assets, vendor e licenças; a CLI continua Python.
