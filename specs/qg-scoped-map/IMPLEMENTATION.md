# Mapa QG escopado — plano candidato de implementação

> Executor: usar superpowers:executing-plans ou subagent-driven-development, por task. Este plano ainda não foi executado. Publicar implementação em PR; não mergear por conta própria.

**Goal:** acrescentar mapa opcional de um recorte, preservando estado canônico, lista padrão e portabilidade.
**Architecture:** scope editorial separado + feed factual; um único componente QG e seu drawer; dependências editoriais distintas de relações.
**Stack:** Python >=3.9, HTML/CSS/JS nativos, unittest e Playwright já usados pelo projeto. Nenhuma dependência de produto nova.
**Spec:** [SPEC.md](SPEC.md). **Cursor:** [plan.json](plan.json), P01–P06.

## Restrições globais

Não alterar status.md nem feed.v4; não ler plan.json para calcular mapa; não criar engine de execução. Sem scope, comportamento atual intacto. Exemplos públicos só com dados fictícios. Nunca inferir dependências da prosa de relations. A ordem mostrada não significa autorizado/pronto. Toda função nova descrita abaixo é proposta, não símbolo já exportado.

## Foco de revisão e donos dos testes

1. Mesmo feed com scope diferente não pode conservar o mapa antigo — P04.
2. ID ausente ou duplicado não pode sumir nem aparecer done — P01/P04.
3. Ciclo contextual é válido; ciclo after não pode produzir falsa sequência parcial — P01/P03.
4. Refresh seletivo não pode ler scope de outro projeto ou sobrescrever sua fonte — P02/P05.
5. Labels com HTML/IDs especiais, teclado e nós isolados continuam seguros/acessíveis — P03/P05.

## Arquivos e responsabilidades

- Novo plugins/superflow/scripts/superflow_scope.py: parser, read-set e projeção puros.
- Novo plugins/superflow/scripts/test_scope.py: testes do contrato/projeção.
- Existentes scripts/superflow.py e scripts/superflow_qg.py, sob plugins/superflow: CLI, publicação e Slots/refresh.
- Existentes assets/qg.html e assets/qg-component.js, sob plugins/superflow: mapa como visão opcional no renderer único; não copiar o protótipo como runtime paralelo.
- Existentes test_commands.py, test_qg.py, test_qg_browser.cjs e test_qg_portable.cjs, sob plugins/superflow/scripts: regressões e integração.
- Raiz scripts/validate-all.sh e package.json: registrar teste novo e incluir módulo no pacote; docs/manifests somente em P06.

## P01 — fonte editorial e projeção determinística

**Consome:** superflow_model.parse_json, ContentError, SourceError; feed.v4 atual.
**Produz em superflow_scope.py:**

```python
parse_scope(text: str) -> dict
read_scope(root: Path, relative_path: str) -> tuple[dict, dict[str, bytes]]
ensure_scopes_unchanged(root: Path, scope_sources: dict[str, bytes]) -> None
project_scope(feed: dict, scope: dict) -> dict
```

Read-set contém paths relativos reais e bytes lidos. Fingerprint usa SHA-256 desses bytes e path; não reescrever a fonte. project_scope devolve members resolvidos/diagnósticos, edges normalizadas com origem, levels, isolated, outside e diagnostics. Membro ausente tem record=None, nunca status inventado. levels=None quando ciclo after ou endpoint sem registro único impedir ordem.

- [ ] Criar test_scope.py com RED de parser ausente. Casos nominais e inválidos correspondem exatamente a SPEC §2; testar duplicação de chave JSON antes de json.loads comum perder a evidência.
- [ ] Fixar os exemplos causais abaixo no teste; depois implementar Kahn + rank máximo e dedupe de context sem apagar os motivos.

```python
# Com membros a,b,c,d,e e apenas after a->c,b->c,c->d:
assert levels == [["a", "b"], ["c"], ["d"]]
assert isolated == ["e"]
# Adicionar context d->a NÃO muda levels.
# Adicionar after d->a: levels=None + ORDER_CYCLE, não prefixo parcial.
# Remover b do feed: b continua membro, record=None,
# levels=None + UNRESOLVED_PRECEDENCE; não é tratado como done.
# Duas rows do feed com id=b: AMBIGUOUS_MEMBER, não first/last wins.
```

- [ ] Testar grupo desconhecido, self-edge, endpoint fora de members, mesma aresta duplicada, membros repetidos e field status no scope: recusa estrutural. Context/evidence em ciclo são aceitos.
- [ ] Rodar `python3 -I plugins/superflow/scripts/test_scope.py`; GREEN requer todos os asserts, não snapshot visual. Registrar contagem real no receipt.

## P02 — opt-in na CLI e refresh sem destruir composição

**Consome:** P01 e snapshot atual de build_snapshot(root).
**Produz:** `qg --scope PATH`; bloco data-superflow-scope; atributo scope-path; read-set separado por arquivo selecionado.
**Modifica:** build_parser/main/atomic_write em superflow.py; snapshot_element/render_embed/render/Slots/refresh_html em superflow_qg.py; test_commands.py/test_qg.py. Preservar assinatura atual por parâmetros opcionais: `render_embed(feed, source=None, sync_hash=False, scope=None, scope_path=None)`; `render(feed, root=None, source=None, scope=None, scope_path=None)`; `refresh_html(text, feed, source=None, scopes=None)`, onde scopes é mapping de scope-path para composição validada. Ausência de scopes num host sem scope mantém caminho anterior; host escopado sem resolução falha explicitamente.

- [ ] RED: gerar HTML com --scope atualmente deve falhar por opção desconhecida. Criar testes que exigem os dois blocos JSON e source/ids válidos; scope+ids deve falhar na resolução do componente.
- [ ] Ler só o arquivo explicitamente selecionado. Rejeitar absoluto, ../, symlink e resolução fora da raiz. Proteger fontes de scope na validação antecipada de outputs e em cada atomic_write; chamar ensure_unchanged existente e ensure_scopes_unchanged separadamente.
- [ ] RED causal de refresh: dois componentes de fontes distintas, só A selecionado; o scope de B é inexistente. Refresh de A passa e preserva B byte a byte; refresh geral falha antes de escrever por B ausente.
- [ ] Testar alteração dos bytes de scope entre leitura e replace: exit 2, saída anterior preservada. Testar output igual à fonte e scopes com caminhos iguais aos outputs feed/runtime/HTML. Não apenas comparar o nome do arquivo.
- [ ] `--scope` com `--refresh` recusa; refresh resolve scope-path de cada componente selecionado. Feed e check status não abrem nenhum scope. Dados malformed na fonte recusam publicação; diagnósticos semânticos de projeção permitem mapa de diagnóstico, nunca ordem falsa.
- [ ] GREEN: `python3 -I plugins/superflow/scripts/test_commands.py` e `python3 -I plugins/superflow/scripts/test_qg.py`.

## P03 — mapa conjunto/foco, sequência e detached

**Consome:** shape validado de scope + feed. **Produz:** visão escopada no template qg.html usando o drawer/narrativa existentes. Nenhum gráfico para o QG padrão.

- [ ] Primeiro escrever asserts browser para: inicialmente todas as arestas; selecionar a destaca só incidentes; selecionar a novamente restaura; Mostrar tudo e Escape restauram; Escape do drawer fecha o drawer primeiro.
- [ ] Implementar SVG nativo + cartões HTML acessíveis, sem lib de grafos. Definir viewport do SVG pela área dos cards; ResizeObserver único; layout não depende de pixels fixos. Determinismo na ordem de members/groups.
- [ ] Sequência usa after, não group/status/context/evidence. Rank de empate significa sem precedência, não recursos disponíveis. Membro sem after incidente aparece separado. Ciclo/ausente mostra diagnóstico e oculta etapas.
- [ ] Membro válido isolado continua clicável; referência fora do recorte aparece no detalhe sem expandir; fonte ausente conserva placeholder identificado. Motivos em textContent/escape; nunca innerHTML de reason.
- [ ] GREEN: `node plugins/superflow/scripts/test_qg_browser.cjs`. Cobrir 390 e 1440 px, teclado, lista textual equivalente, host CSS adversarial e dois componentes independentes. Capturas são evidência complementar, não oráculo de cores/fontes.

## P04 — identidade de render e atualização viva

**Consome:** P01–P03. **Modifica:** validate/accept/load e observedAttributes de qg-component.js; contrato de display em qg.html.
**Produz:** identidade de render `(feed.snapshot_id, scope fingerprint, view/selection)`; composição vem do bloco/geração, nunca fetch de scope-path.

- [ ] RED: mesmo snapshot_id, scope A seleciona a/b e scope B a/c: DOM precisa atualizar. Com feed e scope iguais, manter DOM/foco.
- [ ] Após feed novo, preservar seleção por spec_id; membro removido continua no scope como diagnóstico sem conteúdo velho apresentado como atual. Duplicação de ID também não escolhe row arbitrária.
- [ ] Falha HTTP mantém o último feed válido e explicita stale; não retorna ao snapshot antigo. Sem src, nenhum request. Atualização de scope ocorre por regeneração/refresh ou alteração explícita do bloco no host, não por polling adicional.
- [ ] Repetir ciclo de desconexão/reconexão do componente: cancelar fetch/timer/observer antigo; nenhum listener duplicado. A lista sem scope passa todos os testes anteriores.
- [ ] GREEN: `node plugins/superflow/scripts/test_qg_browser.cjs` e `node plugins/superflow/scripts/test_qg_portable.cjs`.

## P05 — prova terminal da composição e publicação

**Consome:** P01–P04. **Modifica:** testes existentes; novo test_scope.py entra no loop obrigatório de scripts/validate-all.sh. Evitar segundo harness.

- [ ] Testar ciclo completo em corpus temporário: status + scope -> CLI -> HTML -> browser -> status alterado -> feed HTTP -> refresh offline. Usar a/b/c sintéticos e os mesmos fixtures para conferir IDs, labels, estados e ordem independentemente.
- [ ] Fixar texto malicioso `</script><img src=x onerror=...>` em title/reason e IDs especiais: nada executa nem consulta rede. Revalidar dois blocos e safe serialization.
- [ ] Provar arquivo local, HTTP com/sem CORS, host indisponível, scope ausente, fonte alterada, lote parcial por erro de IO, atualização seletiva e host externo preservado. Não prometer transação entre saídas.
- [ ] `npm ci` e `npm run test:setup` são preparação somente se ausentes; depois `npm test`. Não instalar browser a cada execução. Receipt: HEAD/base, comandos, exit, contagens, erros browser, fixtures e capturas. Nenhum resultado desta etapa é alegado na entrega da spec.

## P06 — contrato público e disponibilidade por PR

**Modifica:** README.md, SPEC-superflow-plugin.md, plugins/superflow/README.md, assets/references/state-contract.md e commands-contract.md; package.json e test_distribution.py para incluir o novo módulo; manifests/versionamento apenas conforme release efetivamente preparada.

- [ ] Alterar explicitamente a proibição histórica de graph: exceção opt-in para projeção escopada, não board/scheduler. Preservar o default e explicar onde o estado e a ordem moram.
- [ ] Exemplo de consumo, comando real, schema, diagnóstico e refresh documentados no pacote. Ajustar validações do pacote que enumerem arquivos/exportação; não remover asserts para obter verde.
- [ ] Rodar `npm test` após a mudança documental/distribuição. Conferir pacote publicado inclui módulo/asset necessário, não o corpus privado nem todo o material da spec.
- [ ] Abrir PR contra main com diffs, evidências e limites. Não mergear, criar tag, lançar release ou marcar esta spec done antes do aceite correspondente.

## Condição de conclusão

R01–R07 com testes e receipt; lista antiga preservada; scope não duplica status/cursor; atualização segura; exemplo adicional criado apenas por dados demonstra reuso. O protótipo desta spec prova a direção visual, não substitui nenhuma dessas integrações.
