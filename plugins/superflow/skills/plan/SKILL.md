---
name: plan
description: "Crie um plan.json com unidades ordenadas e verificáveis quando a sequência, as dependências ou a retomada justificarem esse controle. Use a partir de PRD pronto e SPEC quando houver arquitetura."
---

# Plan

Plan existe para tornar a sequência explícita. Não o crie para uma mudança
direta de uma unidade, e não o use como diário, kanban ou contrato de
orquestração.

## Procedimento

1. Leia PRD.md e SPEC.md quando houver. Confirme que a decisão de arquitetura
   já está tomada; se não estiver, volte a build.
2. Liste apenas unidades que alguém pode concluir e verificar. Para cada uma,
   registre comportamento, arquivos ou área, predecessoras, critérios de
   aceite, status e evidência usando o
   [template](../../assets/templates/plan.json).
3. Mapeie cada unidade a um aceite do PRD. Dependências são locais ao plano e
   não formam um scheduler, board ou campanha.
4. Defina verificações reais e proporcionais ao comportamento. Para mudança de
   comportamento, a execução deve observar a falha relevante antes da correção
   e depois a prova verde; não invente comandos RED ou GREEN que o projeto não
   possui.
5. Se criar ou atualizar o plano, siga o
   [contrato de estado](../../assets/references/state-contract.md) para
   plan.json e o cadastro da spec.

## Limites

- Uma task done tem evidência atual; skipped exige motivo.
- Ao invalidar uma prova, reabra a task e as dependentes afetadas. Conserve a
  história no diário já adotado pelo projeto, sem criar um segundo registro.
- Não crie board, logs obrigatórios ou divisão por agente. Ownership e
  ferramentas pertencem ao projeto e ao pedido em curso.
