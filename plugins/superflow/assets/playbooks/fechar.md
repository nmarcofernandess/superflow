# Receita: fechar

Use quando uma entrega parece pronta e precisa de aceite honesto.

1. Faça review do desenho ou diff se ele ainda for aplicável; resolva achados
   bloqueantes e maiores e revalide as correções.
2. Compare cada aceite do PRD com a prova correspondente. Consulte as regras
   do projeto e proof_cmd/ship_cmd na configuração quando existirem. Execute
   proof_cmd se ele for aplicável ao aceite; sua ausência não dispensa prova.
   Rode checks e proofs proporcionais ao risco. Registre qa quando o plano
   estiver encerrado e a verificação final começar; tasks ainda abertas
   continuam em execute. Um aceite que falha reabre a execução.
3. Faça ship, deploy, migration ou comunicação externa somente se o pedido e as
   regras do repositório autorizarem. Use ship_cmd quando definido e aplicável;
   a configuração não concede autorização adicional.
4. Atualize status para done apenas quando aceite próprio, dependências, plano,
   espera e evidências atendem ao contrato.
5. Rode check e, quando útil, feed para conferir a projeção da fonte atual.

Se o aceite falhar, reabra o trabalho que falhou e volte à execução. Não feche
por mensagem de sucesso, passagem de tempo ou arquivo arquivado.
