# Plano nativo, execução e retenção

## Uma autoridade por pergunta

PRD define a promessa; ANALYST guarda exploração/decisões; SPEC consolida arquitetura; PLAN.md define sequência; ledger Superpowers registra o ocorrido; status orienta retomada/aceite global. Não há progress Superflow ou JSON espelho obrigatório.

Novas entregas ativas usam Analyst → Build → `superpowers:writing-plans`, com `PLAN.md` na própria spec. A etapa de design já aceita não é repetida em outra árvore. A skill Superpowers real deve ser carregada; indisponibilidade deve ser comunicada. O reader não depende da instalação do executor.

## Identidade e ordem

O plano usa headings `### Task N: título`, N inteiro positivo único, sem zero inicial. A ordem textual é a sequência escolhida, não N+1. Passos, Files, Interfaces, Run e Expected seguem writing-plans. `**Balde:**`, `**Por que agora:**` e `**Depends on:** 1, 9` são metadados opcionais da mesma task. Predecessoras declaradas existem antes do consumidor. Baldes não autorizam escrita paralela; SDD usa implementadores em série.

Retrofit: mantenha números concluídos, crie número novo antes dos consumidores futuros e registre sua origem. Exemplo: Task 1 concluída → Task 9 retrofit → Task 2. Não ampliar silenciosamente uma task já complete no ledger. Reconciliar SPEC quando muda arquitetura e PRD quando muda promessa aceita.

## Seleção e continuidade

No corpo de status.md:

```markdown
## Execução
- Plano: specs/minha-entrega/PLAN.md
- Método: sdd
- Registro: .superpowers/sdd/PLAN/progress.md
```

São exemplos de caminhos, não instrução para inventá-los. Use o resolvedor nativo sdd-workspace para obter a identidade real. Métodos aceitos: sdd/inline. Campos não preenchidos não devem virar placeholders publicados. O caminho Plano identifica PLAN.md ou plan.json dentro do pacote.

Com apenas um formato convencional, a seleção é inequívoca. Com ambos, Plano é obrigatório para distinguir ativo de histórico. Não há migração automática, conversão bidirecional ou escolha por mtime. JSON legado conserva cinco campos por task: id, task, status, depends_on, acceptance. Estado legado é autoral; não é evidência de revisão nativa.

## Ledger

A primeira linha nativa identifica o plano: `# SDD ledger — plan: specs/minha-entrega/PLAN.md`. O leitor admite identidade absoluta apenas quando ela corresponde à raiz em leitura; uma cópia de outra máquina precisa de reconciliação explícita, não correspondência por basename.

O leitor considera linhas `Task N:` fora de cercas Markdown. Conclusão exige a forma nativa com intervalo de commits e revisão/teste. Fix posterior retira a atribuição de conclusão anterior até novo encerramento. Ressalvas/parked permanecem visíveis. Task desconhecida ou predecessora sem conclusão torna a atribuição indisponível. Exemplos em cercas e checkboxes não são evidência.

O QG mostra último checkpoint, nunca “agente ativo” por inferência. O ledger é um registro do executor, não um veredito criptográfico nem substituto das evidências originais. Um registro completo não marca status global done.

## Autonomia e limites

Escolha o método no handoff. SDD faz implementação/revisão por unidade; inline não deve se anunciar como SDD. Não duplicar a revisão de implementação com outro ciclo Superflow. O controle de risco e a autorização do projeto prevalecem sobre rotinas genéricas.

Um bug local usa correção/verificação focal. Falha de integração pode revelar interação legítima; não concluir automaticamente que todo vermelho foi uso de CI como debugger. O erro é repetir campanha sem investigar/provar a correção proporcionalmente. Documentos não exigem testes de produto artificiais.

Execute checkpoints internos sem pedir novo GO a cada task. Pausa do usuário prevalece: preservar WIP e fontes, não esperar review/Smoke/merge para poder pausar. Não existe supervisor autônomo criado por esta documentação.

## Retenção e transferência

Antes de apagar scratch/worktree, preserve uma cópia final do mesmo ledger em `specs/minha-entrega/execution/<run>/progress.md`, sem sobrescrever outra execução. Retenha reports/reviews referenciados necessários e promova decisões arquiteturais à SPEC. Atualize Registro para o arquivo preservado. Somente depois remova o workspace próprio.

Isso é transferência terminal, não dois ledgers ativos. Uma execução nova recebe seu registro próprio e mapeia o trabalho já entregue. Compactação, perda do host e remoção de worktree são eventos diferentes. Handoff precisa transferir também quem pensa copy, mantém descriptor e revisa provas; remover uma worktree não faz isso automaticamente.

## Exposição no QG

A configuração `qg_details` habilita IDs específicos. Documentos convencionais e Registro declarado podem ser publicados. Confirme que o conteúdo é publicável; não coloque segredos/dados pessoais em fonte destinada ao painel. O modo padrão permanece status-only. Detalhe não executa comandos, não chama task-start/task-done e não altera estado por clique.
