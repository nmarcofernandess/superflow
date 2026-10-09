---
name: build
description: Use para consolidar uma exploração aceita em arquitetura integrada, ou reconciliar uma decisão técnica material antes de planejar sua implementação.
---

# Build — arquitetura consolidada

Build escreve `SPEC.md`, não BUILD.md. A entrada é o PRD amadurecido, o Analyst ativo e pesquisas/decisões pertinentes. Não repete pesquisa resolvida: integra e passa a limpo a solução escolhida.

## Completude

Use o [template SPEC](../../assets/templates/SPEC.md) para fechar o recorte autorizado. Para cada caminho material, defina entrada, identidade/owner, validação, transformação, escrita, efeitos, leitura, UI, falhas e recuperação. Feche invariantes, interfaces e consumidores. Em UI, escolha componentes e composição, props/eventos relevantes, estado canônico/draft/derivado, confirmações/cancelamento, readonly/loading/erro e copy que expressa política.

“Seguir os patterns” é orientação de leitura, não uma escolha arquitetural. Se a investigação de componentes encontrou uma necessidade, incorpore-a explicitamente; não a apague para encurtar o texto. Decisões materiais abertas impedem chamar a SPEC de fechada. Detalhes triviais de corpo de função podem ficar ao implementador.

## Referências e tamanho

Não há teto artificial de linhas. Organize índice, seções e exemplos. Referências a código, API, research ou Analyst sustentam decisões; não obrigam o planejador a reconstruí-las. Anexos normativos fazem parte do mesmo pacote e têm autoridade delimitada. Não crie dois contratos concorrentes.

HTML de debate contém alternativas e não serve como implementação final. Quando a geometria visual exigir HTML normativo, produza uma versão limpa da solução aceita e declare o que ela governa. Markdown continua dono do comportamento e das invariantes. Copy literal tem uma casa explícita. Contradição entre formatos precisa ser resolvida, não herdada pelo Plan.

## Integração e saída

Código, testes e configuração permanentes ficam no owner do projeto, fora de `specs/**`; scripts temporários têm uso e remoção/promoção definidos pela [fronteira do pacote](../../assets/references/state-contract.md#fronteira-do-pacote-da-spec).

Confira PRD versus SPEC: se a arquitetura muda a promessa, comunique a escolha e reconcilie produto conforme autorização. Faça uma passada de interfaces e lifecycle, riscos, negativos e verificação proporcional. Um planejador com SPEC/anexos e código citado deve conseguir planejar sem reviver Analyst/chat para descobrir uma decisão.

Persista antes de apresentar. Havendo autorização para planejar, entregue a SPEC a `superflow:plan`; caso contrário aguarde apenas a decisão de etapa realmente necessária. O aceite de arquitetura não autoriza silenciosamente código, merge ou publicação.
