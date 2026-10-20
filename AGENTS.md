# Superflow · instruções de manutenção

## Fechamento de atualizações com release

Por orientação de Marco em 20/10/2026, toda atualização autorizada de uma
entrega distribuída por release deve terminar com seus artefatos regenerados
e publicados pelo fluxo canônico. A regra vale para o Superflow, outros plugins,
CI Queue e demais ferramentas com distribuição própria.

Commit, push ou merge do código-fonte não encerram a atualização do produto
distribuído. Confira quais fontes entram na distribuição, regenere ou compile
os artefatos pertinentes, mantenha versões e manifestos coerentes e publique
a release correspondente. Reutilize artefatos apenas quando sua compatibilidade
com a atualização estiver demonstrada.

Quando a atualização inclui instalação ou adoção local, atualize a instalação
consumida e confira a versão e a origem efetivas. Uma release publicada não
comprova que CLI, worker, API, aplicativo ou plugin instalado já a estejam usando.
Respeite os contratos de identidade e compatibilidade do produto. Não reinicie
processos alheios nem altere permissões ou segurança por consequência.

Valide proporcionalmente o que mudou e confira a publicação remota. Relate
separadamente fonte integrada, artefato gerado, release publicada, instalação
atualizada e comportamento observado. Se faltar uma etapa indispensável,
registre o impedimento e o próximo passo; não declare a atualização concluída.
A regra não concede autorização para novos ambientes ou operações fora do pedido.

Para feed e QG, siga o
[contrato de geração local e publicação](plugins/superflow/assets/references/commands-contract.md#geração-local-e-publicação).
Uma alteração apenas neste guia não modifica o pacote distribuído do plugin;
se a atualização atingir o pacote, a release integra o fechamento acima.
