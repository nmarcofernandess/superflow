---
name: status
description: "Mantenha o cadastro factual de uma spec, suas evidências, espera e próxima ação. Use para iniciar, pausar, retomar, arquivar, concluir, cancelar, reconciliar ou gerar projeções sem inferir sucesso."
---

# Status

status.md diz o que está factual e verificavelmente em curso. Ele não é PRD,
diário, board nem sinal de que um agente continua online.

## Procedimento

1. Leia o [contrato de estado](../../assets/references/state-contract.md) e a
   fonte que comprova a mudança antes de editar o cadastro.
2. Atualize fase, estado aberto, updated_at, espera, relações e evidências
   somente para refletir o fato observado. In_progress declara trabalho em
   execução, não presença contínua.
3. Para gerar ou verificar uma projeção, leia também o
   [contrato de comandos](../../assets/references/commands-contract.md). Os
   comandos nunca executam proof, ship ou outro comando configurado pelo repo.
4. Quando a promessa mudou, encaminhe a prd; quando a evidência contradiz a
   conclusão, reabra as tasks e retorne à execução ou review conforme
   necessário.

## Fechamento honesto

Done exige aceite próprio, dependências satisfeitas, plano sem tarefas abertas
quando existe, ausência de espera e evidência pertinente. Arquivar só muda
visibilidade. Cancelar registra a decisão e não satisfaz dependências.
