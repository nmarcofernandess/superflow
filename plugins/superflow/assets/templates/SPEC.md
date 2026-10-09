# SPEC — título da entrega

## Objetivo, escopo e autoridade

Declare a promessa aceita do PRD, limites e fontes. Separe decisões fechadas de limites externos. Não publique como pronta uma arquitetura que delega escolhas materiais ao futuro executor.

## Arquitetura e integração

Descreva a jornada inteira: entrada, identidade, validação, transformação, escrita, efeitos, leitura e encerramento. Nomeie owners e caminhos/símbolos reais. Integre as conclusões pertinentes de todos os assuntos do Analyst.

## Dados, estado e invariantes

Defina entidades, interfaces, fonte canônica, draft/derivado, persistência, concorrência, lifecycle e consumidores. Explicite respostas de sucesso, erro, cancelamento, retomada e compatibilidade pertinentes.

## Componentes e interação

Quando houver UI material, escolha composição, primitive/feature, props/eventos, estados, gestos, acessibilidade, responsividade e copy decidida. “Usar patterns” não substitui esse fechamento. Sem UI, declare a não aplicabilidade sem inventar componentes.

## Anexos normativos

Liste somente anexos necessários e qual aspecto cada um governa. HTML normativo mostra a solução escolhida, não a comparação A/B. Referências de pesquisa explicam origem; decisões operacionais precisam estar nesta SPEC ou em seus anexos declarados.

## Transição, riscos e verificação

Defina o que muda, o que permanece compatível, rollback/recuperação necessários e propriedades a verificar no menor nível adequado. Tese do proof, estado a capturar, limite da imagem e owner editorial ficam explícitos quando pertinentes.

## Destinos e encerramento

Componentes permanentes têm destino canônico no projeto. Artefatos temporários têm uso e condição de remoção/promoção. A SPEC cobre o recorte acordado, não todos os problemas futuros do sistema.
