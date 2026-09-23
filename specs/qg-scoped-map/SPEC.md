# SPEC candidata — QG scoped map

## 1. Compatibilidade e fontes atuais

Base lida: b99f78eee3251e3ac2ed4feffe04632a17ad0eb1. Não mudar status.md, relations ou superflow.feed.v4. O modo padrão continua lista; não escanear scopes automaticamente. Composição é dado editorial do consumidor, não um novo workflow de execução do plugin.

Fontes verificadas: README.md §§ Estado/Comandos/Incorporar; SPEC-superflow-plugin.md §§ Estado/Runtime/Projeção; plugins/superflow/assets/references/commands-contract.md §§ Fonte/Componente/Refresh; scripts/superflow.py (build_parser, main, atomic_write); scripts/superflow_qg.py (render_embed, Slots, refresh_html); assets/qg-component.js (validate, accept, load). Todos os paths de scripts/assets nesta seção são relativos a plugins/superflow, exceto README/SPEC da raiz. O runner real é scripts/validate-all.sh na raiz.

## 2. Scope v1 proposto

Arquivo do consumidor: .superflow/scopes/<slug>.json. Exemplo pequeno:

```json
{
  "schema_version": "superflow.scope.v1",
  "id": "entrega-coerente",
  "title": "Uma entrega, várias frentes",
  "goal": "Entregar uma experiência consistente sem duplicar estado.",
  "groups": [{"id":"core","title":"Capacidades"}],
  "members": [
    {"spec_id":"writer","group":"core","focus":"Confirmação da gravação"},
    {"spec_id":"editor","group":"core","focus":"Sessão que consome o contrato"}
  ],
  "edges": [
    {"from":"writer","to":"editor","kind":"after","reason":"A integração do editor consome o contrato de confirmação."}
  ]
}
```

Obrigatórios: schema_version, id, title, goal, members. Opcionais: groups, edges, que assumem []. Campos desconhecidos, chaves JSON duplicadas, strings vazias e listas com tipos errados são inválidos. Members contêm exatamente spec_id e opcionalmente group/focus. IDs são strings opacas não vazias; não reescrever IDs em slugs. Scope id é identificador editorial, não cadastro de spec.

Groups têm exatamente id/title; IDs únicos. Membro sem grupo vai para Outros. Grupo desconhecido ou membro duplicado é erro. Edges têm exatamente from/to/kind/reason; kind é after, context ou evidence. Endpoints precisam ser membros; self-edge e duplicação do mesmo trio são erros. Reason explica a condição; nenhuma expressão é executável. O estado da spec nunca é duplicado no scope.

Para representar só parte de uma spec, focus nomeia o recorte. O cartão informa “estado da spec inteira”; a seta não espera automaticamente que a spec-mãe inteira vire done. Execução e suas autorizações continuam no plano receptor. V1 não resolve task IDs nem calcula prontidão.

## 3. Relações e ordem são eixos separados

O mapa reúne arestas explícitas e relations dos status cujos dois endpoints estão selecionados. Relação vinda de status é sempre context, com origem visível; relação inversa redundante pode ser desenhada uma vez, preservando os motivos. Não converter reason em dependência. Contextual declarada no scope para o mesmo par evita duplicação visual, mas preserva a indicação de ambas as fontes no detalhe.

After significa precedência editorial entre as contribuições descritas neste recorte. Evidence significa entrega de evidência sem implicar precedência obrigatória. Quando evidência realmente exigir ordem, declarar after separadamente. Só after participa do DAG.

Sequência: Kahn + maior nível predecessor, O(V+E), desempate pela ordem de members. Nível zero reúne membros com caminho de execução e sem predecessores; nível n = 1 + max(níveis anteriores). Membros sem nenhuma after incidente ficam em Sem precedência declarada, não numa falsa etapa obrigatória. Context/evidence não alteram níveis. Ciclo after invalida a sequência inteira e mostra membros envolvidos; não renderizar um prefixo parcial como plano completo.

Rótulo obrigatório: “Na mesma etapa: sem precedência declarada. Recursos, conflitos de edição e autorização não avaliados.” Nenhum botão executar/autorizar/concluir. Estados pending/done não removem automaticamente condições nem reordenam o DAG.

## 4. Detached, fora do recorte e ausentes

- **Isolado válido:** membro presente no feed e sem conexão no mapa. Continua visível e consultável; não é erro nem backlog inferido.
- **Fora do recorte:** relation de status aponta para ID não selecionado. Mostrar contagem e motivo no detalhe, sem puxar destinos/pais/filhos implicitamente. Para declarar precedência com ele, incluí-lo explicitamente em members.
- **Sem cadastro nesta fotografia:** membro selecionado sem registro único no feed, inclusive duplicação de IDs. Mostrar cartão diagnóstico, sem inventar título factual ou status done/pending. Não afirmar exclusão do produto. Se qualquer endpoint after não tiver cadastro único, não sugerir sequência; explicar a falta.

Uma atualização HTTP pode remover um membro. Preservar sua presença editorial e trocar sua representação por diagnóstico; não fingir que o sprint encolheu nem conservar o conteúdo antigo como atual. O último feed válido continua sujeito às regras oficiais de rede.

## 5. UX e composição

Mapa de um recorte explicitamente escolhido, não do corpus inteiro. Abre sem seleção, com todas as arestas visíveis. Selecionar destaca vizinhança; clicar no mesmo nó, Mostrar tudo, Escape no mapa ou área vazia do canvas retorna ao conjunto. Escape de um dialog fecha primeiro o dialog. Seleção é apenas estado volátil de UI.

Setas orientadas para after/evidence, linhas tracejadas para contexto, legenda textual e relações navegáveis em lista. Não depender só de cor. Celular usa leitura sequencial/lista equivalente. Sequência ignora grupos visuais e mostra níveis reais do DAG; grupos do mapa não se apresentam como sequência.

Reusar a linguagem do asset: cabeçalho, cartões, detalhe lateral e espaço entre as frentes. Na implementação, usar o Shadow DOM e o drawer/narrativa do QG existente; não manter um segundo renderer de status nem copiar a miniaplicação do protótipo inteira para o plugin.

Sem scope, não há graph nem mudança no comportamento de ids, inclusive ids=[] e IDs removidos. Com scope, members define o recorte exato: ids e scope simultâneos são erro explícito, não uma interseção que esconda pré-requisitos.

## 6. CLI e fronteira de refresh propostas, ainda inexistentes

Novo argumento opt-in: qg --scope .superflow/scopes/<slug>.json --output painel.html; compatível com --embed e --online. --scope junto de --refresh é rejeitado: cada instância recebe sua própria composição persistida no host. Feed/check status sem scope continuam lendo somente os status/config atuais; nenhum scan extra de arquivos ou planos.

O gerador incorpora no elemento oficial um segundo bloco application/json, data-superflow-scope, e atributo scope-path relativo à raiz do consumidor para reabrir a fonte no refresh. O bloco contém a composição normalizada e scope_id de fingerprint; data-superflow-snapshot continua sendo o feed oficial. O browser NÃO busca scope-path, arquivo local ou URL extra.

refresh_html hoje substitui todo o interior do componente. A implementação deve preservar/recarregar a composição de cada instância selecionada, antes de formar os outputs. Resolver paths contra --root, bloquear symlinks e escapes, proteger todos os arquivos de scope contra sobrescrita e checar seus bytes novamente antes de cada atomic_write. Não injetar scopes em read_sources e quebrar a igualdade de ensure_unchanged para comandos padrão: manter um read-set separado e função de conferência conjunta.

Arquivo de scope ausente, estruturalmente inválido ou alterado durante geração: erro operacional exit 2 e outputs anteriores preservados antes do primeiro replace. Preparar/validar todos os componentes selecionados antes de publicar. Mantém-se a atomicidade por arquivo e a possibilidade de falha de IO no meio do lote já documentada; não prometer transação global.

--source continua selecionando por src exato e não baixa URL. Scopes de componentes não selecionados não são lidos nem alterados. Não mudar qg_outputs ou descobrir destinos automaticamente. Componentes não escopados continuam com o caminho existente.

Ciclos after e registros ausentes/ambíguos são diagnósticos semânticos da projeção: o HTML pode ser publicado para inspeção, mas sem sequência válida. Não são confundidos com um arquivo de scope estruturalmente inválido.

## 7. Runtime, segurança e diagnóstico

Chave de renderização escopada = snapshot_id + fingerprint do scope + seleção/visão; mesmo feed com composição diferente precisa atualizar o mapa. Preservar busca, seleção e drawer por ID quando aplicável; feed/escopo removido limpa seleção e explica a mudança. Sem localStorage, daemon, editor visual persistente ou novos pacotes de layout.

Usar script_safe_dumps em ambos os blocos. Labels/razões/IDs são texto, nunca HTML executável ou selectors interpolados sem escape. Validar novamente o envelope do scope no cliente. Erro de composição mostra diagnóstico, não quebra a lista oficial nem ativa sequenciamento. Status inválido/ausente e ciclo after impedem ordem confiável, não leituras já autorizadas.

Exemplos públicos são sintéticos. Nenhum path/link de repositório privado, token, e-mail ou corpo real de handbook pode ser publicado pelo asset.

## 8. Entregáveis e não objetivos

A implementação futura altera runtime Python, componente/template QG, testes e documentação pública em PR. Esta entrega altera apenas specs/ e exemplos. Não eleva a versão 0.12.3, não modifica feed.v4, não instala plugin, não cria sprint como nova entidade de status e não altera projetos consumidores.

Adiado deliberadamente: source multi-repo, task refs, cronograma, capacity planning, escrita visual de manifests, agrupamento automático do corpus inteiro. Manter como requisitos futuros, não precondições do mapa v1.
