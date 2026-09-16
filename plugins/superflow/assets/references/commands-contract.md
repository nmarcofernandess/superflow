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

`specs/**/status.md` é a fonte editável. `.superflow/config.json` configura `specs_root`; não contém destinos ou hooks. Sem config, o diretório padrão é `specs`. O plugin não instala scripts nem configura CI no consumidor.

`feed` publica `.superflow/feed.json` e `.superflow/qg.js`: dados derivados e componente compartilhado. `feed --output <pasta/feed.json>` muda a saída; `qg.js` acompanha o feed na mesma pasta. `qg` também atualiza esse par na localização padrão e usa o mesmo snapshot para suas saídas offline. Não é preciso rodar feed antes de qg.

O envelope `superflow.feed.v4` contém `records`, `diagnostics`, `generated_at`, `source_revision` e `snapshot_id`. O hash cobre caminhos e bytes dos status e da configuração, inclusive alterações não commitadas. O SHA informa o HEAD, não prova árvore limpa. Remoções e renomeações entram como estão nas fontes; não há inferência de identidade.

Escolha a raiz que representa o conteúdo a publicar. Para um painel compartilhado, prefira a branch integrada e atualizada do projeto; uma lane é adequada para ensaio identificado. O plugin não escolhe branch, faz pull nem exige um nome de branch.

Versionar feed e componente é decisão do consumidor: faz sentido para publicar um site estático ou preservar uma fotografia. Eles são recriáveis e não devem ser editados à mão. Não há atualização automática ao editar status ou abrir o HTML.

## Online: um feed, vários HTMLs

Sirva a pasta do feed por HTTP(S). O componente busca os dados a cada carregamento, sem cache da requisição ou armazenamento local. Após mudar status, rode `feed` uma vez e recarregue os painéis. O mesmo componente funciona em uma tab, section ou qualquer contêiner HTML:

```html
<script data-superflow-runtime defer src="https://exemplo.org/specs/qg.js"></script>
<superflow-qg src="https://exemplo.org/specs/feed.json"></superflow-qg>
<superflow-qg src="https://exemplo.org/specs/feed.json"
              ids='["importacao", "categorias"]'></superflow-qg>
```

Sem `ids`, mostra o corpus inteiro. Com `ids`, mostra apenas os IDs listados, sem adicionar pais, filhos ou relacionados implicitamente. `ids='[]'` mostra zero specs. IDs ausentes simplesmente não aparecem; a seleção não é um contrato de existência. Relações fora do recorte não abrem outro registro. A hierarquia permanece entre os registros incluídos.

O host escolhe posição e dimensões; o componente mantém o layout oficial e isola CSS/IDs com Shadow DOM. Cada instância tem busca e drawer próprios. A URL do host não muda; o standalone usa `sync-hash` para links diretos.

Para gerar uma página ou fragmento online:

```text
superflow.py --root <repo> qg --online https://exemplo.org/specs/feed.json --output <painel.html>
superflow.py --root <repo> qg --online https://exemplo.org/specs/feed.json --embed --output <fragmento.html>
```

Nesses exemplos, `superflow.py` representa o comando Python completo. O HTML carrega `qg.js` da mesma pasta da URL do feed. URLs relativas também funcionam quando resolvem para HTTP(S). A publicação dos arquivos no servidor pertence ao projeto; o comando não faz upload.

Use a mesma origem HTTP para host e feed ou configure CORS no servidor do feed. `file://` não fornece leitura HTTP de um arquivo local; abrir um HTML local com feed HTTP também depende da permissão CORS do servidor. Para distribuir sem servidor, use offline. O componente mostra falha de leitura explicitamente, sem recorrer a uma cópia antiga. Não há servidor, watcher, daemon, hook ou gate instalado pelo plugin.

## Offline: uma fotografia em vários destinos

`qg --output <qg.html>` gera uma página autocontida. `qg --embed --output <fragmento.html>` gera o mesmo componente para inserir num host. Ambos contêm dados e runtime, sem dependência de rede. Não substitua um HTML personalizado usando `--output`: essa opção cria uma página completa ou fragmento novo.

Para congelar ou atualizar componentes de HTMLs existentes, use a marcação acima e indique os destinos:

```text
superflow.py --root <repo> qg --refresh <painel-a.html> <painel-b.html> --source https://exemplo.org/specs/feed.json
```

`--source` seleciona por igualdade exata do atributo `src`, não baixa essa URL. Os dados vêm da raiz `--root`. Componentes que apontam para outra fonte permanecem intactos. Sem `--source`, atualiza componentes sem `src`, como os gerados pelo modo offline padrão.

O comando lê um snapshot, atualiza feed/componente e incorpora a mesma fotografia nos destinos indicados. Mantém `src` e `ids`, adiciona `offline` e substitui somente o conteúdo dos elementos `<superflow-qg>` selecionados e o `<script data-superflow-runtime>`. O restante do host é preservado. Não há adaptador específico por painel nem registro persistente de destinos. Para voltar ao online, retire `offline`; a instância volta a consultar `src`.

Uma exportação offline continua antiga até outra exportação, por definição. Para dezenas de painéis vivos, prefira online. `--refresh` serve para fotografias e distribuição portátil.

As gravações são atômicas por arquivo, com conferência de fontes antes de publicar; não existe transação entre arquivos. Falha no meio de um lote pode deixar destinos de gerações diferentes: corrija a falha e repita o comando. O `snapshot_id` permite conferir a coerência; a data aparece na descrição do identificador no QG. Atualizar a release e publicar novamente feed/componente renova o código compartilhado; exports offline recebem o código novo na próxima exportação.
