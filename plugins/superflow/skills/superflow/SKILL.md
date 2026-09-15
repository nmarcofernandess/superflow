---
name: superflow
description: Roteia trabalho por uma spec mínima, escolhendo capacidades e playbooks conforme os contratos existentes.
---

# Superflow

Use para registrar, preparar, retomar, reconciliar ou fechar uma entrega.

## Leitura inicial

1. Localize a spec e leia `status.md` primeiro.
2. Escolha a intenção: capturar, preparar/executar, retomar, reconciliar ou fechar.
3. Abra somente a receita e os contratos necessários à intenção escolhida.

## Regras

- Ideia nova: `PRD.md` e `status.md`, com resumo humano do tema.
- SPEC e plano são independentes e condicionais: arquitetura material pede Build; sequência coordenada pede Plan.
- `superflow check spec <spec>` valida o pacote existente; autorização e próximo trabalho dependem do contexto.
- Estado global e de task usam `pending | done`. Analyst, Build, Plan, Execute, Review e QA são capacidades ou ações.
- Relações preservam memória; condições e direção ficam em `Próximo trabalho`. Plano com task pendente é o único cursor de tasks.
- Atualize PRD quando mudar produto; SPEC quando mudar arquitetura; plano quando mudar execução; status quando mudar direção, autorização, espera relevante, relação, divisão de escopo ou handoff.
- Ao criar, atualizar, retomar ou fechar, use a [fronteira do pacote](../../assets/references/state-contract.md#fronteira-do-pacote-da-spec): material da spec é autocontido; implementação permanente tem destino canônico no projeto.
- O projeto consumidor é dono de testes, provas, CI e ship.

## Playbooks

Leia somente a receita escolhida em `../../assets/playbooks/`: `capture`, `feature`, `retomar`, `fechar` ou `reconciliar`. Para retomar, carregue `retomar.md` e interprete a orientação junto do plano ativo, se houver.

Os comandos `new`, `feed`, `qg` e `check` são determinísticos e não autorizam ações externas.
