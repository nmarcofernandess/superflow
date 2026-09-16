# Contrato de comandos

```text
python3 -I <plugin>/scripts/superflow.py --root <repo> new <slug> --title <titulo> --summary <resumo>
python3 -I <plugin>/scripts/superflow.py --root <repo> check status
python3 -I <plugin>/scripts/superflow.py --root <repo> check spec <spec>
python3 -I <plugin>/scripts/superflow.py --root <repo> feed
python3 -I <plugin>/scripts/superflow.py --root <repo> qg --output <qg.html>
```

`new` exige um resumo humano e cria apenas PRD e status. Um diagnóstico em outra spec não impede a criação; o comando ainda recusa entrada inválida, ID conhecido ou destino físico já ocupado. `check status`, feed e QG leem somente status. `check spec` confere PRD e status obrigatórios e SPEC/plano quando presentes na spec-alvo. A integridade dos destinos de `relations` é conferida pelos status da coleção. Inspecionar os arquivos não decide prontidão, autorização nem necessidade de artefatos condicionais.

Os comandos nunca executam proof, teste, CI ou ship. `check`, feed e QG relatam conteúdo incompleto ou inválido como `warning` e terminam com exit 0; esses diagnósticos não afirmam validade nem bloqueiam a operação do projeto. Exit 1 indica que `new` recusou a entrada ou uma colisão antes de escrever. Exit 2 indica falha operacional. Status inválido pode ficar fora dos registros; seu diagnóstico permanece na projeção.

## Fonte e publicação

`specs/**/status.md` é a fonte editável. `.superflow/config.json` configura a raiz e pode listar destinos HTML:

```json
{
  "specs_root": "specs",
  "qg_outputs": ["painel.html", "docs/entregas.html", "/caminho/absoluto/painel.html"]
}
```

Sem config, a raiz padrão é `specs`. Caminhos de destinos relativos são resolvidos a partir da raiz do projeto, não do diretório do terminal; caminhos absolutos também são permitidos. O plugin não instala scripts, hooks, CI ou servidor no consumidor.

`feed` publica `.superflow/feed.json` e `.superflow/qg.js`: consolidado derivado e componente. `feed --output <pasta/feed.json>` muda a saída; `qg.js` acompanha o feed na mesma pasta. `qg` também atualiza esse par na localização padrão e usa o mesmo snapshot para suas saídas. Não é preciso rodar feed antes de qg.

O envelope `superflow.feed.v4` contém `records`, `diagnostics`, `generated_at`, `source_revision` e `snapshot_id`. O hash cobre caminhos e bytes dos status e da configuração, inclusive alterações não commitadas. O SHA informa o HEAD, não prova árvore limpa. Remoções e renomeações entram como estão nas fontes; não há inferência de identidade.

Escolha a raiz que representa o conteúdo a publicar. Para um painel compartilhado, prefira a branch integrada e atualizada do projeto; uma lane é adequada para ensaio identificado. O plugin não escolhe branch, faz pull nem exige um nome de branch.

Versionar feed, componente e HTMLs é decisão do consumidor: faz sentido para publicar um site estático ou preservar uma fotografia. São recriáveis e não devem ser editados à mão. Não há observação automática dos status: o script precisa publicar o feed.

## Painel portátil com atualização opcional

**Este painel funciona sem servidor com o retrato incorporado. Para acompanhar atualizações publicadas, configure uma URL HTTP do feed. Para atualizar a fotografia portátil, execute o comando de atualização.**

`qg --output <qg.html>` gera uma página autocontida. `qg --embed --output <fragmento.html>` gera o mesmo componente para inserir num host. Todos os HTMLs gerados incorporam snapshot e runtime, inclusive quando têm uma fonte HTTP opcional:

```text
superflow.py --root <repo> qg --online https://exemplo.org/specs/feed.json --output <painel.html>
superflow.py --root <repo> qg --online https://exemplo.org/specs/feed.json --embed --output <fragmento.html>
```

Nesses exemplos, `superflow.py` representa o comando Python completo. A publicação no servidor pertence ao projeto; o comando não faz upload. A URL de `--online` será o `src` do componente, mas não é consultada durante a geração: a fotografia incorporada vem de `--root`.

O componente começa exibindo a fotografia incorporada. Se `src` estiver configurado, tenta uma leitura HTTP(S). Sucesso apresenta o feed novo; falha preserva o último retrato válido exibido, que pode ser mais recente que o incorporado. Modo, data de geração e falha ficam explícitos no rodapé. Não há retorno ao retrato incorporado após uma leitura HTTP válida na mesma instância.

A leitura HTTP não grava o HTML nem cria cache persistente. A próxima abertura começa novamente na fotografia incorporada. Se a página foi aberta por HTTP e o host sair do ar, F5 pode impedir a própria página de carregar: fallback protege uma página já carregada ou um arquivo local portátil, não um servidor indisponível.

Para abrir um HTML por duplo clique e buscar um feed HTTP, o servidor precisa permitir CORS para essa origem. Sem CORS, o navegador bloqueia a atualização e a fotografia permanece disponível. Arquivos JSON `file://` não são fontes online suportadas. Use um servidor configurado adequadamente, sem desativar a segurança do navegador. Não há servidor automático no plugin.

## Componente e escopo no HTML

Insira o fragmento gerado em uma tab, section ou contêiner do host. Ele contém os seguintes pontos padronizados, preenchidos pelo gerador:

```html
<superflow-qg src="https://exemplo.org/specs/feed.json"
              ids='["importacao", "categorias"]'
              refresh-seconds="60">
  <script type="application/json" data-superflow-snapshot>…snapshot gerado…</script>
</superflow-qg>
<script data-superflow-runtime>…runtime incorporado pelo gerador…</script>
```

Omita `src` para usar somente a fotografia. Omita `ids` para o corpus inteiro; `ids='[]'` mostra zero specs. A lista seleciona IDs exatos, sem adicionar pais, filhos ou relacionados implicitamente. IDs ausentes simplesmente não aparecem. Relações fora do recorte não abrem outro registro. A hierarquia permanece entre os registros incluídos.

`refresh-seconds` é opcional. Sem ele, há uma tentativa HTTP ao carregar. Um valor positivo agenda novas tentativas após cada consulta, com intervalo mínimo de cinco segundos; sessenta segundos é um ponto de partida. Consultas não se sobrepõem. Isso acompanha o feed publicado, não observa os status em tempo real. Snapshot igual não recria o DOM; snapshot novo preserva busca, visão e drawer da spec se ela continuar presente. `offline`, quando explicitamente presente, desativa as consultas HTTP.

O host escolhe posição e dimensões; o componente mantém o layout oficial e isola CSS/IDs com Shadow DOM. Cada instância tem busca e drawer próprios. A URL do host não muda; o standalone usa `sync-hash` para links diretos.

`qg.js` também está disponível para hosts que deliberadamente preferem runtime externo. Isso cria uma dependência para carregar a página e não oferece a mesma portabilidade do HTML gerado com runtime incorporado.

## Atualizar as fotografias portáteis

```text
superflow.py --root <repo> qg --refresh
superflow.py --root <repo> qg --refresh <painel-a.html> <painel-b.html>
```

Sem caminhos, usa `qg_outputs`. Caminhos explícitos substituem a lista configurada naquela execução. O comando lê um snapshot, publica feed/componente e atualiza os elementos `<superflow-qg>` e o `<script data-superflow-runtime>` dos destinos. Preserva `src`, `ids`, intervalo e o conteúdo do host fora desses pontos. Não descobre HTMLs nem exige um adaptador por painel. Os destinos precisam ter recebido o fragmento ou a marcação do componente uma vez; `--output` cria uma nova página ou fragmento e não preserva um host personalizado.

Por padrão, todos os componentes dos destinos recebem a fotografia de `--root`: a lista de publicação deve pertencer ao projeto. Em um host com componentes de projetos diferentes, use `--source <URL>` para selecionar por igualdade exata do atributo `src`. Essa opção não baixa a URL; os dados vêm de `--root`. Componentes de outras fontes permanecem intactos. A seleção de specs continua exclusivamente no HTML.

Destinos HTML ausentes são listados no stderr como `warning: <path>: OUTPUT_NOT_FOUND`, sem impedir a publicação dos demais. O comando não recria esses HTMLs nem altera a configuração. Ao concluir, informa quantos HTMLs atualizou e quantos destinos não encontrou; se todos estiverem ausentes, publica feed/runtime e informa zero HTMLs atualizados, com exit 0. A IA relata os caminhos para o operador decidir se corrige ou remove as entradas. Erros de leitura, permissão, estrutura ou escrita continuam sendo falhas operacionais (exit 2).

As gravações são atômicas por arquivo, com conferência de fontes antes de publicar; não existe transação entre arquivos. Falha no meio de um lote pode deixar destinos de gerações diferentes: corrija a falha e repita o comando. O `snapshot_id` permite conferir a coerência. Atualizar o plugin e publicar as fotografias novamente incorpora também o runtime novo.
