# Superflow plugin

Este pacote oferece uma fonte pequena de trabalho vivo: PRD para promessa,
status.md para cadastro factual e PLAN.md Superpowers para novas entregas
ativas. O plan.json segue como formato legado selecionável. O projeto continua dono de suas ferramentas, testes, CI, ship e
evidências.

## Fluxo

O status exige `id`, `title`, `summary` e `status`; `relations` é opcional.
O resumo explica o tema, e o corpo descreve o retrato e o próximo trabalho.
Relações guardam contexto, sem controlar execução; o plano com tasks pendentes
é o único cursor da sequência quando existir.

    ideia estacionada -> PRD/status -> parar
    entrega ativa -> PRD -> Analyst vivo -> Build/SPEC -> PLAN.md
                  -> SDD ou inline autorizado -> review/proof -> aceite
    execução aprovada -> PLAN + ledger -> retomar sem reiniciar design

A entrega ativa segue o lifecycle acima com profundidade proporcional. Uma
correção avulsa delimitada fora desse fluxo pode executar diretamente com
a autorização e verificação adequadas. Uma entrega não vira done só
porque há prosa, arquivo arquivado ou mensagem de sucesso.

## Skills

- superflow escolhe a receita adequada.
- prd escreve a promessa, escopo e aceite verificável.
- analyst mantém ANALYST.md vivo e integra pesquisa, componentes e decisões
  com comunicação ativa ao operador.
- build passa a limpo a arquitetura em SPEC.md, incluindo interfaces, estados,
  componentes e falhas pertinentes.
- plan chama writing-plans para PLAN.md, respeitando o legado plan.json.
- review confronta desenho ou diff com fontes e efeitos reais.
- status mantém o retrato completo, a orientação de continuidade e as relações entre specs sem
  inferir sucesso.

- orquestrar prepara encaminhamentos e acompanha retornos, com painel offline opcional.

## Receitas

| Receita | Use quando | Saída |
|---|---|---|
| [capture](assets/playbooks/capture.md) | uma ideia ou pedido ainda está sendo definido | pacote local e próxima preparação explícita |
| [feature](assets/playbooks/feature.md) | há entrega autorizada | entrega verificada ou bloqueio real |
| [retomar](assets/playbooks/retomar.md) | é preciso continuar trabalho existente | próxima ação baseada em fontes atuais |
| [fechar](assets/playbooks/fechar.md) | a entrega pede aceite | aceite próprio conferido ou trabalho restante explícito |
| [reconciliar](assets/playbooks/reconciliar.md) | cadastro e realidade divergem | fonte e projeção coerentes |

Este README é o índice único das receitas; não há README paralelo na pasta de
playbooks.

## Referências e templates

| Recurso | Consulta |
|---|---|
| [state contract](assets/references/state-contract.md) | Ao editar status.md e relações. |
| [execution contract](assets/references/execution-contract.md) | Plano nativo, ledger, retrofit, retenção e migração. |
| [ANALYST](assets/templates/ANALYST.md) | Lousa de análise persistente. |
| [commands contract](assets/references/commands-contract.md) | Ao usar new, check, feed ou qg. |
| [PRD](assets/templates/PRD.md) | Ao criar ou amadurecer PRD. |
| [status](assets/templates/status.md) | Como exemplo de cadastro manual. New emite status programaticamente. |
| [SPEC](assets/templates/SPEC.md) | Quando arquitetura precisa ficar explícita. |
| [plan legado](assets/templates/plan.json) | Pacotes antigos; novos planos usam writing-plans. |

## Uso da CLI

    python3 -I <plugin>/scripts/superflow.py --root <repo> new <slug> --title <titulo> --summary <resumo>
    python3 -I <plugin>/scripts/superflow.py --root <repo> check status
    python3 -I <plugin>/scripts/superflow.py --root <repo> check spec <spec>
    python3 -I <plugin>/scripts/superflow.py --root <repo> feed --output <feed.json>
    python3 -I <plugin>/scripts/superflow.py --root <repo> qg --output <qg.html>

Python 3.9 ou superior é necessário. A interface, os efeitos e os exit codes
estão em assets/references/commands-contract.md.
Diagnósticos editoriais permanecem visíveis e não controlam CI ou ship do projeto.

## Materiais da spec

A spec reúne registros e materiais autocontidos da entrega. Código, testes,
configuração e outros artefatos permanentes recebem um local canônico no
projeto. Scripts temporários são removidos ao fechar ou promovidos com seus
consumidores. HTMLs e receipts históricos podem permanecer na spec.
Ferramentas de gestão de specs podem ler seus artefatos declarados.
A explicação completa vive no contrato de estado.

## Incorporar a lista de specs

O QG gerado é autocontido: runtime e snapshot incorporados. Abre por duplo clique sem servidor. `qg --online <URL-do-feed> --output painel.html` acrescenta uma fonte HTTP opcional; começa na fotografia incorporada e conserva a última leitura válida se a rede falhar.

`qg --embed --output fragmento.html` produz o componente para qualquer ponto de outro HTML. O host declara `src` opcional, `ids` opcional e `refresh-seconds` opcional. IDs ausentes deixam de aparecer; Shadow DOM isola CSS e IDs. Atualizações preservam busca e drawer, e não recriam o DOM quando `snapshot_id` não muda.

`feed` publica `.superflow/feed.json` e `.superflow/qg.js`. A URL HTTP é escolhida e mapeada pelo host do consumidor; `/superflow/feed.json` é um exemplo, não um caminho obrigatório. Atualizar esse feed permite que os leitores HTTP acompanhem a nova fotografia. A leitura pelo navegador não regrava o HTML e não cria cache persistente.

`qg --refresh painel-a.html painel-b.html` publica o mesmo snapshot nos componentes indicados, preservando o restante dos hosts e seus filtros. Sem caminhos, lê a lista opcional `qg_outputs` da configuração. Em hosts de vários projetos, `--source <URL>` seleciona os componentes pela fonte declarada. Não há descoberta automática de destinos.

**Este painel funciona sem servidor com o retrato incorporado. Para acompanhar atualizações publicadas, configure uma URL HTTP do feed. Para atualizar a fotografia portátil, execute o comando de atualização.**

O contrato de comandos explica HTTP/CORS, publicação e limites. Arquivo local buscando feed HTTP depende de CORS; F5 de uma página servida por HTTP depende de o host continuar disponível.

## Orquestração opcional

A [skill orquestrar](skills/orquestrar/SKILL.md) mantém próximos passos e prompts.
O [contrato de escopos](assets/references/scope-contract.md) define o mapa QG.
Specs, tasks e encaminhamentos preservam identidades e estados próprios.

## Detalhe QG opt-in (0.14.0)

Declare `qg_details` com IDs exatos em `.superflow/config.json` quando for seguro
publicar os documentos e o ledger da spec. O drawer apresenta Resumo, Decisões,
Trabalho, Documentos e Evidências sem manter estado duplicado. O QG padrão não
lê PLAN, Analyst nem reports; ausência de fonte aparece como diagnóstico.
Sem scripts de execução no leitor, sem novo backend ou alterações em consumidores.
