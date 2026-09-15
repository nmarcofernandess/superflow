# Retomar

1. Leia `status.md`: resumo, retrato e `## Próximo trabalho` orientam a continuação.
2. Confira condições vigentes e autorização nas fontes relevantes. Uma espera parcial pode permitir outro trabalho; uma relação registra contexto e não bloqueia automaticamente.
3. Leia PRD e, conforme a ação, SPEC ou outras fontes necessárias. Ao lidar com artefatos da spec, aplique a fronteira do pacote do contrato de estado.
4. Se `plan.json` existir e contiver task `pending`, ele é o plano ativo e o único cursor. Escolha uma task pendente cujas predecessoras estejam concluídas e compatível com a orientação e autorização atuais.
5. Sem plano ativo, interprete o próximo trabalho: esclarecer uma dúvida, preparar arquitetura, criar uma sequência ou executar uma mudança simples. Acione Analyst, Build ou Plan somente quando necessário.
6. Se o plano existente estiver todo concluído, preserve o registro encerrado. Explicite o novo recorte e sua forma de registro antes de começar nova execução; não reabra tasks silenciosamente.
7. Conclua tasks no plano aplicável após conferir aceite. Atualize status somente se mudar direção, autorização, espera relevante, relação, divisão de escopo ou handoff.

Se fontes divergirem, use Reconciliar. Uma condição sem resposta suficiente fica explícita para a decisão necessária, junto do trabalho que ainda pode avançar.
