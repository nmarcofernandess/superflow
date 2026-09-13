---
name: prd
description: "Crie ou amadureça um PRD local com problema, promessa, escopo e aceite verificável. Use para transformar um pedido em trabalho compreensível sem inventar arquitetura ou fases desnecessárias."
---

# PRD

PRD é a fonte da promessa. Ele vem antes de análise, arquitetura ou plano
quando o trabalho precisa permanecer no repositório.

## Procedimento

1. Se não houver pacote, use o comando new para criar o cadastro e o PRD
   inicial. Não crie um ticket quando o pedido pede somente uma resposta.
2. Escreva ou amadureça PRD.md pelo
   [template](../../assets/templates/PRD.md). Explique problema, consequência,
   resultado prometido, escopo, fora de escopo, aceite e perguntas abertas.
3. Escreva de modo que outra pessoa reconheça a situação sem a conversa:
   mecanismo concreto, consequência observável, objetivo e limite. Use exemplo
   somente quando ele reduz ambiguidade; não preencha seções com jargão.
4. Pergunte somente o que muda promessa, escopo, aceite, risco ou autorização.
   Uma decisão humana ausente permanece explícita.
5. Marque prd como ready somente quando problema, promessa, escopo e aceite são
   verificáveis. Caso contrário, mantenha gathering.
6. Ao escrever metadados, leia o
   [contrato de estado](../../assets/references/state-contract.md). Não use
   status.md para repetir todo o PRD.

## Próximo passo

Uma dúvida que muda a promessa chama analyst; fronteiras técnicas relevantes
chamam build; sequência complexa chama plan. Uma correção pequena e pronta pode
seguir direto para execução pelas ferramentas do projeto.
