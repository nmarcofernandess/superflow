---
name: build
description: "Feche uma arquitetura verificável em SPEC a partir de um PRD pronto e do terreno real. Use para mudanças com fronteiras, contratos, migração, integração, segurança, estado compartilhado ou risco que a execução não deve decidir no caminho."
---

# Build

Build decide arquitetura; não decompõe tarefas nem cria uma lista de progresso.
Use-o quando a implementação precisa de uma escolha técnica explícita antes de
começar.

## Procedimento

1. Leia o PRD.md pronto e qualquer analysis.md que sustente a decisão. Volte a
   analyst se a promessa, os fatos ou a decisão humana ainda não estiverem
   maduros.
2. Reconheça o sistema real antes de desenhar: interfaces, dados, fluxos,
   limites de autorização, superfícies, dependências e testes existentes.
   Afirmações materiais recebem path:line; hipótese continua hipótese.
3. Considere somente as facetas relevantes: produto, dados e Backend,
   interface, cópia, risco e operação; registre como elas se afetam.
4. Procure reuso antes de criar. Mostre a implementação ou padrão considerado e
   justifique reusar, adaptar ou introduzir algo novo.
5. Escreva SPEC.md com o [template](../../assets/templates/SPEC.md): decisão,
   fronteiras, fluxo, comportamentos observáveis, sequência de alto nível,
   verificação, riscos e rollback quando aplicável.
6. Atualize o PRD se a arquitetura revelou que a promessa ou o escopo precisava
   mudar. Atualize status.md apenas quando a fase de fato avançar, seguindo o
   [contrato de estado](../../assets/references/state-contract.md).

## Saída

Uma SPEC permite que a próxima pessoa implemente sem redescobrir as fronteiras
ou inventar contratos. Ela não precisa de diagrama, tabela de facetas ou plano
de tarefas quando isso não esclarece a mudança.
