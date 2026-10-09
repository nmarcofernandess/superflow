# Superflow 0.14.0 Implementation Plan

> Use superpowers:executing-plans nesta execução: o host não oferece dispatch de subagents. Uma revisão final separada do autor será identificada como self-review. Não declarar SDD. Não mergear nem publicar release.

**Goal:** Implementar o lifecycle aprovado e QG detalhado opt-in.
**Architecture:** Leitores stdlib de PLAN/ledger alimentam o model e o renderer existentes, com privacidade default status-only.
**Tech Stack:** Python 3.9+, JavaScript, Markdown, Playwright do plugin.
**Spec:** specs/014-analyst-plan-qg/SPEC.md

## Global Constraints
Um plano ativo por entrega. Sequência textual; IDs estáveis. Ledger não dá aceite global. Read-set ampliado só por opt-in. Sem mudanças em consumidores, Superpowers, CI clínico ou instalações. Dúvidas materiais não ficam ocultas; código público não inclui contexto privado. Não usar suíte completa como debugger.

## Review Focus
Escapes por symlink/paths; interpretações de exemplos como tasks concluídas; fonte ausente confundida com vazio; publicação com fontes alteradas; refresh que mistura aba/seleção antiga; compatibilidade da distribuição e do modo padrão.

## Sequência
Leitura → fontes e continuidade → apresentação → lifecycle documental → distribuição/relato. Esta ordem entrega as interfaces consumidas pela unidade seguinte; não há implementação paralela.

### Task 1: Ler plano nativo e ledger sem inventar progresso
**Balde:** Leitura
**Por que agora:** Define o contrato consumido pelo snapshot.
**Files:** Create plugins/superflow/scripts/superflow_work.py; Create plugins/superflow/scripts/test_work.py.
**Interfaces:** Produz parse_plan, parse_ledger e resolução de referências; consome texto Markdown e identidade do plano.
- [ ] Escrever casos de ordem 1/9/2, headings em cercas, dependência inválida, dois planos e ledger de outro plano.
- [ ] Run: python3 -m unittest discover -s plugins/superflow/scripts -p test_work.py. Expected: falhas nas capacidades ausentes.
- [ ] Implementar parsers determinísticos; preservar ressalvas e desconhecidos.
- [ ] Rodar o mesmo comando. Expected: casos passando sem execução de comandos pelo reader.
- [ ] Commitar unidade e registrar resultado.

### Task 2: Integrar fontes opt-in e validação de plano ao model
**Balde:** Fontes
**Por que agora:** O parser já define identidade e ordem.
**Depends on:** 1
**Files:** Modify plugins/superflow/scripts/superflow_model.py; Extend test_work.py; Modify testes de model/commands somente onde o contrato novo exigir.
**Interfaces:** Consome parsers; produz snapshot detail e read-set com identidade de todas as fontes.
- [ ] Escrever regressões para status-only, opt-in, documento ausente, mudança de bytes, symlink, paths fora da spec e PLAN legado.
- [ ] Run: python3 -m unittest discover -s plugins/superflow/scripts -p test_work.py. Expected: falhas específicas de integração.
- [ ] Integrar leitores sem alterar comandos de produto ou autoridade do status.
- [ ] Rodar focais e testes existentes pertinentes. Expected: detalhes corretos e isolamento padrão preservado.
- [ ] Commitar unidade e registrar resultado.

### Task 3: Apresentar cinco abas no drawer existente
**Balde:** Apresentação
**Por que agora:** Consome o snapshot opt-in já verificado.
**Depends on:** 2
**Files:** Create plugins/superflow/assets/qg-detail.js; Modify assets/qg.html, assets/qg-component.js e scripts/superflow_qg.py; Create scripts/test_qg_detail.cjs.
**Interfaces:** Consome record.detail; mantém state/refresh da instância existente.
- [ ] Escrever testes das tabs, task 9 como próxima, ressalvas, documentos escapados e refresh preservando aba.
- [ ] Run: node plugins/superflow/scripts/test_qg_detail.cjs. Expected: falha pelo detalhe ausente.
- [ ] Implementar apresentação usando o tema existente, acessibilidade e limites de largura.
- [ ] Rodar o focal no browser disponível e integrações existentes pertinentes. Expected: modo padrão inalterado e cinco abas úteis.
- [ ] Commitar unidade e registrar evidências sem fingir aceite humano.

### Task 4: Fechar skills, templates, playbooks e migração
**Balde:** Lifecycle
**Por que agora:** Documenta interfaces executáveis, não promessas de reader futuro.
**Depends on:** 3
**Files:** Modify skills/{superflow,prd,analyst,build,plan,status,review,orquestrar}/SKILL.md; assets/templates; assets/playbooks; assets/references; README.md; plugins/superflow/README.md; SPEC-superflow-plugin.md.
**Interfaces:** PLAN/ledger nativos; Execução no status; qg_details opt-in.
- [ ] Conferir o fluxo ideia/entrega/retomada e a cobertura dos 20 checkpoints do desenho.
- [ ] Escrever Analyst vivo e Build autocontido; um único PLAN; retenção de registro antes de cleanup; integração sem review duplicado.
- [ ] Validar links e consistência de exemplos contra parser. Expected: nenhuma instrução concorrente para novas entregas; legado explicitamente preservado.
- [ ] Registrar limites de ensaio comportamental sem inventar uso de agentes.
- [ ] Commitar unidade.

### Task 5: Preparar release candidata e publicar PR Draft
**Balde:** Entrega
**Por que agora:** Runtime, apresentação e documentação representam a mesma capacidade.
**Depends on:** 4
**Files:** package.json, package-lock.json, manifestos e marketplaces, CLI, validate_superflow.py, distribuição, CHANGELOG.md; execution/validacao.md desta spec.
**Interfaces:** Consome entrega estabilizada; produz pacote candidato 0.14.0 e PR para main.
- [ ] Atualizar versão e pacote; preservar dependências existentes.
- [ ] Run: npm test. Expected: validação do plugin verde ou limitação nominal de ambiente registrada, nunca PASS presumido.
- [ ] Revisar diff completo, privacidade, contrato de fontes, cleanup e cobertura.
- [ ] Preservar ledger/resultados e registrar self-review quando não houver revisor independente.
- [ ] Publicar branch e uma PR Draft contra main com evidências e limites. Não mergear, criar tag/release nem atualizar instalação.
