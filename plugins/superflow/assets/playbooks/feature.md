# Feature

1. Leia PRD/status e confirme recorte e autorização. Numa entrega nova ativa, comece pelo PRD inicial e pelo Analyst vivo, mesmo que a análise seja curta.
2. Integre research e respostas no mesmo Analyst; exponha perguntas materiais com recomendação, sem interrogatório artificial. Decisões de produto aceitas amadurecem o PRD.
3. Build passa as decisões a limpo numa SPEC arquitetural fechada. Não delegue componentes/interfaces a “usar patterns”. HTML normativo, quando necessário, é limpo e tem autoridade delimitada.
4. Use `superflow:plan` para chamar writing-plans e gravar PLAN.md nativo no pacote. Registre método de execução. Não criar plan.json espelho nem repetir design aprovado.
5. Confira os artefatos por `check spec`; os diagnósticos não são autorização. Execute até o limite concedido, seguindo ordem textual e ledger. Sem subagents disponíveis, não alegar SDD.
6. Use a revisão do método escolhido e as provas/ship do projeto. Corrija causa focal antes de repetição ampla; não rodar toda suíte duas vezes apenas para rebatizar uma de preflight.
7. Siga fechar.md. Uma correção avulsa delimitada fora de nova spec pode continuar pelo aceite autorizado sem criar este pacote inteiro.
