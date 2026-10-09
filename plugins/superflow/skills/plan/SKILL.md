---
name: plan
description: Use quando a arquitetura aceita precisa virar uma sequência verificável de implementação, ou quando um retrofit exige reconciliar o futuro de um plano ativo.
---

# Plan — entrada para planejamento nativo

Para uma nova entrega ativa, use **superpowers:writing-plans**, com a SPEC aceita, e salve o plano nativo em `<spec>/PLAN.md`. Preserve o pacote Superflow. Não invoque novamente brainstorming para decisões já aprovadas, não mova a SPEC e não gere plan.json espelho.

Carregue a skill real disponível e confira seu formato. Se o método solicitado não estiver disponível, informe a limitação e preserve o material; não finja uso do plugin ou troque executor silenciosamente. Superpowers não é dependência do reader/QG.

## Contrato do plano

Cada `### Task N: título` é uma unidade verificável com arquivos, interfaces consome/produz, requisitos locais, passos, comandos/Expected e critério de conclusão. Use números positivos únicos. A ordem textual é a sequência; não escolher livremente qualquer pendência. O quadro de baldes explica dependências, não autoriza implementadores concorrentes.

Metadados opcionais na própria task: `**Balde:**`, `**Por que agora:**` e `**Depends on:** 1, 9`. Dependências numéricas devem apontar para tasks anteriores na ordem textual. Não crie outro arquivo resumindo as mesmas tasks para o painel.

Se o Plan precisa decidir política, entidade, composição ou protocolo material ainda abertos, reconcilie SPEC/Analyst em vez de inventar arquitetura escondida. Profundidade adequada não é transcrever todo o código nem omitir valores/interfaces necessários.

## Handoff, legado e retrofit

Registre método escolhido e plano/ledger na continuidade conforme [execution-contract](../../assets/references/execution-contract.md). SDD e inline têm custos e revisões diferentes. Apresente o plano e execute somente com a autorização aplicável; não repita um GO já concedido para esse recorte.

`plan.json` existente continua válido no contrato legado de cinco campos. Se os dois formatos coexistirem, selecione um explicitamente no status. Nenhuma migração em massa ou conversão bidirecional. Pacotes encerrados permanecem encerrados.

Retrofit recebe Task N nova e mapeamento para o requisito anterior, colocada antes dos consumidores futuros. Não renumere nem amplie silenciosamente o aceite de uma task com conclusão no ledger. Registre ruling, ajuste a região da SPEC quando material e preserve evidência anterior com seu alcance real.
