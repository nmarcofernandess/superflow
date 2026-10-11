# Fechar

1. Confira aceite do PRD, arquitetura da SPEC e unidades do plano selecionado. Ledger terminal com ressalvas não equivale a aceite global.
2. Encerre a autoria quando terminarem as tasks e reviews previstos. Registre a passagem e o responsável pelo fechamento conforme [execution-contract](../references/execution-contract.md#registro-do-fechamento-de-ci-e-integração); falhas desta fase seguem o owner de CI do projeto, sem reiniciar automaticamente o método. Produto, proof, PR, merge e release são fatos distintos.
3. Antes do cleanup do Superpowers, preserve o mesmo ledger e reports/reviews indispensáveis em `execution/<run>/progress.md` e arquivos associados. Atualize Registro no status. Não mantenha dois registros ativos nem apague história útil.
4. Promova rulings arquiteturais à SPEC e decisões de produto aceitas ao PRD. Remova scripts descartáveis ou promova o que continuará operando a seu owner fora da spec.
5. Integre/publice somente com autorização e fluxo do consumidor. Registre comandos, revisão, evidências e limites reais. Sem ferramenta/revisor disponível, diga isso, não fabrique validação.
6. Marque status global done somente após o aceite próprio. Confira check spec e regenere feed/QG quando a projeção fizer parte da entrega. Ausência de detalhe ou erro editorial não controla o CI do produto.
