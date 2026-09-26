# Exemplo visual, não runtime do plugin

Abra `mapa-sprint.html` num navegador. É autocontido, sem servidor, rede ou persistência. O cenário é fictício e não contém handbooks ou links de repositório privado.

- Mapa inicia sem seleção, com todas as linhas; clique novamente no mesmo nó, Mostrar tudo, Escape ou área vazia retorna ao conjunto.
- Sequência usa apenas after. Frentes na mesma etapa não têm precedência declarada entre si; recursos/autorização não foram avaliados.
- Troque o cenário para ver cadastro ausente ou ciclo after. Isolado válido, fora do recorte e fonte ausente têm tratamentos distintos.
- De onde vem cada coisa mostra a composição separada do estado. `example.json` é o fixture; seu conteúdo está incorporado no HTML sem depender de fetch local.

O asset preserva a linguagem visual do painel de acompanhamento aprovado pelo operador. A integração futura usa o renderer/drawer oficiais; não deve simplesmente copiar este protótipo para criar um segundo QG. O JavaScript aqui cobre a demonstração; não implementa o CLI, parser de fontes, refresh ou consumo HTTP definidos na SPEC.

Ao alterar o fixture, regenerar o bloco `mock-data` no HTML usando serialização segura de JSON e conferir equivalência. O plan.json da spec acompanha a implementação futura, não o estado fictício deste exemplo.

## Ajuste de foco — 26/09/2026

A visão geral continua abrindo sem seleção, com todas as conexões e setas de direção. Ao selecionar uma frente, ficam somente as relações incidentes em curvas contínuas por trás dos cartões. No foco, não há desvio pelas bordas nem pontas de seta disputando atenção; direção e motivo permanecem na lista textual, na visão geral e na sequência.

Os cartões conservam fundo opaco, inclusive os secundários: o destaque reduz o contraste de bordas e textos, nunca a opacidade da superfície inteira. Assim o traço pode desaparecer sob um cartão intermediário sem atravessar seu texto. O SVG permanece abaixo dos cartões e sem captura de ponteiro.

Segundo clique, Mostrar tudo, Escape e área vazia devolvem a visão geral. Nenhum dado, precedência, cálculo de etapas ou contrato do plugin mudou. Este comportamento visual deve ser preservado na futura integração P03; não acrescenta modo persistido ao schema de scope.
