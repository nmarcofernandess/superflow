# Contrato de qualidade

Qualidade prova o aceite prometido no contexto do projeto. Um comando verde sem
relação com o comportamento não é evidência suficiente.

## Mudança de comportamento

Quando código novo ou corrigido altera comportamento observável, primeiro
observe uma falha relevante, implemente a menor correção e então observe a
verificação verde. Use a suíte, harness ou cenário real do projeto. Não invente
um comando RED ou GREEN apenas para preencher uma tabela.

Mudança documental, ajuste de configuração sem comportamento novo ou trabalho
que não admite teste útil registra a razão e uma verificação alternativa
concreta: links, parse, renderização, inspeção ou check nativo.

## Review e QA

Review examina desenho ou diff com evidência e resolve achados antes do avanço.
QA compara cada aceite do PRD com sua prova e inclui testes, check estático,
prova visual, dado ou segurança quando o risco pede. Achado bloqueante ou maior
aceito volta à correção e é reconferido.

A evidência pode viver no harness, em outro diretório ou em CI ou PR. Registre a
referência e o resultado atual; uma URL sozinha não prova frescor. Publicação,
ship, deploy, migration destrutiva e mensagens externas continuam exigindo a
autorização e os gates do repositório.
