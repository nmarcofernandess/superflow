# Exemplo visual, não runtime do plugin

Abra `mapa-sprint.html` num navegador. É autocontido, sem servidor, rede ou persistência. O cenário é fictício e não contém handbooks ou links de repositório privado.

- Mapa inicia sem seleção, com todas as linhas; clique novamente no mesmo nó, Mostrar tudo, Escape ou área vazia retorna ao conjunto.
- Sequência usa apenas after. Frentes na mesma etapa não têm precedência declarada entre si; recursos/autorização não foram avaliados.
- Troque o cenário para ver cadastro ausente ou ciclo after. Isolado válido, fora do recorte e fonte ausente têm tratamentos distintos.
- De onde vem cada coisa mostra a composição separada do estado. `example.json` é o fixture; seu conteúdo está incorporado no HTML sem depender de fetch local.

O asset preserva a linguagem visual do painel de acompanhamento aprovado pelo operador. A integração futura usa o renderer/drawer oficiais; não deve simplesmente copiar este protótipo para criar um segundo QG. O JavaScript aqui cobre a demonstração; não implementa o CLI, parser de fontes, refresh ou consumo HTTP definidos na SPEC.

Ao alterar o fixture, regenerar o bloco `mock-data` no HTML usando serialização segura de JSON e conferir equivalência. O plan.json da spec acompanha a implementação futura, não o estado fictício deste exemplo.
