# Compor um encaminhamento completo

Preencher esta estrutura com conteúdo real antes de mostrá-la como pronta. O modelo abaixo não é um prompt pronto. Remover os títulos que não se aplicam, sem omitir contexto necessário.

1. **Papel e capacidade do destinatário:** planejador documental, revisor ou executor; ambiente/ferramentas realmente disponíveis. GPT online não executa validações locais.
2. **Objetivo desta unidade:** resultado concreto, sem anexar toda a história.
3. **Estado conferido:** o que existe, o que falta, fonte/revisão/data; distinguir relato não conferido.
4. **Leituras necessárias:** instruções vigentes, contrato dono, decisões, código pertinente. Usar URLs versionadas quando o destinatário não acessa o disco local. Se não houver acesso, preparar material sanitizado antes de chamar pronto.
5. **Escopo e ownership:** arquivos/pacotes permitidos, consumidores envolvidos, trabalho alheio ativo, limites e interfaces de entrada/saída.
6. **Dependências:** entradas disponíveis, esperadas e trabalho que pode avançar sem elas.
7. **Trabalho esperado:** revisão, descoberta, SPEC/plano ou implementação. Para plano mecânico quando pedido: arquivos/símbolos, comportamento, teste discriminante e dados/oráculo, alteração proposta, comando focal real, resultado esperado e término. Não fabricar APIs nem prova executada.
8. **Decisões:** preservar as ratificadas; para as realmente abertas, apresentar cenário, recomendação fundamentada, consequências e receptor da resposta. Oferecer HTML didático se facilitar a decisão. Não votar pelo operador.
9. **Entrega:** caminhos canônicos, completude esperada, como relatar achados/residuais e próxima ação. Se houver lacuna inseparável, entregar o prompt específico que a resolve.
10. **Parada:** condição objetiva. Não mudar de planejamento para execução, publicação ou merge por inferência.

## Exemplo de próximo passo quando falta arquitetura

“Revise o contrato atual de persistência e as decisões citadas. Identifique qual interface o módulo consumidor precisa e quais comportamentos já existem. Entregue recomendação com fontes, as decisões que ainda faltam e um prompt para a próxima unidade. Escreva o plano mecânico somente para a parte cuja semântica estiver fechada. Não implemente nem declare testes executados.”

## Exemplo de confirmação de envio

“Recebido: o prompt P-03 foi enviado ao chat indicado. Atualizar a unidade para enviado/aguardando, registrar o link e manter os sucessores dependentes aguardando sua saída.”

Um prompt pode pedir a correção de um status desatualizado. Isso não autoriza recalcular todo o projeto, abrir uma campanha ou reescrever onze pacotes sem relação com a unidade.
