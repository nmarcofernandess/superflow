---
name: review
description: "Revise um desenho ou diff com evidência, priorize achados reais e conduza a correção até a rechecagem. Use antes de avançar uma SPEC, antes de fechar uma entrega, ou quando o usuário pede crítica técnica."
---

# Review

Review compara o alvo com suas fontes e efeitos reais. Pode revisar uma SPEC
antes do plano ou um diff antes do QA. Não exige arquivo paralelo de revisão: o
registro fica onde o projeto já acompanha o trabalho.

## Procedimento

1. Declare o alvo: desenho, diff, comportamento ou prova. Leia as fontes que
   definem o contrato e, para código, o diff e a verificação relacionada.
2. Registre cada achado com gravidade proporcional, evidência reproduzível
   (path:line, cenário ou comando) e impacto concreto.
3. Separe defeito que bloqueia aceite, comportamento errado, manutenção útil e
   preferência. Não infle nits para simular revisão.
4. Resolva ou encaminhe cada achado com motivo e destino. Uma correção de
   comportamento recebe a prova útil prevista no
   [contrato de qualidade](../../assets/references/quality-contract.md).
5. Se uma prova concluída foi invalidada, leia o
   [contrato de estado](../../assets/references/state-contract.md), reabra a
   task e as dependentes afetadas e retire a evidência inválida do estado atual.
6. Reconfira os achados bloqueantes e maiores antes de permitir avanço.

## Saída

Entregue veredito, achados, evidência, correções verificadas e riscos
restantes. Uma revisão sem achados nomeia o alvo e a cobertura examinada.
