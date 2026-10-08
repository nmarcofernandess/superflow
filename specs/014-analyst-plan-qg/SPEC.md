# SPEC — Superflow 0.14.0

## Baseline e autorização
Base: ea3f8b91be9791a12ba09f17f95c88f1b7c3ccc4 (0.13.0). Esta entrega prepara uma PR Draft para main. Nenhuma tag, release, instalação ou repositório consumidor será alterado. O desenho foi aprovado; a execução pode continuar sem novo GO por task.

## 1. Autoridades
PRD: promessa. ANALYST: exploração viva, perguntas e razões. SPEC: arquitetura consolidada. PLAN.md: unidades e sequência. Ledger Superpowers: resultados de execução. status.md: orientação e aceite global. QG: projeção. Não criar BUILD.md, progress Superflow ou espelho JSON de tasks.

Capturar ideia cria PRD/status e para. Trabalhar numa nova entrega percorre Analyst → Build → Plan com profundidade proporcional. Executar plano aprovado retoma o registro, sem repetir design. Analyst mantém índice, questões abertas e entendimento integrado; cada resposta relevante persiste os achados e apresenta resumo/pergunta/recomendação quando necessária. Build incorpora decisões materiais, incluindo composição de componentes, estado, interfaces, efeitos e falhas. Fontes de pesquisa não substituem o contrato. HTML exploratório não é anexo normativo sem consolidação.

## 2. Plano e continuidade
`superflow:plan` usa writing-plans dentro da spec. Não converte JSON em Markdown nem duplica brainstorming. PLAN.md contém headings `### Task N: título`, números positivos únicos, ordem textual, arquivos/interfaces, passos, Run/Expected e verificação proporcional. `**Balde:**` e `**Por que agora:**` são metadados editoriais opcionais. `**Depends on:**` pode enumerar números separados por vírgula; dependências devem existir antes do consumidor na ordem textual. Retrofit recebe ID novo sem renumerar concluídas: 1 → 9 → 2 é válido.

A seção `## Execução` do status admite linhas `- Plano: specs/<id>/PLAN.md`, `- Método: inline` ou `sdd`, e `- Registro: <caminho relativo do ledger>`. Ela não repete task status. Com um só plano convencional, a seleção é inequívoca. Se PLAN.md e plan.json coexistirem, exigir declaração explícita; diagnosticar, não escolher por mtime. JSON legado continua com cinco campos e validação existente. Não reinterpretar pacote encerrado como trabalho novo.

O parser ignora headings e eventos dentro de cercas Markdown. Ledger começa por `# SDD ledger — plan: <path>` e deve identificar o plano selecionado. Eventos de `Task N:` registram checkpoint, fix, conclusão e ressalvas; não representam liveness. Uma conclusão precisa do formato terminal nativo com commits e revisão/teste. IDs desconhecidos ou identidade divergente impedem atribuição de conclusão. Checkboxes não constituem prova. Nenhum reader chama scripts de execução.

Antes de cleanup, o executor preserva uma cópia final do ledger e reports indispensáveis em `execution/<run>/`, atualiza Registro e só então remove scratch próprio. Rulings que alteram arquitetura voltam à SPEC; mudança de produto aceita volta ao PRD. Pedido de pausa prevalece sobre execução contínua. Falta de subagent deve ser explícita; inline não é SDD.

## 3. QG opt-in e fontes
Adicionar `qg_details: ["spec-id"]` à configuração existente. Ausente/vazio preserva o read-set status-only. Apenas IDs únicos de specs válidas são selecionados. O detalhe lê PRD.md, ANALYST.md, SPEC.md, plano selecionado e ledger declarado. Uma seção `## Documentos` pode declarar anexos locais com linhas `- Título: specs/<id>/arquivo.md` ou `.html`; não seguir links internos desses documentos.

Todos os caminhos são relativos à raiz do projeto. Recusar absoluto, `..`, backslash, symlink em qualquer segmento e arquivos especiais. Documentos ficam dentro da própria spec; ledger fica em `execution/` dessa spec ou em `.superpowers/sdd/**/progress.md`. Não varrer scratch. Limitar cada fonte a 2 MiB e o detalhe a 32 arquivos. Conteúdo indisponível produz diagnóstico explícito. Incluir bytes, ausência/presença e seleção na identidade da fotografia e na conferência antes da publicação. O modo padrão mantém seu comportamento sem ler fontes adicionais.

Snapshot mantém feed v4 e acrescenta `detail` somente aos registros habilitados. Detalhe inclui documentos, decisões extraídas de seções do Analyst, plano/ordem/baldes, registro identificado, eventos e diagnósticos. Nenhum estado de task altera status global. Expor raiz identificada, revisão e data, distinguindo lane de integração. Nunca expor dados de arquivos não selecionados.

## 4. Interface
Reusar drawer, componente, renderer e tema existentes. Sem detalhe, o drawer continua narrativo. Com detalhe, oferecer Resumo, Decisões, Trabalho, Documentos, Evidências. Documento integral é texto escapado; anexos HTML não rodam no QG. Trabalho mostra ordem, dependência, razão, conclusão registrada e ressalvas; ausência de registro é desconhecida, não 0% ou 100%. Próxima unidade deriva da ordem do plano e resultados válidos, não número N+1. Não alegar agente ativo.

Tabs acessíveis por teclado, estado por texto além da cor, detalhes recolhíveis, sem overflow de página em 390/768/1440 px. Refresh preserva busca, drawer e aba selecionada. Preservar scope, embed/Shadow DOM, HTML portátil, HTTP opcional e última fotografia válida. Campos extras do detalhe não dão autoridade ao navegador.

## 5. Integração técnica
Novo módulo de leitura `superflow_work.py` usa apenas stdlib e é consumido pelo model. Model continua owner de config/status/diagnósticos e publicação. Módulo de apresentação `qg-detail.js` integra o renderer existente; não cria segundo viewer. CLI, empacotamento e runtime carregam os mesmos assets. Check spec reconhece plano nativo/legado sem executar nada. Erro editorial permanece advisory; falhas operacionais continuam protegendo saídas anteriores.

## 6. Prova e compatibilidade
Testes focais para parser, ledger, identidade, retrofit, fontes/paths, privacidade, snapshot e integração CLI. Preservar os testes status-only. Browser verifica cinco tabs, conteúdo host, scopes, refresh e segurança. Fixture não se apresenta como execução SDD. Um ensaio descartável usa helpers nativos disponíveis para duas tasks e um retrofit; registrar precisamente o que foi executado. Se o host não permitir a suíte completa, não inventar verde: PR permanece Draft com o comando e limite.

## 7. Distribuição
Candidata 0.14.0: package/lock, três manifestos, marketplaces, CLI, testes de distribuição, README e changelog coerentes. Sem instalar dependência no consumidor. Documentação pública não contém contexto privado, dados de clientes ou relatos pessoais. Superpowers é requisito do método de planejamento/execução escolhido, não do reader/QG. Manter oito skills; fortalecer assets e contratos existentes.
