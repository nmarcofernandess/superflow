# SPEC: plugin Superflow enxuto

## Status desta especificação

Este é o contrato técnico atual do plugin. Materiais que descrevem o Superflow
0.7, seu roteador por budgets, status.json, HANDBOOK, board, campanha, WARLOG
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

Status.md usa front matter com id, title, phase, state, prd e updated_at.
Depends_on e absorbed_by são relações explícitas; containment de mãe e
complementos não bloqueia a conclusão. Arquivo não prova done. Cancelamento não
satisfaz dependência. A absorção total exige fechamento conferido, não cascata
automática.

Plan.json contém tasks com comportamento, arquivos, dependências, aceite,
status e evidência. Não é board, scheduler, log de agentes nem artefato de
campanha.

## Runtime

O runtime Python 3.9 ou superior expõe new, check, feed e qg com raiz explícita
e modo isolado. New cria somente status.md e PRD.md; check é somente leitura.
Feed e QG derivam uma fotografia única e não executam proof_cmd ou ship_cmd da
configuração do consumidor.

O parser usa YAML seguro e a validação diferencia erro de status.md de
documentos candidatos sem cadastro. Migração de corpus é censo explícito; não
há fallback que converta história em ticket sem decisão.

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
